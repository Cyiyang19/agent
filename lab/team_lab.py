"""Modified AutoGen software team: replace blocking UserProxy with actual QA.
ReplayChatCompletionClient supplies fixtures, NOT live model intelligence.
"""
import argparse
import asyncio
import json
from pathlib import Path
from autogen_agentchat.agents import AssistantAgent, BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_ext.models.replay import ReplayChatCompletionClient
from .energy import check_candidate

class QualityAssurance(BaseChatAgent):
    def __init__(self):
        super().__init__('QualityAssurance', 'Run real unit checks against allowlisted energy functions.')

    @property
    def produced_message_types(self):
        return (TextMessage,)

    async def on_reset(self, cancellation_token):
        pass

    async def on_messages(self, messages, cancellation_token):
        proposals = [m.content for m in messages if m.source == 'Engineer' and isinstance(m, TextMessage)]
        try:
            candidate = json.loads(proposals[-1])['implementation']
            failures = check_candidate(candidate)
        except (IndexError, KeyError, TypeError, json.JSONDecodeError):
            candidate, failures = 'invalid', ['missing or malformed candidate']
        if failures:
            text = 'QA_FAIL: ' + '; '.join(failures) + '. Engineer: select a corrected implementation.'
        else:
            text = f'QA_PASS: {candidate}; 5 executable checks passed. TERMINATE'
        return Response(chat_message=TextMessage(content=text, source=self.name))

async def run_team(repair=True):
    clients = []
    def agent(name, replies, prompt):
        client = ReplayChatCompletionClient(replies)
        clients.append(client)
        return AssistantAgent(name, model_client=client, system_message=prompt)
    manager = agent('ProductManager', ['Need W*h/1000 in kWh; reject negative inputs.',
                                      'Revise the candidate using the QA failure report.'],
                    'Define requirements and acceptance criteria.')
    engineer = agent('Engineer', ['{"implementation":"buggy"}',
                                 '{"implementation":"fixed"}' if repair else '{"implementation":"buggy"}'],
                     'Select an allowlisted candidate using JSON; never execute generated code.')
    reviewer = agent('CodeReviewer', ['Check units and negative inputs; let QA execute checks.',
                                    'The QA result, not this review, determines success.'],
                     'Review the proposed candidate; do not claim tests were executed.')
    termination = TextMentionTermination('TERMINATE', sources=['QualityAssurance']) | MaxMessageTermination(12)
    team = RoundRobinGroupChat([manager, engineer, reviewer, QualityAssurance()],
                              termination_condition=termination, max_turns=8)
    try:
        result = await team.run(task='Build an energy calculator; 1000 W for 2 h must equal 2 kWh.')
        messages = [{'source': m.source, 'content': m.content} for m in result.messages if isinstance(m, TextMessage)]
        passed = any(m['source'] == 'QualityAssurance' and m['content'].startswith('QA_PASS:') for m in messages)
        return {'mode': 'offline-replay / real AutoGen', 'status': 'pass' if passed else 'needs_help',
                'stop_reason': result.stop_reason, 'messages': messages}
    finally:
        for client in clients:
            await client.close()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--no-repair', action='store_true')
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    result = asyncio.run(run_team(repair=not args.no_repair))
    print('MODE: OFFLINE REPLAY / REAL AutoGen / NO LLM API')
    for m in result['messages']:
        print(f"{m['source']}: {m['content']}")
    print('RESULT:', result['status'])
    print('STOP:', result['stop_reason'])
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
