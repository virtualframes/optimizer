from ..adapters.claude_adapter import ClaudeAdapter
from .patch_generator import synthesize_patch
from .merge_resolver import resolveconflicts
from .pr_drafter import createpatchpr

def autodebugandpatchcifailure(traceback: str, prbranch: str):
    diagnosis = ClaudeAdapter().diagnose_build_failure(traceback)
    patch = synthesize_patch(diagnosis)
    resolveconflicts(prbranch)
    return createpatchpr(patch, "fix: install g++ for pybullet build")