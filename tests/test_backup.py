import json, os, pathlib, sqlite3, subprocess, tempfile, unittest
from contextlib import closing
SCRIPT=pathlib.Path(__file__).resolve().parents[1]/'scripts/backup.sh'

class Backup(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.ws=pathlib.Path(self.tmp.name)
    def run_backup(self,*args,ok=True,files='MEMORY.md'):
        p=subprocess.run(['bash',str(SCRIPT),*args],capture_output=True,text=True,env={**os.environ,'WORKSPACE_DIR':str(self.ws),'CHECKPOINT_FILES':files},timeout=20)
        self.assertEqual(p.returncode==0,ok,p.stdout+p.stderr);return p
    def test_restore_verified_and_reject_corruption(self):
        note=self.ws/'MEMORY.md';note.write_text('original')
        self.run_backup('checkpoint','create','quoted "reason"')
        self.run_backup('checkpoint','verify','latest')
        note.write_text('changed');self.run_backup('checkpoint','restore','latest');self.assertEqual(note.read_text(),'original')
        manifest=self.ws/'memory/checkpoints/latest/manifest.json';manifest.write_text('{broken')
        note.write_text('owner latest');self.run_backup('checkpoint','verify','latest',ok=False)
        self.run_backup('checkpoint','restore','latest',ok=False);self.assertEqual(note.read_text(),'owner latest')
    def test_missing_and_traversal(self):
        self.run_backup('checkpoint','create',ok=False)
        self.run_backup('checkpoint','create',files='../escape',ok=False)
        self.run_backup('checkpoint','verify','../outside',ok=False)
    def test_sqlite_online_backup(self):
        db=self.ws/'session.db'
        with closing(sqlite3.connect(db)) as c:
            c.execute('pragma journal_mode=wal');c.execute('create table memories(note text)');c.execute("insert into memories values ('fixture')");c.commit()
            self.run_backup('checkpoint','create',files='session.db')
            with closing(sqlite3.connect(self.ws/'memory/checkpoints/latest/session.db')) as saved:
                self.assertEqual(saved.execute('select note from memories').fetchone()[0],'fixture')
    def test_git_secret_gate_keeps_index(self):
        def git(*args):return subprocess.run(['git',*args],cwd=self.ws,check=True,capture_output=True)
        git('init','-q');git('config','user.name','Fixture');git('config','user.email','fixture@example.invalid')
        (self.ws/'README.md').write_text('fixture');git('add','.');git('commit','-qm','baseline')
        (self.ws/'tracked.env').write_text('SYNTHETIC=value');git('add','tracked.env');git('commit','-qm','fixture env')
        (self.ws/'.gitignore').write_text('*.env\nmemory/checkpoints/\n')
        index=(self.ws/'.git/index').read_bytes()
        self.run_backup('snapshot',ok=False)
        self.assertEqual((self.ws/'.git/index').read_bytes(),index)
        git('rm','tracked.env');self.run_backup('snapshot')

if __name__=='__main__':unittest.main()
