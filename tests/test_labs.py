import asyncio
import pytest
from lab.graph_lab import run_case
from lab.team_lab import run_team
from lab.energy import check_candidate

def test_baseline_has_no_quality_gate():
    r = run_case(baseline=True)
    assert r['status'] == 'unreviewed'
    assert r['attempts'] == 1 and len(r['citations']) == 1

def test_reflection_retrieves_more_evidence():
    r = run_case(min_sources=2, max_retries=1)
    assert r['status'] == 'pass'
    assert r['attempts'] == 2 and len(r['citations']) == 2
    assert r['trace'].count('reflect:retry') == 1

def test_transient_failure_recovers():
    r = run_case(scenario='transient', min_sources=2, max_retries=1)
    assert 'search#1:error' in r['trace'] and r['status'] == 'pass'

@pytest.mark.parametrize('kwargs', [dict(scenario='failure'), dict(question='tomorrow weather'), dict(min_sources=3)])
def test_unanswerable_stops_without_false_success(kwargs):
    r = run_case(max_retries=1, **kwargs)
    assert r['status'] == 'needs_help' and r['attempts'] == 2

def test_retry_budget_zero():
    r = run_case(min_sources=2, max_retries=0)
    assert r['attempts'] == 1 and r['status'] == 'needs_help'

def test_relaxed_gate_changes_path():
    r = run_case(min_sources=1, max_retries=1)
    assert r['status'] == 'pass' and r['attempts'] == 1

@pytest.mark.parametrize('kwargs',[dict(question=' '),dict(min_sources=0),dict(max_retries=6)])
def test_bad_config_fails_fast(kwargs):
    with pytest.raises(ValueError):
        run_case(**kwargs)

def test_qa_detects_actual_bug():
    assert check_candidate('buggy')
    assert not check_candidate('fixed')
    assert check_candidate('untrusted-code')

def test_team_repair_executes_qa_twice():
    r = asyncio.run(run_team())
    qa = [m['content'] for m in r['messages'] if m['source'] == 'QualityAssurance']
    assert len(qa) == 2 and qa[0].startswith('QA_FAIL') and qa[1].startswith('QA_PASS')
    assert r['status'] == 'pass'

def test_team_never_repairs_stops_at_limit():
    r = asyncio.run(run_team(repair=False))
    assert r['status'] == 'needs_help'
    assert len(r['messages']) <= 9
    assert not any('QA_PASS' in m['content'] for m in r['messages'])


def test_fake_or_duplicate_citations_do_not_pass():
    from lab.graph_lab import reflect_node
    r = reflect_node(dict(search_results=[{'id':'real'}], final_answer='[fake]', citations=['fake','fake'],
                          error='', min_sources=2, attempts=2, max_retries=1))
    assert r['status'] == 'needs_help'


def test_duplicate_valid_citation_only_counts_once():
    from lab.graph_lab import reflect_node
    r = reflect_node(dict(search_results=[{'id':'real'}], final_answer='[real] [real]', citations=['real','real'],
                          error='', min_sources=2, attempts=2, max_retries=1))
    assert r['status'] == 'needs_help'
