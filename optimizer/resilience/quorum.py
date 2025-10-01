from __future__ import annotations
from typing import Callable, NamedTuple, List

class ValidationResult(NamedTuple):
    passed: bool
    witnesses: int
    details: list[str]

Validator = Callable[[str], bool]

def prefix_validator(prefix: str) -> Validator:
    def f(text: str) -> bool:
        return text.strip().startswith(prefix)
    return f

def validate(output: str, threshold: int, validators: List[Validator]) -> ValidationResult:
    witnesses = 0
    details = []
    for i, v in enumerate(validators):
        try:
            if v(output):
                witnesses += 1
                details.append(f"Validator {i} passed.")
            else:
                details.append(f"Validator {i} failed.")
        except Exception as e:
            details.append(f"Validator {i} raised an exception: {e}")

    passed = witnesses >= threshold
    return ValidationResult(passed=passed, witnesses=witnesses, details=details)