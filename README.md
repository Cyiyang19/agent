# Agent：Hello Agents 第六章與學習實驗

**30–60 分鐘課堂分享＋免 API key 實驗。** 教材範圍：Hello-Agents V1.0.2（2026-02-10）第六章；補充第 1–5 章先備知識，最後銜接第七章。

獨立專案：[Cyiyang19/agent](https://github.com/Cyiyang19/agent)。下載後直接在 repository 根目錄執行。

## 先從這裡開始

- **自己的學習路線：** [理解 → 預測 → 修改 → 驗證](docs/09_自己的學習框架.md)

- **報告者先讀：** [最簡單上手教學](docs/05_最簡單教會你.md)
- **上課講義：** [CH6 完整講義](docs/01_CH6講義.md)
- **同學操作：** [實驗單與繳交內容](docs/02_同學實驗單.md)
- **上台使用：** [30／45／60 分鐘講者稿](docs/04_講者稿與時間表.md)
- **第六章章末題：** [六題完整解答與流程圖](docs/10_CH6章末六題解答.md)
- [前五章速讀](docs/00_前五章速讀.md) · [教師解答](docs/03_教師解答.md) · [修改對照](docs/07_修改對照與來源.md) · [排錯](docs/06_環境與排錯.md)

## 一鍵操作（Windows）

1. 第一次：安裝 **Python 3.12**，勾選 Add python.exe to PATH，雙擊 **setup.cmd**。安裝需要網路；跑實驗不需要。
2. 看到 **PASS: CH6 offline framework lab verified end-to-end.** 才算環境成功。
3. 雙擊 **demo.cmd**，依序選 **1 → 2 → 4 → 5**。

本機已建立隔離的 .venv。換電腦仍必須執行 setup.cmd，不能複製 .venv。

## 終端機操作

在本資料夾開啟終端機；建立環境後不必 activate：

~~~powershell
.\.venv\Scripts\python.exe -X utf8 -m lab.graph_lab --baseline
.\.venv\Scripts\python.exe -X utf8 -m lab.graph_lab
.\.venv\Scripts\python.exe -X utf8 -m lab.graph_lab --scenario failure
.\.venv\Scripts\python.exe -X utf8 -m lab.team_lab
.\.venv\Scripts\python.exe -X utf8 scripts/verify_environment.py
~~~

macOS／Linux（指令已提供；本機驗證平台是 Windows）：

~~~bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python scripts/verify_environment.py
.venv/bin/python scripts/demo_menu.py
~~~

## 我們真的驗證了什麼？

| 項目 | 狀態與界線 |
|---|---|
| LangGraph 1.2.11 | 真正執行 StateGraph、節點、條件邊、有限重試 |
| AutoGen 0.7.4 | 真正執行 AssistantAgent、RoundRobinGroupChat、ReplayChatCompletionClient、QA 與停止條件 |
| LLM | **未呼叫、未驗證。** 固定資料／回覆替身不代表模型推理能力 |
| AgentScope／CAMEL | 本次講解設計與案例；**沒有安裝或聲稱跑通這兩個框架** |
| 網頁搜尋 | 使用本地兩筆教材摘要；**沒有連接 Tavily、不是即時網搜** |
| 測試 | 16 項自動測試；外部網路連線遭測試攔截，允許 Windows asyncio 所需的本機 loopback |

[驗證報告](outputs/environment_report.json) 記錄時間、版本與實際結果；[pytest 輸出](outputs/pytest.txt) 保留測試證據。failure／needs_help 是刻意失敗情境的預期結果，不能與環境驗證失敗混淆。

## 作業交付對照

| 老師要求 | 本專案對應 |
|---|---|
| 修改 existing codes | 保留兩個 upstream 原檔，改編三步搜尋與軟體團隊；附修改表與 diff |
| Prepare lab for other teams | 實驗單、學生待改程式、檢查器、驗收表、教師答案 |
| Markdown lecture notes | 前置知識、完整講義、講者稿、排錯與自學指引 |
| Demonstrate code | 免金鑰選單、成功／重試／持續失敗／真實 QA 示範 |
| Record and share | **依本人最新指示，這次改為現場 demo，未製作影片。** 若老師仍要求錄影，須課堂錄製後補交 |
| 第七章 | 提供銜接解說；不取代另一組的 CH7 工作 |

## 來源與授權

改編自 [Datawhale Hello-Agents](https://github.com/datawhalechina/hello-agents)，保留作者歸屬與 [CC BY-NC-SA 4.0](LICENSE.txt)。原始檔與版本鎖定見 [來源與修改說明](docs/07_修改對照與來源.md)。本專案使用 AI 協助整理與改編，報告者需理解並自行完成課堂說明。
