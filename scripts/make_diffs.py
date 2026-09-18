from pathlib import Path
import difflib
root = Path(__file__).resolve().parents[1]
for name, a, b in [('langgraph','upstream/Langgraph/Dialogue_System.py','lab/graph_lab.py'),('autogen','upstream/AutoGenDemo/autogen_software_team.py','lab/team_lab.py')]:
    lines = difflib.unified_diff((root/a).read_text(encoding='utf-8').splitlines(True), (root/b).read_text(encoding='utf-8').splitlines(True), fromfile=a, tofile=b)
    (root/'changes').mkdir(exist_ok=True)
    (root/f'changes/{name}.patch').write_text(''.join(lines),encoding='utf-8')
