#!/usr/bin/env python3
"""Locked local snapshots and verified checkpoints. No remote uploads."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import uuid
from contextlib import closing
from datetime import datetime, timezone


def command(args, cwd, env=None, binary=False):
    return subprocess.run(args,cwd=cwd,env=env,check=True,capture_output=True,text=not binary,timeout=120).stdout


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def safe_path(root, name):
    rel=PurePosixPath(name)
    if not name or rel.is_absolute() or '..' in rel.parts or '\\' in name:
        raise ValueError('invalid relative checkpoint path')
    path=root/str(rel)
    if not path.resolve().is_relative_to(root.resolve()):raise ValueError('path escapes backup/workspace')
    current=path
    while current != root:
        if current.is_symlink():raise ValueError('symlink checkpoint paths are not supported')
        current=current.parent
    return path


def copy_state(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    with src.open('rb') as stream:is_sqlite=stream.read(16)==b'SQLite format 3\x00'
    if is_sqlite:
        with closing(sqlite3.connect(src.resolve().as_uri()+'?mode=ro',uri=True,timeout=10)) as source:
            with closing(sqlite3.connect(dst)) as target:source.backup(target)
    else:shutil.copyfile(src,dst)
    dst.chmod(0o600)
    return 'sqlite-backup' if is_sqlite else 'file'


def verify(folder):
    manifest=folder/'manifest.json'
    if manifest.is_symlink():raise ValueError('manifest must not be a symlink')
    data=json.loads(manifest.read_text())
    if not isinstance(data,dict) or data.get('schema')!=1 or not isinstance(data.get('files'),list) or not data['files']:
        raise ValueError('invalid or empty checkpoint manifest')
    seen=set()
    for entry in data['files']:
        if not isinstance(entry,dict) or not isinstance(entry.get('path'),str) or not re.fullmatch('[a-f0-9]{64}',str(entry.get('sha256',''))):
            raise ValueError('invalid file record')
        if entry['path'] in seen:raise ValueError('duplicate file record')
        seen.add(entry['path']);path=safe_path(folder,entry['path'])
        if not path.is_file() or digest(path)!=entry['sha256']:raise ValueError('checkpoint file missing or checksum mismatch: '+entry['path'])
    if sorted(data.get('required_files',[]))!=sorted(seen):raise ValueError('required file set differs from manifest')
    return data


def create(ws, checkpoints, files, reason, prefix='checkpoint'):
    if not files:raise ValueError('at least one required file must be configured')
    for rel in files:
        if not safe_path(ws,rel).is_file():raise ValueError('required file missing: '+rel)
    ident=prefix+'-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]
    stage=checkpoints/('.'+ident);stage.mkdir(mode=0o700)
    try:
        entries=[]
        for rel in files:
            dst=safe_path(stage,rel);kind=copy_state(safe_path(ws,rel),dst)
            entries.append({'path':rel,'sha256':digest(dst),'kind':kind})
        manifest={'schema':1,'checkpoint_id':ident,'timestamp':datetime.now(timezone.utc).isoformat(),
                  'reason':reason,'required_files':files,'files':entries}
        (stage/'manifest.json').write_text(json.dumps(manifest,indent=2))
        verify(stage)
        final=checkpoints/ident;stage.rename(final)
        if prefix=='checkpoint':
            temp=checkpoints/('.latest-'+uuid.uuid4().hex);temp.symlink_to(ident);os.replace(temp,checkpoints/'latest')
        return final
    except Exception:
        shutil.rmtree(stage,ignore_errors=True);raise


def resolve_checkpoint(checkpoints, ident):
    if ident=='latest':
        link=checkpoints/'latest'
        if not link.is_symlink():raise ValueError('latest checkpoint missing')
        ident=os.readlink(link)
    if not re.fullmatch(r'(checkpoint|pre-restore)-[A-Za-z0-9-]+',ident):raise ValueError('invalid checkpoint ID')
    folder=checkpoints/ident
    if folder.is_symlink() or not folder.is_dir():raise ValueError('checkpoint missing or unsafe')
    return folder


SECRET=re.compile(rb'(?:api[_-]?key|secret|password|passwd|access[_-]?token)\s*[=:]\s*[\x22\x27]?([^\s\x22\x27,;]{8,})|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,})',re.I)


def snapshot(ws):
    git=lambda *a,**kw:command(['git',*a],ws,**kw)
    git('rev-parse','--git-dir')
    if not git('status','--porcelain'):return {'status':'OK','changed':False}
    gitdir=Path(git('rev-parse','--absolute-git-dir').strip())
    index=gitdir/'index';old=index.read_bytes() if index.exists() else None
    with tempfile.TemporaryDirectory(prefix='backup-index-',dir=gitdir) as temp:
        tmpindex=Path(temp)/'index'
        if old is not None:tmpindex.write_bytes(old)
        env={**os.environ,'GIT_INDEX_FILE':str(tmpindex)}
        git('add','-A',env=env)
        paths=git('ls-files','-z',env=env).split('\0')
        blocked=[]
        for name in filter(None,paths):
            base=Path(name).name.lower()
            if base=='.env' or base.startswith('.env.') or base.endswith(('.env','.pem','.key')) or base in ('auth-profiles.json','hosts.yml','ops-config.json'):
                blocked.append(name);continue
            blob=git('show',':'+name,env=env,binary=True)
            if b'\0' not in blob and SECRET.search(blob):blocked.append(name)
        if blocked:raise ValueError('snapshot blocked by secret gate (paths only): '+', '.join(blocked[:20]))
        if (index.read_bytes() if index.exists() else None)!=old:raise ValueError('Git index changed during snapshot')
        # Git itself locks index/ref updates; private staging keeps failures out of the owner index.
        git('commit','-q','-m','snapshot '+datetime.now(timezone.utc).isoformat(),env=env)
        os.replace(tmpindex,index)
        return {'status':'OK','changed':True,'commit':git('rev-parse','HEAD').strip()}


def main():
    os.umask(0o077)
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation',choices=['snapshot','checkpoint','gc'])
    p.add_argument('action',nargs='?')
    p.add_argument('value',nargs='?')
    p.add_argument('--workspace',default=os.environ.get('WORKSPACE_DIR') or os.environ.get('OPENCLAW_WORKSPACE'))
    p.add_argument('--files',nargs='+',help='required workspace-relative files; all must exist')
    args=p.parse_args()
    try:
        if not args.workspace:raise ValueError('set --workspace, WORKSPACE_DIR or OPENCLAW_WORKSPACE')
        ws=Path(args.workspace).expanduser().resolve()
        if not ws.is_dir() or ws==Path('/'):raise ValueError('invalid workspace')
        checkpoints=Path(os.environ.get('CHECKPOINT_DIR',str(ws/'memory/checkpoints'))).expanduser().resolve()
        checkpoints.mkdir(parents=True,exist_ok=True,mode=0o700)
        with (checkpoints/'.backup.lock').open('w') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            files=args.files or shlex.split(os.environ.get('CHECKPOINT_FILES','memory/core-state.json memory/threads/main-thread.jsonl memory/active-tasks.md MEMORY.md'))
            if args.operation=='snapshot':result=snapshot(ws)
            elif args.operation=='gc':
                command(['git','gc','--prune=2.weeks.ago'],ws);result={'status':'OK','prune_grace':'2 weeks'}
            elif args.action=='create':
                folder=create(ws,checkpoints,files,args.value or 'manual');result={'status':'OK','checkpoint':folder.name,'files':len(files)}
            elif args.action=='list':
                result={'status':'OK','checkpoints':sorted(p.name for p in checkpoints.glob('checkpoint-*') if p.is_dir() and not p.is_symlink())}
            elif args.action in ('verify','restore'):
                folder=resolve_checkpoint(checkpoints,args.value or 'latest');data=verify(folder)
                if args.action=='restore':
                    destinations=[(entry,safe_path(ws,entry['path'])) for entry in data['files']]
                    for entry,dst in destinations:
                        if entry.get('kind')=='sqlite-backup' and (Path(str(dst)+'-wal').exists() or Path(str(dst)+'-shm').exists()):
                            raise ValueError('stop SQLite writer and checkpoint WAL before restoring: '+entry['path'])
                    present=[entry['path'] for entry,dst in destinations if dst.exists()]
                    before=create(ws,checkpoints,present,'before restore','pre-restore') if present else None
                    restored=[]
                    try:
                        for entry,dst in destinations:
                            dst.parent.mkdir(parents=True,exist_ok=True)
                            tmp=dst.with_name('.restore-'+uuid.uuid4().hex)
                            shutil.copyfile(folder/entry['path'],tmp);tmp.chmod(0o600);os.replace(tmp,dst);restored.append((entry,dst))
                    except Exception:
                        for entry,dst in reversed(restored):
                            if before and (before/entry['path']).exists():shutil.copyfile(before/entry['path'],dst)
                            else:dst.unlink(missing_ok=True)
                        raise
                result={'status':'OK','action':args.action,'checkpoint':folder.name,'files':len(data['files'])}
            else:raise ValueError('checkpoint requires create/list/verify/restore')
        print(json.dumps(result));return 0
    except (OSError,ValueError,KeyError,TypeError,sqlite3.Error,subprocess.SubprocessError) as exc:
        message='backup command failed; no success receipt issued' if isinstance(exc,subprocess.SubprocessError) else str(exc)
        print(json.dumps({'status':'FAIL','error':message}),file=sys.stderr);return 1


if __name__=='__main__':sys.exit(main())
