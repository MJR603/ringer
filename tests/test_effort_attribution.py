#!/usr/bin/env python3
"""Reasoning-effort and model attribution on logged attempt rows.

Exercises RingerRunner._log_attempt directly (the real row-building path),
not a reimplementation of it. See docs/TAXONOMY.md: Ringer records only
explicit effort values and never guesses a harness-side default.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ringer import (  # noqa: E402
    AppConfig,
    ArtifactConfig,
    EngineConfig,
    EvalConfig,
    Manifest,
    RingerRunner,
    VerifyResult,
    WorkerResult,
)

LONG_SPEC = (
    "Create the requested artifact in the current working directory, keep the change scoped, "
    "and make the check command able to explain any failure clearly."
)
GOOD_CHECK = (
    "test -s output.txt && grep -q 'ready' output.txt || "
    "{ echo 'FAIL: output.txt missing or does not contain ready'; exit 1; }"
)


def codex_engine(**overrides: object) -> EngineConfig:
    fields: dict[str, object] = dict(
        name="codex",
        bin="/usr/local/bin/codex",
        args_template=("exec", "{engine_args}", "{model_args}", "{spec}"),
        full_access_args=(),
        sandbox_args=(),
        token_regex=None,
    )
    fields.update(overrides)
    return EngineConfig(**fields)  # type: ignore[arg-type]


class EffortAttributionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def config(self, engines: dict[str, EngineConfig]) -> AppConfig:
        return AppConfig(
            path=None,
            identity_default=None,
            state_dir=self.root / "state",
            dashboard_port_base=8787,
            hud_port=8700,
            hud_app_path=None,
            allow_full_access=False,
            eval=EvalConfig(backend="jsonl", jsonl_path=self.root / "eval.jsonl"),
            engines=engines,
            artifact=ArtifactConfig(
                enabled=False,
                out_template=str(self.root / "live.html"),
                report_template=str(self.root / "report.html"),
                index_out=self.root / "index.html",
            ),
        )

    def task_obj(self, **extra: object) -> dict[str, object]:
        task: dict[str, object] = {
            "key": "a",
            "spec": LONG_SPEC,
            "check": GOOD_CHECK,
            "engine": "codex",
            "expect_files": ["output.txt"],
            "verified": "output exists with expected content",
        }
        task.update(extra)
        return task

    def run_and_log(
        self,
        *,
        engines: dict[str, EngineConfig],
        task: dict[str, object],
        last_worker_command: list[str],
    ) -> dict[str, object]:
        manifest = Manifest.from_obj(
            {
                "run_name": "effort-attribution",
                "workdir": str(self.root / "work"),
                "tasks": [task],
            }
        )
        runner = RingerRunner(
            manifest,
            config=self.config(engines),
            identity="tester",
            dashboard_enabled=False,
        )
        runtime = runner.runtimes[0]
        runtime.last_worker_command = last_worker_command
        runner._log_attempt(
            runtime,
            runtime.task.spec,
            False,
            WorkerResult(returncode=0, timed_out=False, tokens=10),
            VerifyResult(ok=True, check_returncode=0, check_timed_out=False, raw_output_excerpt="ok"),
            "PASS",
            10,
        )
        return json.loads((self.root / "eval.jsonl").read_text(encoding="utf-8"))

    def test_codex_engine_args_high_effort_is_recorded(self) -> None:
        payload = self.run_and_log(
            engines={"codex": codex_engine(model_default="gpt-5.5")},
            task=self.task_obj(engine_args=["-c", "model_reasoning_effort=high"]),
            last_worker_command=[
                "codex", "exec", "-c", "model_reasoning_effort=high", "-m", "gpt-5.5", LONG_SPEC,
            ],
        )
        self.assertEqual("high", payload["reasoning_effort"])

    def test_no_effort_anywhere_is_null(self) -> None:
        payload = self.run_and_log(
            engines={"codex": codex_engine(model_default="gpt-5.5")},
            task=self.task_obj(),
            last_worker_command=["codex", "exec", "-m", "gpt-5.5", LONG_SPEC],
        )
        self.assertIsNone(payload["reasoning_effort"])

    def test_model_resolved_from_engine_default_when_task_has_none(self) -> None:
        payload = self.run_and_log(
            engines={"codex": codex_engine(model_default="gpt-5.5")},
            task=self.task_obj(),
            last_worker_command=["codex", "exec", "-m", "gpt-5.5", LONG_SPEC],
        )
        self.assertEqual("gpt-5.5", payload["model"])

    def test_opencode_variant_flag_is_recorded_as_effort(self) -> None:
        opencode = EngineConfig(
            name="opencode",
            bin="/usr/local/bin/opencode",
            args_template=("run", "-m", "{model}", "{engine_args}", "{spec}"),
            full_access_args=(),
            sandbox_args=(),
            token_regex=None,
            model_default="openrouter/z-ai/glm-5.2",
        )
        payload = self.run_and_log(
            engines={"opencode": opencode},
            task=self.task_obj(engine="opencode", engine_args=["--variant", "high"]),
            last_worker_command=[
                "opencode", "run", "-m", "openrouter/z-ai/glm-5.2", "--variant", "high", LONG_SPEC,
            ],
        )
        self.assertEqual("high", payload["reasoning_effort"])

    def test_engine_configured_default_effort_fills_in_when_command_has_none(self) -> None:
        claude = EngineConfig(
            name="claude",
            bin="/usr/local/bin/claude",
            args_template=("--model", "{model}", "{engine_args}", "-p", "{spec}"),
            full_access_args=(),
            sandbox_args=(),
            token_regex=None,
            model_default="sonnet",
            reasoning_effort_default="high",
        )
        payload = self.run_and_log(
            engines={"claude": claude},
            task=self.task_obj(engine="claude"),
            last_worker_command=["claude", "--model", "sonnet", "-p", LONG_SPEC],
        )
        self.assertEqual("high", payload["reasoning_effort"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
