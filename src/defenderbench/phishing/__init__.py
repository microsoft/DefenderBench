import gymnasium as gym

from .phishing_env import PhishingText, PhishingTextFewShot
from .phishing_env import PhishingWeb, PhishingWebFewShot
from .phishing_env import PhishingTextSmall, PhishingTextFewShotSmall
from .phishing_env import PhishingWebSmall, PhishingWebFewShotSmall


environments = [
    ['PhishingText', 'v0'],
    ['PhishingTextFewShot', 'v0'],
    ['PhishingWeb', 'v0'],
    ['PhishingWebFewShot', 'v0'],

    ['PhishingTextSmall', 'v0'],
    ['PhishingTextFewShotSmall', 'v0'],
    ['PhishingWebSmall', 'v0'],
    ['PhishingWebFewShotSmall', 'v0']
]

for environment in environments:
    gym.register(
        id='defenderbench/{}-{}'.format(environment[0], environment[1]),
        entry_point='defenderbench.phishing:{}'.format(environment[0]),
    )
