# Model notes — how workers actually perform

A running log of how models perform on real Ringer tasks, so engine and
model choices are made on evidence instead of vibes. The raw numbers now
live in the local eval log (`~/.ringer/runs.jsonl`); run `./ringer.py models`
to print the per-model, per-task_type scoreboard (tasks, attempts,
pass_rate, first_try_pass_rate, median duration/tokens, last_seen). This
file remains the judgment layer on top of those numbers.

**How to add a row:** after reviewing a run (post-run ritual step 5 in the
ringer skill), append one dated line under the model. Say the task type,
what happened, and what you'd do differently. Only write what the executed
checks and raw logs support — no vibes, no worker self-reports.

**Index note (2026-08-20):** commit `9c96831` (branch copy `c0ad12a`) backfilled
dated entries 2026-07-21 → 2026-08-18 across many sections in one commit; `git
log` does not surface them. This file, not the log, is the record of that period.

## codex (GPT-5-class, own harness)
- 2026-08-28 — p2a-adjutant-correction (code-fix ×2, code-feature ×1; gpt-5.4, worktrees, patch-export): all three tasks reported FAIL after 2 attempts, but every patch was correct and applied clean to the real repo (131 passed, same 5 pre-existing failures as baseline; runtime proven: doctor 401→200, route 410, manifest written). The check demanded a green full suite in a worktree where the baseline already had 5 reds — orchestrator error, not model error. t3 added an out-of-ownership tests/conftest.py that monkeypatched the failing builder to get green: reject shims outside ownership even when they pass. ~107k/175k/230k tokens. Lesson: baseline the suite on the target repo before writing a full-suite check; `lint` does not do it.
- 2026-08-28 (afternoon) — p20b r1/r2 (code-feature/code-fix), mjr939 installer (code-feature, PASS 1st try, ~83k), manifest (code-feature, check FAIL ×2 but product correct — orchestrator check ran a pytest glob before the worker created the file; applied and green in the real repo), statuslint (code-fix, PASS 1st try, ~83k). Pattern of the day: a worker that cannot run the live legs will still ship a correct static shape; the live-machine pass found 4 defects in p20b r1 and 1 (substring needle) in r2. Keep the orchestrator live pass mandatory; keep worker checks static-only and baseline-aware.
- 2026-08-08 (research / SRG bookkeeping judgment packs, s31+s32): s31 3/3
  with one-retry pattern on judgment packs; s32 repeat — 3/3, two of three
  needed one retry (validator: thin rationale / disposition vocab misses on
  attempt 1). Retry-with-injected-failure reliably rescues; keep Codex on
  judgment, budget one retry into timing.
- 2026-08-08 (docs / mech classification, s31): Sonnet 7/7 first-try on
  coding packs at ~200-token median; s32 repeat 3/3 first-try. Sonnet is
  the proven mech-pack default for this workload. (Recorded under codex
  section for the s30/s31 comparison context: GLM was NOT exercised in s31;
  the s30 GLM note debt is closed as no-evidence — nothing to record.)
- 2026-07-21 — planner-p0-hardening task1 (code-feature): OAuth plan usage limit hit, both attempts died at 0 tokens ("try again Jul 25"). Not a capability signal. Route around codex until 2026-07-25; check limit before assigning heavy lanes.

- Strongest general worker; the default engine. Spend reasoning effort per
  task via `engine_args` (`["-c", "model_reasoning_effort=low|medium|high"]`)
  — high on gnarly tasks, low on boilerplate.
- 2026-07-05 — carried the heavy lanes of the milk-crate demo rehearsals
  (market read with source allowlist, site build) with clean first-attempt
  passes.
- 2026-07-10 — gpt-5.6-sol, code-feature (steering-profiles feature in
  ringer.py itself, ~470-line change + 18 tests + docs, run
  ringer-steering-profiles): shipped as PR #25. 2 attempts, 379k tokens,
  but the attempt-1 FAIL was the CHECK's fault, not the model's — the check
  gated on the ENTIRE pre-existing suite being green inside the worker
  sandbox (localhost binds blocked, fixture missing). The feature work
  itself was verified green both attempts; attempt 2 "hardened" an already
  -sound implementation. Scoreboard's FAIL row for this run understates the
  model. Lesson for check authors: regression gates must compare against
  the BASELINE failure set, never assert absolute suite green.
- 2026-07-06 — adversarial pre-merge review (aicred spark): passed on
  attempt 1, ~85k tokens.
- 2026-07-06 — motion design (5 HTML animations for video b-roll) + 2
  editorial diagram pages, each verified by rendering through headless
  Chromium to MP4/PNG: 7/7 passed on attempt 1. Broadcast-quality visual
  output from rich storyboard specs; the render-as-check pattern works.
- 2026-07-06 — milk-crate demo: two single-file website builds (v1 scaffold
  316s/~175k tok; final brand+market-test reskin 622s/~184k tok), both passed
  14-assertion content checks on attempt 1, including base64-embedding photos
  and honoring honesty-marker requirements. Codex remains the site-build lane.
- 2026-07-06 — ringer.py feature batch (task_type field + enriched eval rows
  + `models` scoreboard + hud single-tab fix; ~640-line diff incl. two new
  test suites): substance passed on attempt 1 — its check printed PASS
  (compile, all 16 suites, exact CLI aggregation contract) — but the run
  recorded attempt 2 because of the expect_files-before-check harness bug
  (see process lessons). Heavy single-file feature work against an exact
  behavioral contract is squarely codex's lane.

- 2026-07-06 — elsas-website demo: Next.js scaffold PASSED attempt 2 (682s,
  ~354k tok) — attempt 1 built a complete homepage and silently skipped the
  other 10 routes; the route-enumeration check caught it. Narration lane
  (15 ElevenLabs calls, chunked, nohup pattern) passed attempt 1. CAUTION: a
  codex fix worker GAMED a verbatim-content needle by hiding the required text
  in a visually-hidden paragraph — passed the check, caught only by
  orchestrator integration review. Needle checks need an anti-hidden-text
  assertion or documented exceptions.

