import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OPTIONS = {
 '1': ('原版三步流程（離線改編）', ['-m', 'lab.graph_lab', '--baseline']),
 '2': ('新增反思與重試', ['-m', 'lab.graph_lab']),
 '3': ('搜尋暫時失敗，第二次恢復', ['-m', 'lab.graph_lab', '--scenario', 'transient']),
 '4': ('搜尋持續失敗，停止並求助', ['-m', 'lab.graph_lab', '--scenario', 'failure']),
 '5': ('AutoGen 團隊：QA 抓錯與修正', ['-m', 'lab.team_lab']),
 '6': ('AutoGen 一直不修正：上限停止', ['-m', 'lab.team_lab', '--no-repair']),
 '7': ('完整環境驗證', ['scripts/verify_environment.py']),
 '8': ('檢查同學的條件邊練習', ['scripts/check_exercise.py']),
}
while True:
    print('\nHello Agents CH6 | 免 API key | 真實框架 + 固定資料')
    for key, (label, _) in OPTIONS.items():
        print(f'{key}. {label}')
    print('q. 離開')
    try:
        choice = input('請輸入選項：').strip().lower()
    except (EOFError, KeyboardInterrupt):
        break
    if choice == 'q':
        break
    if choice not in OPTIONS:
        print('請輸入 1-8 或 q。')
        continue
    args = OPTIONS[choice][1]
    print('COMMAND: python ' + ' '.join(args), flush=True)
    result = subprocess.run([sys.executable, '-X', 'utf8', *args], cwd=ROOT)
    if result.returncode:
        print(f'程式回傳 {result.returncode}；請看上方訊息。')
