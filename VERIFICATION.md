# workspace-backup: acceptance and recovery

## Offline regression

From the reviewed checkout run `bash test.sh`. It runs the repository's provider-free tests using disposable HOME/workspaces. Exit 0 means those tests passed, not that every real model/provider/environment was exercised. Lifecycle tests cover install → reinstall → full-commit update → rollback → uninstall and preserve owner data where applicable. Optional native test skips are printed explicitly.

## Functional acceptance

Input / command: In a synthetic WS, checkpoint create → verify → restore to an isolated destination; repeat with a corrupt archive and SQLite WAL writer.

Expected result: Manifest hashes validate, corrupt/missing required entries or unsafe restore paths fail, and online SQLite backup includes committed WAL data. Git snapshot preserves the user index and blocks secret candidates.

Scope and remaining integration checks: Default checkpoint is not every OpenClaw state file. Inventory config, databases, credentials and workspace explicitly for full recovery; restore a separate instance. Keep existing local schedule; off-VPS copies are currently deferred.

## Failure handling

Keep the exit status, redacted stderr, exact source commit and relevant artifact paths. A missing dependency/probe or incomplete check is not a pass. Reproduce on an isolated fixture; after a change rerun the failed case and this entrypoint. Use the README's matching workspace/instance for rollback. Preserve memory, configuration, queues and evidence files unless their removal is separately intended.
