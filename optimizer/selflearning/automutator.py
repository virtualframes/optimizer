from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import time, hashlib, json, pathlib, subprocess
from git import Repo
from optimizer.self_rewrite.ast_tools import AddLogEnter, apply_transformers
from optimizer.self_rewrite.sandbox_runner import run_pytest_sandbox

AUDIT = pathlib.Path("audit"); AUDIT.mkdir(exist_ok=True)
EVENTS = AUDIT / "events.jsonl"
MUTS   = AUDIT / "mutations.jsonl"

@dataclass
class Evidence:
    kind: str                     # "trace", "coverage", "latency", "risk"
    payload: Dict

@dataclass
class MutationPlan:
    id: str
    kind: str                     # "bugfix" | "refactor" | "test_add" | "feature_seed"
    targets: List[str]            # file paths
    transforms: List[str]         # names of AST transformers or patch steps
    tests_hint: Optional[str] = None

@dataclass
class MutationResult:
    plan_id: str
    ok: bool
    sandbox_rc: int
    delta_metrics: Dict
    stdout_tail: str
    stderr_tail: str

class AutoMutator:
    def __init__(self, repo_dir=".", repo_branch="main"):
        self.repo = Repo(repo_dir)
        self.repo_dir = repo_dir
        self.branch = repo_branch

    # --- signal intake stubs (extend with journald/coverage parsers) ---
    def collect_signals(self) -> List[Evidence]:
        evs = []
        # 1) pytest cache / last failure file
        # 2) audit/availability.csv spikes
        # 3) audit/risk_index.jsonl newest items
        # Implement readers here; return structured Evidence list
        return evs

    def triage(self, evs: List[Evidence]) -> MutationPlan:
        ts = int(time.time())
        # Simple rule: if any error trace → bugfix; else if latency spike → refactor; else feature_seed
        kind = "bugfix" if any(e.kind=="trace" for e in evs) else "refactor"
        return MutationPlan(id=f"mut_{ts}", kind=kind, targets=["self_rewrite/ast_tools.py"],
                            transforms=["AddLogEnter"])

    def realize(self, plan: MutationPlan) -> MutationResult:
        # Apply AST transforms in-memory then sandbox
        # For demo: only AddLogEnter on first target
        res = apply_transformers(plan.targets[0])
        sb = run_pytest_sandbox(self.repo_dir)
        ok = (sb["returncode"] == 0)
        return MutationResult(plan_id=plan.id, ok=ok, sandbox_rc=sb["returncode"],
                              delta_metrics={"tests_pass": ok}, stdout_tail=sb["stdout"], stderr_tail=sb["stderr"])

    def commit_if_green(self, plan: MutationPlan, result: MutationResult):
        if not result.ok: return False
        try:
            self.repo.git.add(all=True)
            msg = f"auto(mut): {plan.kind} {plan.targets} plan={plan.id}"
            self.repo.index.commit(msg)
            self.emit_event("mutation_committed", {"plan": asdict(plan), "result": asdict(result)})
            self.append_jsonl(MUTS, {"ts": time.time(), "plan": asdict(plan), "result": asdict(result)})
            return True
        except Exception as e:
            print(f"Git commit failed: {e}")
            return False

    # --- helpers ---
    def emit_event(self, name: str, payload: Dict):
        self.append_jsonl(EVENTS, {"ts": time.time(), "event": name, "payload": payload})

    @staticmethod
    def append_jsonl(path: pathlib.Path, obj: Dict):
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj) + "\n")

def main():
    am = AutoMutator()
    evs = am.collect_signals()
    plan = am.triage(evs)
    res  = am.realize(plan)
    am.commit_if_green(plan, res)

if __name__ == "__main__":
    main()