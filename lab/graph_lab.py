"""Adapted from Hello-Agents ch6 Langgraph/Dialogue_System.py.
Real LangGraph orchestration; deterministic local retrieval and extractive answers.
"""
import argparse
import json
import operator
from pathlib import Path
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from . import settings

ROOT = Path(__file__).resolve().parents[1]

class SearchState(TypedDict):
    question: str
    search_query: str
    search_results: list[dict]
    final_answer: str
    citations: list[str]
    attempts: int
    min_sources: int
    max_retries: int
    scenario: str
    status: str
    feedback: str
    error: str
    trace: Annotated[list[str], operator.add]

def understand_query_node(state: SearchState) -> dict:
    # 固定關鍵字規則；這不是 LLM 理解能力。
    text = state['question'].lower()
    topic = 'langgraph' if any(w in text for w in ['langgraph', '狀態', '状态', '條件邊', '条件边']) else 'unknown'
    return {'search_query': topic, 'trace': ['understand']}

def local_search_node(state: SearchState) -> dict:
    attempt = state['attempts'] + 1
    fails = state['scenario'] == 'failure' or (state['scenario'] == 'transient' and attempt == 1)
    if fails:
        return {'search_results': [], 'attempts': attempt, 'error': 'InjectedSearchError', 'trace': [f'search#{attempt}:error']}
    documents = json.loads((ROOT / 'data/knowledge.json').read_text(encoding='utf-8'))
    matches = [d for d in documents if d['topic'] == state['search_query']]
    # 第一輪刻意只取一筆；反思後擴大檢索。這是可重現的實驗設定。
    count = 1 if attempt == 1 else state['min_sources']
    found = matches[:count]
    return {'search_results': found, 'attempts': attempt, 'error': '', 'trace': [f'search#{attempt}:hits={len(found)}']}

def generate_answer_node(state: SearchState) -> dict:
    docs = state['search_results']
    if not docs:
        answer = '目前沒有可用的教材證據，無法回答；請檢查資料或工具。'
    else:
        answer = '\n'.join(f"{d['text']} [{d['id']}]" for d in docs)
    return {'final_answer': answer, 'citations': [d['id'] for d in docs], 'trace': ['answer']}

def reflect_node(state: SearchState) -> dict:
    # 結構化來源 ID 必須來自這次檢索且真的出現在答案中。
    valid_ids = {d['id'] for d in state['search_results'] if f"[{d['id']}]" in state['final_answer']}
    cited_ids = set(state['citations']) & valid_ids
    passed = not state['error'] and len(cited_ids) >= state['min_sources']
    retry = state['attempts'] < 1 + state['max_retries']
    status = 'pass' if passed else ('retry' if retry else 'needs_help')
    reason = f"sources={len(cited_ids)}/{state['min_sources']}; attempts={state['attempts']}; status={status}"
    return {'status': status, 'feedback': reason, 'trace': [f'reflect:{status}']}

def route_after_reflection(state: SearchState) -> str:
    return 'search' if state['status'] == 'retry' else 'end'

def create_search_assistant(baseline: bool = False):
    workflow = StateGraph(SearchState)
    workflow.add_node('understand', understand_query_node)
    workflow.add_node('search', local_search_node)
    workflow.add_node('answer', generate_answer_node)
    workflow.add_edge(START, 'understand')
    workflow.add_edge('understand', 'search')
    workflow.add_edge('search', 'answer')
    if baseline:
        workflow.add_edge('answer', END)
    else:
        workflow.add_node('reflect', reflect_node)
        workflow.add_edge('answer', 'reflect')
        workflow.add_conditional_edges('reflect', route_after_reflection, {'search': 'search', 'end': END})
    return workflow.compile()

def run_case(question='LangGraph 的 State、Node、Edge 是什麼？', *, baseline=False,
             scenario='normal', min_sources=None, max_retries=None):
    min_sources = settings.MIN_SOURCES if min_sources is None else min_sources
    max_retries = settings.MAX_RETRIES if max_retries is None else max_retries
    if not question.strip():
        raise ValueError('question must not be empty')
    if not 1 <= min_sources <= 10 or not 0 <= max_retries <= 5:
        raise ValueError('min_sources: 1..10; max_retries: 0..5')
    if scenario not in {'normal', 'transient', 'failure'}:
        raise ValueError('unknown scenario')
    initial = dict(question=question, search_query='', search_results=[], final_answer='',
                   citations=[], attempts=0, min_sources=min_sources, max_retries=max_retries,
                   scenario=scenario, status='unreviewed', feedback='', error='', trace=[])
    return create_search_assistant(baseline).invoke(initial, {'recursion_limit': 32})

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--scenario', choices=['normal', 'transient', 'failure'], default='normal')
    parser.add_argument('--question', default='LangGraph 的 State、Node、Edge 是什麼？')
    parser.add_argument('--min-sources', type=int, default=settings.MIN_SOURCES)
    parser.add_argument('--max-retries', type=int, default=settings.MAX_RETRIES)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run_case(args.question, baseline=args.baseline, scenario=args.scenario,
                      min_sources=args.min_sources, max_retries=args.max_retries)
    print('MODE: OFFLINE / REAL LangGraph / NO LLM API')
    print('TRACE: ' + ' -> '.join(result['trace']))
    print(f"RESULT: {result['status']} | attempts={result['attempts']} | sources={len(result['citations'])}")
    print(result['final_answer'])
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
