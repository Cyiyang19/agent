import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from exercises.student_policy import choose_next
cases = [('retry', 'search'), ('pass', 'end'), ('needs_help', 'end')]
failed = 0
for state, expected in cases:
    actual = choose_next(state)
    good = actual == expected
    failed += not good
    print(f"{'PASS' if good else 'FAIL'}: {state} -> {actual}; expected {expected}")
print('PASS: student routing policy' if not failed else 'Exercise unfinished: edit exercises/student_policy.py')
raise SystemExit(bool(failed))
