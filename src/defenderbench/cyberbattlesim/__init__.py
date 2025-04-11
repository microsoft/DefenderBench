import gymnasium as gym

from .cyberbattlesim_env import CyberBattleChain2, CyberBattleChain4, CyberBattleChain10
from .cyberbattlesim_env import CyberBattleTiny, CyberBattleToyCTF

environments = [
    ['CyberBattleTiny', 'v0'],
    ['CyberBattleChain2', 'v0'],
    ['CyberBattleChain4', 'v0'],
    ['CyberBattleChain10', 'v0'],
    ['CyberBattleToyCTF', 'v0'],
]

for environment in environments:
    gym.register(
        id='defenderbench/{}-{}'.format(environment[0], environment[1]),
        entry_point='defenderbench.cyberbattlesim:{}'.format(environment[0]),
    )
