"""AutoGen dynamic rollback: changed requirements return to ProductManager.

All AssistantAgent replies are fixed fixtures. The selector and QA tests really run.
"""
import asyncio
import json
from pathlib import Path
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_ext.models.replay import ReplayChatCompletionClient
from .team_lab import QualityAssurance


def next_speaker(messages):
    """Choose the next role from the last message, independent of an LLM."""
    latest = messages[-1]
    if latest.source == 'user':
        return 'ProductManager'
    if latest.source == 'ProductManager':
        return 'Engineer'
    if latest.source == 'Engineer':
        return 'CodeReviewer'
    if latest.source == 'CodeReviewer':
        if latest.content.startswith('REQUIREMENTS_CHANGED:'):
            return 'ProductManager'
        if latest.content.startswith('REVIEW_PASS:'):
            return 'QualityAssurance'
        return 'Engineer'
    if latest.source == 'QualityAssurance':
        return 'Engineer' if latest.content.startswith('QA_FAIL:') else 'ProductManager'
    raise ValueError(f'Unexpected speaker: {latest.source}')


async def run_dynamic_team():
    clients = []

    def role(name, replies, system_message):
        client = ReplayChatCompletionClient(replies)
        clients.append(client)
        return AssistantAgent(name, model_client=client, system_message=system_message)

    pm = role('ProductManager', [
        'SPEC_APPROVED:v1; target: 1000 W x 2 h = 2 kWh.',
        'SPEC_APPROVED:v2; target unchanged; reject negative inputs.'
    ], 'Confirm the active requirements version before implementation.')
    engineer = role('Engineer', [
        '{"implementation":"buggy","spec_version":1}',
        '{"implementation":"fixed","spec_version":2}'
    ], 'Choose only an allowlisted candidate; include the requirements version.')
    reviewer = role('CodeReviewer', [
        'REQUIREMENTS_CHANGED:v2; reject negative inputs. ProductManager must reapprove.',
        'REVIEW_PASS:v2; send the candidate to QualityAssurance.'
    ], 'Check changes in requirements and route them for approval.')
    selector_client = ReplayChatCompletionClient(['ProductManager'])
    clients.append(selector_client)
    team = SelectorGroupChat(
        [pm, engineer, reviewer, QualityAssurance()],
        model_client=selector_client,
        selector_func=next_speaker,
        termination_condition=(TextMentionTermination('TERMINATE', sources=['QualityAssurance'])
                               | MaxMessageTermination(12)),
        max_turns=8,
    )
    try:
        result = await team.run(task='Build an energy calculator.')
        messages = [{'source': m.source, 'content': m.content}
                    for m in result.messages if isinstance(m, TextMessage)]
        passed = any(m['source'] == 'QualityAssurance' and m['content'].startswith('QA_PASS:')
                     for m in messages)
        return {'status': 'pass' if passed else 'needs_help',
                'stop_reason': result.stop_reason, 'messages': messages,
                'mode': 'AutoGen SelectorGroupChat + deterministic selector + real QA'}
    finally:
        for client in clients:
            await client.close()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = asyncio.run(run_dynamic_team())
    for message in result['messages']:
        print(f"{message['source']}: {message['content']}")
    print('RESULT:', result['status'])
    print('STOP:', result['stop_reason'])
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