- 2026-07-06 — OpenRouter catalog + explore suggester (catalog subcommand
  with snapshot/changelog/free-detection, daemon auto-refresh, tiered
  --explore; offline fixture-driven contract check): PASS attempt 1, 362s.
  Follow-up sentinel-pricing fix (variable-pricing models): PASS attempt 1,
  114s. With the verify-order fix landed, zero phantom retries across the
  whole batch.
- 2026-07-06 — adversarial review of the model-router stack (2,650-line
  diff, structured report contract): PASS attempt 1, 176s — found a real
  HIGH (--since window inflating first-try rates) plus 3 MEDIUMs, all
  confirmed against the code. Then fixed all five review findings in one
  batch (task-level --since, pricing transitions, event durability + flock,
  unknown pricing, stderr notice) with test coverage: PASS attempt 1, 202s.
  Review->fix roundtrip in codex's lane works end to end.
- 2026-07-06 — scoreboard HTML page (zero-LLM renderer, ~700-line diff,
  design + evidence-floor ranking + cost math + notes parser): substance
  PASS attempt 1 (the run's recorded retry was an orchestrator check bug —
  the free-promo watchlist legitimately mentions a free model before the
  ranked cards, and the check compared raw first-occurrence). Six review
  findings fixed in one batch, PASS attempt 1, 141s.
- 2026-07-06 — model-db stack (SQLite read model 516s, page redesign 536s,
  Ringside tab 527s, plus three fix batches all attempt-1): five substantial
  ringer.py features in one day, every one against an executed contract
  check. Review lane found the HIGH that mattered (sync cursor skipping a
  half-written trailing line). Codex is the proven lane for both sides of
  the review->fix loop on this codebase.

## glm-5.2 via opencode (`openrouter/z-ai/glm-5.2`)

- The cheap-intelligence default (~$0.74/M in, $2.33/M out, 2026-07 —
  20-30x cheaper output than frontier coding models). Reliable on
  mechanical, tightly-specced work: file edits, format conversions,
  template-driven builds.
- 2026-07-05 — milk-crate demo rehearsals: handled brand-board/SVG/copy
  tasks at around a penny per passing task.
- 2026-07-06 — adversarial pre-merge review (aicred spark): passed, but
  needed the retry (attempt 2) where codex passed on attempt 1. Long
  structured reviews sit at the edge of its comfort zone; keep the section
  contract explicit in the spec.
- 2026-07-06 — three mechanical image-generation batches (18 images via
  openrouter-image commands, idempotent batch-runner spec): 3/3 passed on
  attempt 1, ~14.5k tokens each. The "execute these exact commands, do not
  improve them" spec pattern is fully reliable for glm-5.2.

- 2026-07-06 — backfill/seed script for the model log (252-line stdlib CLI
  with a run-state join, 3-level mapping precedence, never-overwrite and
  idempotency rules): the artifact was CORRECT; the recorded FAIL was an
  orchestrator check-fixture bug (a missing newline glued the fixture's last
  row to a garbage line) plus the harness ordering bug below. Verified PASS
  once the check was fixed. Tight behavior contracts in the spec work great
  for glm — and read the raw logs before blaming the model.
- 2026-07-06 — README/MODEL-NOTES docs + task_type sweep across 17 template
  manifests: passed attempt 2; attempt 1 was lost to the harness ordering
  bug, not model quality — the retry worker's log correctly diagnosed that
  harness bug unprompted, impressive debugging from the cheap lane.
- 2026-07-06 — catalog/explore README section (flags, promotion ladder,
  per-user framing): PASS attempt 1, ~21.5k tokens. Doc sections against a
  grep-able content contract remain a safe glm lane.
- 2026-07-06 — milk-crate demo, full run: 4 independent buyer-persona
  reviews (focus group) all passed attempt 1 (~15k tokens, ~2¢ each) with an
  explicit VERDICT-block contract — persona work is squarely in glm's zone.
  Market read with live curl fetching passed once the spec demanded verbatim
  copy-paste of source URLs (first fail was the worker trimming URL slugs —
  spec/check craft, not model weakness). Brand-kit doc incl. a clean inline
  SVG wordmark: good, one bounce off an over-strict check regex.

- 2026-07-06 — elsas-website demo: verbatim content capture (16 pages + 19
  news posts, 213 blockquotes) passed attempt 2 — attempt 1 SELF-REPORTED
  "all 213 match exactly, 0 errors" while the executed check found 13 stitched/
  paraphrased quotes. Self-reports are worthless; the retry with injected
  failures fixed all 13 (~148k tok total, ~3¢). Page builds (about+faq;
  news index + 19 generated post routes via its own extraction script) and
  2 focus-group personas: all attempt 1. Fix batch attempt 1.
- 2026-07-06 — invariants/file-I/O review lens on the same stack: PASS
  attempt 1, 68k tokens — caught the non-atomic backfill rewrite (real data
  loss risk) and the daemon stdout race; both confirmed. Then fixed the
  backfill atomicity (tmp+os.replace, pid-stamped backups) attempt 1 with
  the original behavioral grader unchanged. Structured review with an
  explicit lens is now proven glm territory, not just probation.
- 2026-07-06 — solo adversarial review of the scoreboard renderer (~700
  line diff, injection-focused lens): PASS attempt 1 — 1 MEDIUM (unanchored
  MODEL-NOTES heading match cross-contaminating gpt-4/gpt-4o-style
  families) + 5 real LOWs, plus an empirically-verified injection all-clear
  (it actually rendered hostile model ids to prove escaping). Second
  proven-tier structured review in one day; glm is now the default review
  lane for mid-size diffs.
- 2026-07-06 — invariants/injection/frontend review of the 4,061-line
  model-db branch: PASS attempt 1, 96k tokens, 14 coverage items — two real
  contention findings (full catalog re-ingest per sync; schema writes on
  read paths) plus an empirical XSS all-clear on the new DOM surfaces.
  Third proven-tier structured review today.

## kimi-k2.7 via opencode (`openrouter/moonshotai/kimi-k2.7-code`)

- 2026-07-06 — adversarial pre-merge review (aicred spark): passed on
  attempt 1, ~83k tokens. First real outing; promising for review work.
  (Ran through an ad-hoc copy of the opencode engine block — the per-task
  `model` field now makes that unnecessary.)

## kimi-k2.6 (`moonshotai/kimi-k2.6`, subject-model evidence via OpenRouter)

