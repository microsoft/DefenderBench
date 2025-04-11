import gymnasium as gym

from .cti_mcq_env import CyberThreatIntelligenceMultiChoiceQuestions
from .cti_mcq_env import CyberThreatIntelligenceMultiChoiceQuestionsWithContext
from .cti_mcq_env import CyberThreatIntelligenceMultiChoiceQuestionsSmall
from .cti_mcq_env import CyberThreatIntelligenceMultiChoiceQuestionsWithContextSmall

environments = [
    ['CyberThreatIntelligenceMultiChoiceQuestions', 'v0'],
    ['CyberThreatIntelligenceMultiChoiceQuestionsWithContext', 'v0'],

    ['CyberThreatIntelligenceMultiChoiceQuestionsSmall', 'v0'],
    ['CyberThreatIntelligenceMultiChoiceQuestionsWithContextSmall', 'v0']
]

for environment in environments:
    gym.register(
        id='defenderbench/{}-{}'.format(environment[0], environment[1]),
        entry_point='defenderbench.cti:{}'.format(environment[0]),
    )
