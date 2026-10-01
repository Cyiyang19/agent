"""Pydantic rule sketch for Chapter 6's AgentScope werewolf exercise.

This validates proposed data. The moderator still owns the authoritative game state.
AgentScope itself is not imported or executed by this file.
"""
from pydantic import BaseModel, Field, model_validator


class HunterAction(BaseModel):
    shoot: bool = Field(description='Whether the hunter fires after death')
    target_name: str | None = Field(default=None, description='Name of the target')
    reason: str = Field(min_length=1, max_length=200, description='Short explanation')

    @model_validator(mode='after')
    def target_matches_choice(self):
        if self.shoot and not self.target_name:
            raise ValueError('A shot needs a target')
        if not self.shoot and self.target_name is not None:
            raise ValueError('No target is allowed without a shot')
        return self


def validate_hunter_event(action: HunterAction, *, death_cause: str,
                          hunter_name: str, alive_players: set[str],
                          shot_already_used: bool) -> None:
    """Example house rules: wolf/vote allow one shot; poison does not."""
    if not action.shoot:
        return
    if death_cause not in {'wolf', 'vote'}:
        raise ValueError('This death does not trigger a shot')
    if shot_already_used:
        raise ValueError('Hunter has already fired')
    if action.target_name == hunter_name or action.target_name not in alive_players:
        raise ValueError('Target must be another living player')


if __name__ == '__main__':
    good = HunterAction(shoot=True, target_name='曹操', reason='选择一名存活玩家')
    validate_hunter_event(good, death_cause='wolf', hunter_name='赵云',
                          alive_players={'赵云', '曹操'}, shot_already_used=False)
    print('VALID:', good.model_dump())
    try:
        bad = HunterAction(shoot=True, target_name=None, reason='没有目标')
    except ValueError:
        print('INVALID: shooting without target was rejected')
    else:
        raise AssertionError(bad)
    try:
        validate_hunter_event(good, death_cause='poison', hunter_name='赵云',
                              alive_players={'赵云', '曹操'}, shot_already_used=False)
    except ValueError:
        print('INVALID: poison death was rejected by moderator rules')
    else:
        raise AssertionError('poison triggered a shot')
