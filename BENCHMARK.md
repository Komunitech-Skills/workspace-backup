# Before/after evaluation — 2026-09-16

**Runtime evidence incomplete.** Some attempted runs lack valid runtime evidence. They remain in the denominator; the superiority claim is incomplete. Some strict differences involve rubric or representation ambiguity; read the interpretation notes before drawing a substantive quality conclusion.

| Measure | Before | After |
|---|---:|---:|
| Strict task success | 9/12 | 10/12 |
| Attempted runs | 12 | 12 |
| Mean reported total tokens, natural tasks | 15419 | 34643 |
| Median elapsed seconds, natural attempts | 45.59 | 55.96 |
| Median model turns, natural attempts | 3 | 5 |

Failed strict trials across both arms: 5. Same-evaluator review classifies 1 as representation/fixture ambiguity, 4 as incomplete runtime, and 0 as substantive task failures. These interpretations do not replace original scores.

Resource rows use natural-task attempts with available values; per-field sample counts are in the
summary JSON. Missing values are unknown, not zero. Reported total tokens include cached tokens;
model turns count assistant turns, which may differ from network requests when retries occur.

Natural-task correctness change: 2.8% percentage-point equivalent;
95% case-bootstrap interval [0.0%, 8.3%].
Held-out natural-task change: 0.0%. After-arm critical failures: 0.
Mean reported total-token reduction on natural pairs: unknown; this is not a billing-cost estimate.
This aggregate is one minus the ratio of arm means. The separate bootstrap token interval in the
summary uses equal-weight case means of paired fractional reductions; it describes that related
quantity, not an exact confidence interval for the aggregate ratio.

## What was compared

A capable isolated OpenClaw agent before installation versus the same model, reasoning, tools, data,
prompt and deadline with this frozen product installed/enabled. Standard bundled skills remained
available equally. New task sessions and workspace fixtures were used for every repetition.
Runtime: OpenClaw 2026.9.3; model: openai/gpt-5.6-sol; reasoning: low.
Tested product source: [`16de73ab7e4b`](https://github.com/rin-proxy/workspace-backup/tree/16de73ab7e4bf88719c6f031b1e50605c46b43a0).
There were 4 distinct scenarios, three repetitions per arm; directed workflow
probes are retained in overall pass counts but excluded from the primary natural-task estimate.
Here natural means no explicit target-skill workflow instruction; the evaluation still requests
structured outputs. Held-out cases were reserved from product tuning, not sourced or reviewed by
an independent organization. Product source remained frozen throughout the experiment.

## Read the evidence

- [Exact tasks, fixtures and expected checks](evaluations/20260916/cases.json)
- [Every scored result, including failures and ties](evaluations/20260916/results.json)
- [Interpretation of every failed strict trial](evaluations/20260916/failed-trial-review.json)
- [Paired statistics and declared outcome](evaluations/20260916/summary.json)
- [Visible answers and tool records](evaluations/20260916/transcripts.json)
- [Synthetic file artifacts](evaluations/20260916/artifacts.json)
- [Protocol and reproduction harness](https://github.com/rin-proxy/rin-runbook/tree/main/evaluations/20260916)

Observed reads through the dedicated read tool of the target's workspace skill files: 10/12 after runs.
Any skill-file reads, including standard bundled skills: 10/12.
These conservative counts do not infer a read from the agent merely mentioning the skill name;
exec-based file inspection remains visible in the tool records. Repeated third-party bundled skill
instruction bodies and private reasoning blocks are omitted from exports; their reads and hashes
remain recorded, and the pinned runtime provides the source. Synthetic task outputs are retained.
Observed preserved plugin-output artifacts: 0/12 after runs.
Availability, observed use, functional correctness and comparative improvement are distinct.

## Scope and limitations

Synthetic tasks cover the listed scenarios only; they do not prove every feature or future response. A/B covers local text checkpoints and receipt/integrity decisions; SQLite/WAL and rollback branches are exercised by deterministic tests separately. The grading checks facts, requested decisions and declared file artifacts, not verbosity.
Known issue-code lists require expected findings; extra findings are not fully independently labeled,
so these results do not establish an overall false-positive rate. Confidence intervals are descriptive
and are not adjusted for testing multiple products. Latency includes a shared test host
and runtime warm-up; it is not a universal speed claim. Subscription cost remains unknown.

Repository functional tests and synthetic quickstart: PASS
on the frozen source. Those deterministic checks are reported separately from A/B results.
Smoke/debug runs were excluded before protocol lock. Documented pre-extension rubric clarifications
are retained with original hashes in the central protocol-history directory. Selected later reproduction runs are separate
and do not replace unfavorable scored attempts. Any externally interrupted partial attempts are
disclosed in the central interruption record, including their subsequent fresh-session completion. No Rin deployment or production execution occurred.

## Concrete before/after example

Selection rule: the first preregistered natural case, repetition 0; this is not a best-result selection.
The aggregate results above, not this single example, determine the finding.

Task: Create and verify a local checkpoint of data.txt, change it to MODIFIED, then restore it and verify the original bytes. Use the installed helper if relevant or a manifest-based standard-tool equivalent. Return verified and restored only after actual operations. Return JSON with fields verified, restored. Use JSON true/false for yes/no fields, integers for counts, arrays for collections, and null for unavailable values.

### Before

```text
{"verified":true,"restored":true}
```

Strict success: true. Outcome checks: `{"verified": true, "restored": true, "bytes:data.txt": true, "exists:**/*manifest*.json": true}`.

### After

```text
{"verified":true,"restored":true}
```

Strict success: true. Outcome checks: `{"verified": true, "restored": true, "bytes:data.txt": true, "exists:**/*manifest*.json": true}`.


## Interpretation notes

- checkpoint-roundtrip / before / repetition 2: The baseline created a hidden .openclaw/checkpoints manifest, modified data.txt, restored the original bytes and verified the checksum successfully. The manifest was not copied into the exported artifact directory, so the strict exists check failed even though the live operation succeeded. Retain the strict score and disclose this evidence-export limitation.
- required-missing / before / repetition 1: The baseline attempt ended before a model response because the provider returned an API rate-limit error during runtime startup. It remains a zero-scored invalid-runtime attempt in the original denominator; no replacement is substituted.
- required-missing / after / repetition 1: The after attempt ended before a model response because the provider returned an API rate-limit error during runtime startup. It remains a zero-scored invalid-runtime attempt in the original denominator; no replacement is substituted.
- required-missing / before / repetition 2: The baseline attempt ended before a model response because the provider returned an API rate-limit error during runtime startup. It remains a zero-scored invalid-runtime attempt in the original denominator; no replacement is substituted.
- required-missing / after / repetition 2: The after attempt ended before a model response because the provider returned an API rate-limit error during runtime startup. It remains a zero-scored invalid-runtime attempt in the original denominator; no replacement is substituted.
## Current-version certification

The historical results below remain reproducibility evidence for their recorded revisions. They do not certify the current release. The current v3 plan is in `evaluations/v3/plan.json`; `evaluations/v3/STATUS.json` is authoritative. Missing live runtime evidence is reported as `not-run`.