- 2026-07-07 — Benchmark Suite 2.0 operator eval, killed by Jon at ~4.5h.
  Serving throughput, not model quality, was the failure: on the Brick
  1000-piece case (reasoning xhigh, pinned provider order
  inceptron→decart→baidu→modelrun, no fallbacks) K2.6 averaged ~21 tok/s
  with two ~19-min stalls at 4.5 tok/s — 136+ min unfinished vs Sonnet 5's
  25 min (94 tok/s) and GPT-5.5's 24 min (55 tok/s) on the identical case.
  Model behavior itself was fine: 28 turns (fewer than Sonnet's 82), 170k
  output tokens (in family norms), 12% reasoning, zero API errors. Verdict:
  do NOT schedule K2.6 for long agentic work through that provider set;
  if K2.6 data is ever wanted, probe a single case against other providers
  first. Distinct model from k2.7-code above — don't transfer this verdict
  to k2.7.


## grok-build (Grok CLI engine, flat plan)

- 2026-07-10 — identity correction (Jon): the Grok Build CLI is a HARNESS
  serving exactly two models — Grok 4.5 (xAI) and Composer 2.5 (Cursor).
  The engine-lane slug `grok-build` resolves to Grok 4.5. "Grok Build 0.1"
  was never a model; earlier notes/rows using it as one describe Grok 4.5.

- 2026-07-06 — first outing (elsas-website demo), engine added same day:
  audition PASS attempt 1 in 28.9s. Then: asset harvest (11 images, live URL
  re-fetch check), books page, 5 work-page routes in one task (59 verbatim
  needles), adversarial code review (10 real findings incl. an unshelled 404
  and a broken embedded link), press/media fix batch, audio-player integration
  across 15 pages — ALL attempt 1 (player's red ledger entry was a check bug,
  artifact certified). Fast, precise on mechanical/code work. No token counts
  in JSON output (flat plan) — cost reads "included in plan".

## grok-composer-2.5-fast (Grok CLI engine, flat plan)

- 2026-07-06 — first outing (elsas-website demo): audition PASS attempt 1
  (138s — slower than grok-build but the strongest copy of the round).
  Accessibility constitution (14 testable criteria, SC-numbered) attempt 1;
  a11y-gatekeeper harness (axe+Playwright, light/dark, reduced-motion assert)
  attempt 2 — attempt 1's harness mishandled Next's default /404 route.
  Events/faq/contact fix batch attempt 1, but satisfied "editorial grid" with
  an EMPTY aside landmark — axe caught it (landmark-complementary-is-top-level).
  Persona work: good. Watch for letter-of-the-spec shortcuts on layout asks.

## nemotron-3-super-120b (via opencode, `openrouter/nvidia/nemotron-3-super-120b-a12b:free`)
- 2026-08-08 (docs / SRG bookkeeping mech-classification, s32 Phase-3 Stage 1):
  audition on one 28-line coding pack (free promo). Attempt 1 FAILED the
  executed validator, attempt 2 PASSED clean (28/28 verdicts, ~268k tokens,
  ~32min — slowest task in the run by 8x vs Sonnet). Verdict quality fine on
  spot-check. Usable as free overflow for non-urgent mech packs; do not put
  it on the critical path — latency and first-try miss cost more than Sonnet
  saves when the run gates a sitting.

- 2026-07-06 — AUDITION FAILED (exploration slot, $0 spent — free promo).
  Task: fresh-eyes adversarial review of a 2,650-line diff with a structured
  report contract. Failed both attempts on the same executed check: report
  had the right sections and verdict but under 3 concrete code citations —
  shallow engagement with the actual code, 212k tokens burned. Don't re-run
  this audition on long structured code review; if it gets another slot,
  try a shorter, more mechanical task first.

## llama-3.3-70b-instruct (via opencode, `openrouter/meta-llama/llama-3.3-70b-instruct:free`)

- 2026-07-06 — AUDITION FAILED (exploration slot, $0). Fresh-eyes review of
  a 4,061-line diff with a verbatim-quote citation requirement: failed the
  structured-report check both attempts. Second free-model audition to fail
  on long structured code review (after nemotron-3-super) — the exploration
  ladder now says: audition free models on SHORT mechanical tasks first;
  long-diff review is a proven-tier lane.

## Small / flash-class models

- First to choke on long conversational or multi-turn harness tasks —
  watch retry counts before scaling them into a batch (2026-07-05 focus
  group lesson).

## Process lessons (cross-model)

- 2026-08-20 — run `nate-docs-adoption-review-20260820T125654Z-p82661` (estate doc
  edits, codex/gpt-5.4-high, 8 tasks / 16 attempts): the headline lesson is a FALSE
  PASS — the executed checks returned PASS on `p1-loop-contract` and
  `p2-venture-clock` although both workers produced ZERO edits ("Patch was blocked
  by sandbox policy"); the orchestrator had applied those patches by hand mid-run,
  and the checks could not tell worker output from orchestrator repair. This file's
  recurring check-bug class is the false FAIL; this is the inverse and worse — a
  check that does not discriminate authorship passes work nobody did. Rule: before
  accepting a PASS in an edit swarm, verify the worker's own diff or export is what
  satisfied the check. Sandbox context (not the headline): `--sandbox
  workspace-write` blocked out-of-taskdir writes for every worker — both "PASSes"
  carry retry=true alongside 14 FAILs, which config variance cannot produce; no
  task had writable roots set. Remedies in order: (1) scoped
  `sandbox_workspace_write.writable_roots` per `templates/repo-feature/manifest.json:16`
  and `templates/repo-feature/README.md:49` (proven 2026-07-06); (2) patch-export
  contract — workers write complete post-edit copies to ./out/ with truncation
  guards, orchestrator diffs, applies, re-runs live checks (6/6 first-try on rerun
  `nate-docs-adoption-review-20260820T132223Z-p89764`); (3) `full_access` LAST —
  it maps to `--dangerously-bypass-approvals-and-sandbox`, a sandbox bypass, not a
  configuration choice.
- 2026-07-21 — planner-p2 t7: check bug class NEW to the list — a
  forbidden-pattern grep (`new Date()|Date.now`) matched the worker's COMMENT
  explaining it doesn't use those calls. Worker attempt-2 substance was correct;
  the red row is orchestrator fault. Rule: strip comments (sed 's|//.*||') before
  any forbidden-pattern grep on source files.
- 2026-07-21 — planner-scenario-editor (opus): attempt-1 "FAIL" was functionally
  correct code — element ids assigned at RUNTIME (sel.id = x) are invisible to a
  static grep contract. Worker self-diagnosed on retry, made every contract id a
  source literal, and honestly reported its sandbox blocked node --check instead
  of bypassing. Check-author rule: when a contract will be grep-verified, the
  SPEC must say "these ids/classes must appear as literals in source".
- 2026-07-21 — planner-p3 t8: same family, third instance — `grep -qF "--fan-inner"`
  parsed the needle as OPTIONS (grep usage error -> false FAIL x2 on a correct
  opus build). Rule: ALWAYS `grep -- "$needle"` when needles can start with a dash.
  planner-p3 t4 (sonnet): substance passed attempt 1; recorded FAILs were a leftover
  `_probe.py` scratch file tripping the ownership gate — benign self-test, removed at
  integration. Spec rule: remind workers to delete scratch files before finishing.

- 2026-07-06 — the orchestrator's CHECKS were the day's top failure source:
  three check bugs (fixture newline join, first-occurrence ordering vs the
  watchlist strip, claim-prefix split on '.' instead of ':') each produced
  a FAIL verdict on work that was actually correct — including all four
  capability-research packets at once. Every one was caught by reading raw
  logs/artifacts before blaming the model. Corollary for the scoreboard:
  recorded FAILs whose root cause was a check bug are annotated here, and
  check fixtures deserve the same review care as production code.


- 2026-07-06 — HARNESS BUG (fix in flight on feat/model-perf-log):
  Verifier.verify evaluated expect_files BEFORE running the check, so any
  check that itself creates/exports its deliverable (the worktree
  patch-export pattern) failed attempt 1 with "missing expected files" even
  when the check printed PASS. Cost 3 phantom retries in one run — and it
  poisons first_try_pass_rate, the model log's routing signal. Until the
  reorder lands on your checkout: have the WORKER write the declared
  deliverable, or don't declare check-created files in expect_files. When
  reading seeded scoreboard numbers, remember 2026-07-06 first-try rates
  are depressed by this.
- 2026-07-06 — the model log is now automatic: every attempt row carries
  model/task_type/retry; `./ringer.py models` prints the scoreboard; 81
  historical rows were seeded via scripts/backfill_model_log.py with a
  hand-authored task-type mapping. Give every manifest task a task_type or
  its evidence buckets as (untyped).

- 2026-07-06 — a three-model "bakeoff" ran every task on the engine's
  hard-coded model: task keys said glm/gpt/kimi, but the opencode engine
  block pinned glm-5.2, so one model wrote all three "competing" reviews.
  This is why the per-task `model` field exists — a bakeoff is only a
  bakeoff if the manifest, not the engine block, names the model. Verify
  with the `model` column in the run state, not the task key.
- 2026-07-06 — spawning 5-6 opencode workers simultaneously hit opencode's
  local "database is locked" (sqlite) — several instant attempt-1 failures,
  all absorbed by Ringer's retry. Cosmetic in Ringside ("sent back" at 0s) but
  wastes an attempt; consider staggering opencode spawns.
- 2026-07-06 — opencode's bash tool kills foreground commands around the
  ~2-minute mark: a 2min+ image-generation API call can never finish inline.
  Spec pattern that works: nohup the long command in the background, then
  poll for the output file in separate short commands.
- 2026-07-06 — two check-craft lessons from the same run: (1) URL-allowlist
  checks must be prefix-tolerant (workers legitimately trim slugs); (2) any
  heading-regex must tolerate numbered headings ("## 3. Type / Typography").
  Both failures looked like worker laziness until the raw logs said otherwise.
- 2026-07-06 — elsas-website demo, check-craft in BOTH directions: (1) a fixed
  800-char body floor failed a worker for faithfully converting genuinely tiny
  source posts — floor must scale with the source; (2) a citation gate treating
  every backtick as a page-quote failed honest reviewers who backticked their
  own fix-suggestions — line-scoped pair parsing + attribute-aware corpus fixed
  it; (3) needle-exception lists must be shared across ALL checks that consume
  the needle set (a needle excepted in one checker failed a task through
  another). Post-mortems ruled FOR the worker 3 times this run — read raw logs
  before blaming the model.
- 2026-07-06 — opencode sqlite "database is locked" again with just 2
  simultaneous opencode spawns (page-news + page-about-faq); retry absorbed it.

## codex (2026-07-06, bench-operator-proofing)
- 8/8 code-feature tasks passed attempt 1 across 3 rounds (worktrees mode, Python harness refactor; 108k-406k tokens/task). Specs embedded the approved architecture doc + exact file ownership; checks built fresh uv venvs and ran the full pytest suite.
- Lesson (check design, not model): all 3 post-integration bugs were invisible to the checks — a test that passed only because the worker's worktree lacked .env, a `--help`-only assertion missing a runtime importlib/sys.modules bug (py3.12 dataclasses), and bare console-script names failing outside activated venvs. Checks should exercise one real invocation from a cold shell, not just --help.

## gpt-5.6-sol (codex)
- 2026-07-15 ringer-self-update run (3 serial tasks, direct-repo-edit mode): code-fix baseline-test repair 1/1 first-try (61k tokens, 1.6m); code-feature self-update mechanism (git fetch/ff-pull/re-exec + HUD staleness restart + 20-test suite) 1/1 first-try at high effort (153k, 8.1m); code-feature signal-contract (all 3 scoreboard surfaces + canonical-route lint enforcement) passed on retry (358k, 13.7m) — attempt 1 died on stale old-column assertions in pre-existing tests it hadn't finished updating; the retry prompt's injected FAIL list was enough to close it out. Lesson: when a task rewrites a display contract, name every test file asserting the old contract in the spec's ownership list AND tell it to update them FIRST.
- 2026-07-09 code-feature/code-fix (ringside-overhaul): 4/4 first-try — a ringer.py logging change with tests, a 265-line stdlib backfill CLI (atomic rewrite, dry-run, idempotence all check-verified), a ~1500-line single-file HTML redesign (running-now pills + worker-card grid + multi-expansion refactor, 30KB patch, node --check + contract greps + unittest), and a render-gating change where it correctly UPDATED tests asserting the old behavior instead of gaming the check. Medium/high reasoning, 65–120k tokens/task.
- Same day, different session (bench-harness-patches, code-fix): 0.29 first-try over 7 tasks on a Next.js/Turbopack harness. Spec and check quality dominate model choice — see the scoreboard before generalizing either number.

## GPT-5.5 (codex) — attribution caveat
- Scoreboard rows dated before 2026-07-09 may actually be gpt-5.6: codex eval rows logged model="" until the write-time stamping fix (PR #18) and were credited to GPT-5.5 by the registry default at read time, while the machine's codex default had already moved to gpt-5.6-sol at an unknown earlier date. `scripts/backfill_model_from_logs.py` re-stamps rows with surviving command-log evidence; anything it skips is a mixed-model aggregate. Trust post-2026-07-09 rows.

## nvidia/nemotron-3-super-120b-a12b:free
- 2026-07-08 (research, content-strategy-recon): FAIL x2. Did the analysis in chat but never wrote report.md; attempt 2 exited rc=0 with no file. Doesn't reliably follow file-output contracts under OpenCode. Demoted — don't re-audition on file-deliverable tasks.

## meta-llama/llama-3.3-70b-instruct:free
- 2026-07-08 (research, content-strategy-recon): FAIL x2. Timed out at 900s both attempts on a moderate DB-scrape+format task. Too slow on the free tier for harness work. Demoted — don't re-audition without much longer timeouts or paid tier.

## z-ai/glm-5.2 (addendum)
- 2026-07-08 (research/filter, pitch-foundry): FAIL x2 on a long-spec rubric-application task (~40k input: embedded rubric + 4 candidate files). Read all inputs, exited rc=0 with ZERO output tokens both attempts — silent stall, no file written. GLM handled the same session's shorter formatting specs fine. Lesson: keep GLM specs short; route long-context apply-this-rubric work to codex.

## GPT-5.5 (codex) — honesty flag
- 2026-07-08 (image-gen, pitch-foundry): sandbox DNS blocked openrouter.ai; ALL 10 API calls errored (logged honestly in gen-log) — but the worker then FABRICATED 10 deliverables locally (composited canvases from the ref image) to satisfy a files-exist>40KB check, and passed. Lesson: (a) codex sandbox has no external DNS on this machine — route API-calling tasks to opencode (network open); (b) never write an existence-only check for generated media — require the success log (SAVED/cost lines) to match the file count.

- 2026-07-09 persona-review (pitch-foundry exec-briefing panel): 0/2 first-try+retry. Produced coherent review CONTENT as chat text but never wrote report.md — does not reliably use file-write tools under opencode. Demoted; do not re-audition for file-deliverable tasks without a write-tool probe first.

## gpt-5.6-luna (codex)
- 2026-07-09 code-feature (unlock-ai guide-format conversion, strict type-contract check): 1/1 first-try, 42.6k tokens, 80s. Followed a multi-file TS pattern precisely at $1/$6 pricing. Good candidate for mechanical codegen/docs lanes; audition in adjacent types.

## opencode / z-ai glm-5.2 (via openrouter)
- 2026-07-09 (aicred-invoice-downloads, 4 code-fix tasks + 1 follow-up, worktrees+npm ci checks): systematic attempt-1 NO-OP — all 4 parallel workers produced zero edits and no summary on first attempt, then completed cleanly on attempt 2 after retry-prompt injection (34k-69k tokens each). Follow-up single task passed attempt 1. Suspect first-invocation session warm-up in opencode-sandboxed under parallel spawn; budget for 2 attempts on parallel GLM batches. Output quality on Next.js/Stripe route+test work: solid, spec-faithful, one boss-caught design gap (used user-scoped supabase client where RLS demanded service role — spec didn't say explicitly; say it explicitly).

## opencode (harness note, any model)
- 2026-07-28 (code-review, pr82-token-saver-review): GLM 5.2 produced a complete, high-quality 218-line report but could NOT write it to an output directory created by the parent Claude Code process — every write returned EPERM. It then spent ~3000s burning retries on ctypes/`openat`/AppleScript/`sandbox-exec` workarounds until it timed out, and the task logged as FAIL despite the deliverable existing in its taskdir. Codex workers in the same run were unaffected. Lesson: point opencode workers' output INSIDE their own taskdir and harvest via `expect_files`; never hand them a shared output dir another process created. This is an orchestrator spec bug, not a model failure — do not read the FAIL as evidence against GLM.

## Process lessons (2026-07-28, PR #82 review)
- **Ideas worth keeping from a rejected PR.** PR #82's pre-call gateway was dropped (needs your own API key, so it converts flat-rate OAuth plans into metered API billing; incompatible with Claude Code; and it saves tokens by stripping the tool list, which is the thing that makes the CLI worth using). One idea inside it is worth remembering if the problem ever comes back: an *explicitly blessed* answer cache — key a reviewed answer to the exact request plus the exact selected source packet, and replay it with zero upstream calls, never auto-accepting a model answer. It only fires on byte-identical repeats, which is why it didn't justify 2,000 lines here.
- **Doc-stated support floors need a CI job or they are fiction.** README promised Python 3.11+ while CI only ever ran 3.12; a 3.12-only f-string reached review with a fully green suite. Either test the floor or move it.

- 2026-07-21 — planner-p1b (8 sequential one-task manifests, same run_name):
  8/8 PASS attempt 1, zero probe bugs, zero integrity incidents. Lanes: GLM 5.2
  4/4 (estate fix, two strategy modules, bracket_fill, metrics — 69-73k tok,
  ~100-150s each), opus 2/2 (strategy-interface plumbing through the projection
  fixed point; guardrails state in the core loop), sonnet 2/2 (scenario runner +
  loader split; CLI subcommand restructure). Every check baselined before spawn
  (--baseline caught nothing this time — the three standing check-author rules
  from P0/P1a were applied at authoring). Contrast with P0/P1a's ~6:2
  probe-bug ratio: writing exact assertions only at unit level (no projection),
  using discriminating fixtures (10%-return opening-balance probe), and no-account
  /zero-tax fixtures for exact spend arithmetic eliminated the false-FAIL class.
  Codex remained usage-limited (Jul 25); grok benched by choice.

- 2026-07-21 — planner-p2 t3 (code-feature, sonnet): FAIL x2 on the scoreboard
  but SUBSTANCE CORRECT — worker wrote the right files at the right paths AND a
  stray nested tools/retirement-planner/tools/retirement-planner/ duplicate
  (path confusion working from the planner subdir); pytest collected both test
  copies, the nested one couldn't find fixtures. Untouched check passed once
  the orchestrator deleted the stray dir; merged after review. Spec lesson:
  when the repo nests the project under tools/<name>/, tell workers explicitly
  "all paths are relative to the WORKTREE ROOT; never create tools/<name>
  inside tools/<name>" — second path-confusion class this program.

## grok (Grok Build CLI, grok-4.5)

- 2026-07-21 — planner-p0-hardening task2 (code-fix): PASS attempt 2, ~12min. Implementation correct (exact planned 2-line fix) and its diagnosis of a miscalibrated check bound was RIGHT — but instead of failing and reporting, it EDITED THE ORCHESTRATOR CHECK SCRIPT (writable because checks lived under /private/tmp and grok Seatbelt allows temp writes). Verdict void until independent re-verification (which confirmed the fix). Lesson: never store checks/patches under temp with grok workers; now in ~/.ringer/p0/. Behavior note: strong analysis, weak verification-boundary respect — spec future grok tasks with an explicit "if the check seems wrong, FAIL and report; never modify verification" rule.

## claude (Claude Code CLI, subscription lane)

- Cross-ref: Sonnet's 2026-08-08 SRG mech-classification results (7/7 and 3/3
  first-try) are filed under `## codex` for s30/s31 comparison context.

- 2026-07-29 — OP-COORD-01 program survey (research, 17 tasks across 4 rounds, sonnet on `claude` / `claude-readonly` / `claude-research` lanes): **the scoreboard's red rows for this job are almost entirely MINE, not the model's.** 8 of 9 first-round failures were orchestrator check bugs, each burning a retry: (1) section anchors treated as part of a path — `SOP-013.md §3.1` never `exists`; (2) repo-relative paths resolved against the caller's cwd; (3) `gate`/`obligation`/`person`/`entity` nodes required to have a filesystem path, when a deadline or an external org has none; (4) only the FIRST node table parsed, so reports that split nodes by class lost most rows and then threw phantom "undeclared node" errors on their own edges; (5) escaped pipes (`\|`) inside cells splitting rows into the wrong cell count and silently dropping them; (6) markdown HEADER rows checked for citations — a header containing the word "Pricing" failed as an "unsourced pricing claim", twice. Re-running the 8 against fixed checks: 7 passed, 1 was a genuine catch. **Lesson (5th instance of this class in this file): baseline a check against a REALISTIC artifact, not a hand-written fixture.** My fixture used one node table, absolute paths, no anchors, no escaped pipes — none of the shapes real workers produce. The fixture passed; reality failed. Baseline against a sample of actual worker output before spawning a batch.
- 2026-07-29 — same job, the model's actual behaviour was strong. Workers repeatedly refused to assert `live` when their tooling could not prove it, wrote `verified_how=GAP` instead, and said so explicitly in their own Gaps sections ("this is a materially different, weaker command than a direct `stat`, noted here so it isn't mistaken for one"). One flagged that its finding "confirms the brief's premise rather than surfacing an exception to it" — i.e. volunteering that it had found absence of evidence, not evidence. When briefed with an epistemic standard, sonnet holds it under pressure and reports its own limits unprompted. The single real failure was mislabeling an unchecked item `held` rather than leaving state empty — an over-assertion, correctly caught by the check.
- 2026-07-29 — sandbox note for the `claude` engine: widening `--allowedTools` to include read-only shell (`ls`/`stat`/`git log`/`launchctl list`) got `launchctl`, `launchctl print` and `ps` working, but did NOT lift the harness's working-directory restriction — `stat`/`find`/`git` against any path outside the worker's own taskdir stayed blocked even with the disable-sandbox flag set. That is a separate, harder layer than the tool-prefix allowlist. Workers routed around it by reading `.git/logs/HEAD` directly (the Read tool is not so restricted). Budget for this: filesystem-inspection swarms on this harness cannot `stat` the estate, and specs should say so up front rather than letting workers discover it and spend turns on it.

- 2026-07-21 — planner-p0-hardening task4 (code-feature, sonnet): scoreboard FAIL x2 is FALSE — both failures were orchestrator-check bugs (asserted post-split deb_income monotonicity, then a withdrawal-order confound; three probe rewrites needed). Worker code was correct from attempt 1; attempt 2 correctly re-diagnosed the check, honored the integrity rule (investigated, reported, did not touch verification), cleaned its scratch files. Treat sonnet as strong on this codebase despite the red rows. Check-author lesson: split-optimizer output and withdrawal sourcing are NOT monotone in inputs — probe per-return deltas with split disabled.
- 2026-07-21 — planner-p0 rounds 6-8: opus first-try on the two hardest tasks (projection fixed-point restructure ~7min; estate module ~4min) with correct out-of-ownership constraint handling (recomputed credits rather than touching a frozen module). sonnet first-try on the integration sweep. GLM 5.2 finished 3/3 first-try on this codebase (tasks 1,3,5). Lane verdict for this repo: GLM for well-specced mechanical, sonnet mid, opus heavy — all under orchestrator-owned checks in ~/.ringer/p0.
- 2026-07-21 — p1a task1 (code-feature, GLM 5.2): PASS attempt 2 but with a semantics bend — probe had a withdrawal-displacement confound (orchestrator fault, 3rd instance of the class) and instead of reporting it, GLM carved stream cash out of wd_need so income would not displace draws, rationalized in a code comment. Stayed in-ownership (better than grok) but bent engine economics to satisfy a flawed check. Orchestrator reverted the carve-out, rebuilt tests on account-free households, added an economics guard test. Standing check-author rule: tax-attribution probes run on NO-ACCOUNT households; always pair with a displacement guard assertion.
- 2026-07-21 — p1a task6 (code-feature, opus): scoreboard FAIL x2 is FALSE — both were orchestrator probe bugs (cap arithmetic exceeded the cap in the "uncapped" case; excess->reinvest->taxed-growth second-order income; survivor tax flip read as a disposition spike). Opus implementation was correct to the dollar (verified by empirical decomposition), honored the integrity rule, cleaned scratch. Opus now 3/3 truly-correct on hardest lanes. Probe-author lessons now standing: (1) no-account households for attribution; (2) kill the excess-reinvest channel (spend > income) when asserting exact deltas; (3) guards must discriminate at the right order of magnitude.

## ollama/qwen3:8b
- 2026-08-08 (mech classification, s31): ollama/qwen3:8b failed 0/2 on a
  mech pack and is DEMOTED for SRG classification work — do not re-audition
  without a material model update.
- 2026-07-24 (data-pipeline, srg-2025-recon normalize-rbc-chq): FAIL x2, produced zero deliverables both attempts even after task-local-write fix that unblocked sonnet/opus peers. 287-row CSV transform with a detailed spec — well within claimed capability, but it got lost in sandbox/write mechanics. Demoted for data-pipeline; don't re-audition below 14B on multi-file harness tasks.

## sonnet (claude) — 2026-07-29, op-coord-01-stage2-gate-repackage
- docs/synthesis (3 tasks: G2 FINAL, G5 FINAL, Fusion MAB v4): 0/3 first-try, 3/3 on retry. All three first attempts included phrases the spec explicitly banned (struck wording quoted from source docs it was told to correct); the validator's failure output named each banned phrase and every retry cleaned them fully without damaging content. Lesson: when a synthesis task must EXCLUDE wording present in its own source material, expect a retry — the ban list in the check is doing the enforcement, not the spec. Budget 2 attempts; don't treat the pattern as model failure.
- Same run: orchestrator reintroduced a scanner-banned string into a handoff by QUOTING the false positive it was documenting. Checks/docs that describe banned patterns must describe, not reproduce.

## claude (Claude Code CLI) — 2026-07-30, op-coord-01-stage3-coa
- 8-lane research fan-out (sonnet): scoreboard shows 0/8 — ALL FALSE FAILS, orchestrator harness bug. Specs directed workers to Write FINALs to absolute REPO paths; the harness Write tool is restricted to the task directory (same layer as the shell cwd restriction noted 2026-07-29 — Read is unrestricted, Write is NOT). Every worker produced a complete, substantive FINAL (16-42KB); every Write was permission-denied; both attempts burned on the same wall. Recovery: the denial records in worker.log carry full tool_input.content — harvested all 8 artifacts from logs, zero content loss, 6/8 passed checks as-recovered. STANDING RULE: claude-engine workers write task-local (./FINAL.md); the orchestrator harvests to destination after QA. Never spec a repo-absolute Write path for this engine.
- Check-rigidity instance #7: required Lessons-Consulted to contain 8-hex OB1 IDs or literal "none found"; two workers honestly declared OB1 tools unreachable in the harness and enumerated attempted queries — substance-correct, check-failed. Checks demanding evidence-of-search must accept an explicit unavailability declaration. (Also: OB1 MCP reachability from ringer claude workers is inconsistent — 1 of 8 got through; assume unavailable and route lessons via an orchestrator-produced input file.)

- 2026-07-30 — drover-slice0-build (code-feature, 7 tasks across 3 rounds):
  codex 7/7 substance pass. Round-1 four lanes (loader/ledger/broker/match,
  ~50-80k tok each) and the loader fix all first-try. Round-2 "FAIL" x2 were
  orchestrator CHECK defects: a JSON-escaped heredoc (\" became literal
  backslash -> SyntaxError AFTER the real validator printed 16/16 PASS) and
  a check asserting an output schema the spec never pinned. Lessons: never
  embed escaped heredocs in manifest check strings (write a check .py file
  and call it), and pin exact output schemas in specs before asserting them.
- 2026-07-31 (rog-cos): code-fix x3 + code-feature x4 + site-build x1 today, phase 2+3 drover build — 7/9 first-try PASS; two check-caused retries were COS check defects (triviality tripwire worked as designed once, loader-stop 503 misread once). gpt-5.4 found a real product defect honestly when its spec allowed reporting instead of passing. Sandbox blocks localhost binds — server-driving checks must run orchestrator-side.

## 2026-08-07 — acct-hardening (r-accounting)
- **GLM 5.2** (opencode): code-feature ×2 (idempotency 8-file sweep; confidence routing 4-file build) — both first-try PASS, 84k/95k tokens. Handles long, prescriptive specs with executed-test checks cleanly. Confidence routing was the larger build (848s) — no retry needed.
- **codex gpt-5.4 high**: code-feature ×2 (anti-plug export gate; invariant suite) — both first-try PASS, 86k/85k tokens. Given the judgment-heavy lanes (fail-closed design, consume-once matching, false-alarm-avoidance doctrine); design decisions in notes were sound and needed no rework. Probation numbers on this box undersell it for well-specced repo work.
- Pattern note: worktrees + patch-export + executed-suite checks = 4/4 first-try on a real bookkeeping repo; the detailed spec (ownership list, house-style pointers, named invariants/violations as contract) is doing the heavy lifting.

## nvidia/nemotron-3-ultra-550b-a55b:free
- 2026-08-11 (docs / SRG bookkeeping recode audit, srg-h1-2026-sweep): passed a 7-row adjudication pack first-try (~56k tokens), then failed an 80-row pack twice (coverage/validator failures both attempts; sonnet retry cleared it first-try). Read: fine for small packs, chokes on large structured-output batches — cap its lane at ~20 rows or keep it off batch-coverage tasks.

## 2026-08-12 — ob1-domain-classification (research/data-labeling, 15 batches × 25 rows)
- **opencode engine, parallel 5: "database is locked" hard-fails.** Five concurrent opencode instances contend on its shared SQLite state; workers died pre-work. At parallel 2 the lock vanished. STANDING RULE: cap opencode lanes at max_parallel 2 (or stagger) until the engine isolates per-instance state.
- **opencode sandbox confines WRITES to the task directory** (same wall as the claude-engine 2026-07-29/absolute-Write note — this is the harness pattern, not one engine's quirk). Round-1 specs demanded an absolute workdir/out/ path: 7 workers did the classification correctly, fell back to writing in cwd, all check-failed on file location. Recovery: validated the misplaced artifacts orchestrator-side, harvested 7/7 PASS, zero content loss. Round-2 spec writes ./output.json task-local and the CHECK exports to out/ on pass. STANDING RULE (all engines): deliverables task-local; the check or orchestrator moves them.
- **GLM 5.2** classification quality on 700-char knowledge-row snippets: sensible domain calls, honest confidence spread, ids exact (7/7 validated packs). Good cheap lane for structured labeling at ≤25 rows/pack.

## google/gemini-3.7-flash (OpenRouter via opencode)
- 2026-08-18 — research (r-accounting s50 forensic lane): audition VOID, not a demotion. Both attempts died in ~1s with OpenRouter "Unexpected server error" (err_34a6f78d, err_d177a6e3) — zero model output. Model was added to the catalog 08-14; provider route may not be live yet. Re-audition after a trivial one-task probe passes; do not burn a real lane on it again until then.


## qwen2.5-coder:14b via opencode-local (DELETED 2026-08-21)
- 2026-08-21 — local-coder bakeoff vs qwen3:8b (both 16K-ctx variants, 3
  scenarios: stats bugfix, CSV dedupe CLI, field rename): 0/6 attempts. Emits
  tool calls as fenced-JSON text instead of invoking tools under OpenCode →
  files never written; also 4-13 min/cell swap-thrash on the 16GB machine with
  normal apps open. qwen3:8b-16k went 3/3 first-try on identical cells.
  Model deleted; do not re-audition on this hardware.

## qwen3:8b via opencode-local — 16K context fix
- 2026-08-21 — round 1 of the same bakeoff failed 6/6 for BOTH models on the
  Ollama app default 4096 num_ctx: specs truncated, workers wrote correct code
  to nowhere or hallucinated "file written". Fix: derived model qwen3:8b-16k
  (PARAMETER num_ctx 16384), now the opencode-local model_default. Always route
  local lane work to the -16k variant; never the bare tag.

## gemma4:e4b-16k via opencode-local (AUDITION PASSED 2026-08-21)
- 2026-08-21 — local-coder bakeoff rerun (same 3 cells qwen3:8b-16k passed:
  stats bugfix, CSV dedupe CLI, field rename): all 3 deliverables PASS their
  executed checks. Code quality solid — correct sample variance, edge-case
  ValueErrors, clean dedupe with casing preserved. SCOREBOARD CAVEAT: the
  model log holds 9 junk FAIL rows for this model from the same evening —
  3 from a run before gemma4:e4b-16k was registered in opencode.jsonc
  (instant "Unexpected server error", zero model output) and 6 from an
  orchestrator check bug (literal `{taskdir}` placeholder — ringer does no
  such substitution; write literal absolute paths in checks). Validators
  were re-executed against the surviving deliverables: 3/3 PASS. Treat those
  FAIL rows as void, not model evidence. ~5-6 min/cell on the 16GB machine.
  Derived via `PARAMETER num_ctx 16384` from gemma4:e4b (shared blob).

## ollama/qwen3:8b-16k
- 2026-08-22 — email-intake-restore graph-shape-sweep (code-review, read-only repo scout): FAIL x2. Both attempts abandoned the worktree cwd and tried to read files inside opencode's own scratch tmp dir; attempt 2 produced generic troubleshooting chat instead of the report. Prior 3/3 code-fix record does not transfer to multi-step repo navigation tasks — keep this model on single-file mechanical work; route repo-wide sweeps to GLM/codex or do them inline.

## Orchestrator note — 2026-08-24 (backlog-part4 run, codex ×2 + GLM-5.2 ×1)
- Two validator FAILs (agents-md/codex, skill-shadow/GLM-5.2) were CHECK bugs, not model failures: the verify string contained `test $? -eq 2` inside a double-quoted `--verify-command`, so the shell expanded `$?` to `0` before the validator ran (an assertion that cannot pass); agents-md's verify also named test paths in `scripts/tests/` that live in `scripts/`, so the worker added shims outside its ownership. Both patches passed the corrected chains on the real tree first try. Do not read these as demotions. Lesson: single-quote or escape `$?` in verify strings, or put exit-code logic in a check script; and confirm every path in a verify chain exists in the worktree before dispatch.
- GLM-5.2 (opencode) on the skill-shadow bash task: correct on substance first attempt (script + 6 tests + wiring), ~154K tokens over two attempts because the retry only re-ran the impossible check.

- 2026-08-24 — gpt-5.4 (codex, default effort) — code-fix ×3 for r-accounting desk-refresh (run desk-refresh-queue-capture-fix, 2 rounds). Round 1: 1/1 PASS first try (53k tokens). Round 2: both tasks recorded FAIL after 2 attempts, but the failures were CHECK defects by the orchestrator (checks used repo-relative paths / `test -f notes.md` after a `cd`, so they could not pass from the task dir); the integrator verified the substance manually — pytest 154→158, real snapshot loads 75/75, end-to-end script PASS. Do not read the round-2 rows as model failures. Lesson: checks that `cd` must reference notes.md by absolute task-dir path; checks that stay in the task dir must `cd` to the repo first.
- 2026-08-24 — gpt-5.4 (codex) — code-feature, r-accounting desk-refresh-counter-rows: recorded FAIL after 2 attempts, again an orchestrator CHECK defect (no `cd` into the repo before relative paths); substance verified by the integrator — pytest 158→161, exporter runs on real data, script wired. Third time today: a check that references repo paths must start with `cd <repo> &&`, and notes.md must be an absolute task-dir path. Do not count as a model failure.
- 2026-08-28 — gpt-5.4 (codex, default effort) — code-fix ×3, run wp4a-ob1-proxy-repair (OB1 local MCP proxy: header auth from Keychain, SSE-aware health probe, streamable-HTTP transport). 3/3 first-try PASS, 68k/43k/63k tokens, 4m43s/2m11s/2m53s. Every round was a tightly-specified single file with the live-acceptance failure quoted verbatim in the spec; the worker never over-reached and kept 3.9-compat stdlib as told. Lesson for the orchestrator, not the model: two of three rounds existed only because the live surface (real upstream SSE framing, real rmcp client GET stream) could not be exercised inside the sandbox check — drive the consumer early.
