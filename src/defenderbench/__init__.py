# This file is used to load all tasks in the defenderbench directory.

import traceback
import warnings
import importlib
import os

from termcolor import colored

from src.defenderbench.version import __version__


root_dir = os.path.dirname(os.path.abspath(__file__))
tasks = []
env_list = []


_exclude_path = ['__pycache__']

for dirname in os.listdir(root_dir):
    if not os.path.isdir(os.path.join(root_dir, dirname)):
        continue

    if dirname in _exclude_path:
        continue

    if "skip" in os.listdir(os.path.join(root_dir, dirname)):
        continue

    if "__init__.py" in os.listdir(os.path.join(root_dir, dirname)):
        tasks.append(dirname)


for task in tasks:
    try:
        # Load environments
        module = importlib.import_module(f".{task}", package='defenderbench')
        environments = getattr(module, 'environments', None)
        if environments:
            for env_name, version in environments:
                env_list.append('{}-{}'.format(env_name, version))
        else:
            warnings.warn('Failed to load `{}.environments`. Skipping the task.'.format(task), UserWarning)
            continue

    except Exception as e:
        warnings.warn('Failed to import `{}`. Skipping the task.'.format(task), UserWarning)
        warnings.warn(colored(f'{e}', 'red'), UserWarning)
        # Add stacktrace
        warnings.warn(colored(f'{traceback.format_exc()}', 'red'), UserWarning)
        continue


# Benchmark tasks used in the paper
benchmark_v0 = [
    'PhishingText',
    'PhishingTextFewShot',
    'PhishingWeb',
    'PhishingWebFewShot',
    'CyberThreatIntelligenceMultiChoiceQuestions',
    'CyberThreatIntelligenceMultiChoiceQuestionsWithContext',
    'CodeVulnerabilityDetection',
    'CodeVulnerabilityDetectionFewShot',
    'CodeVulnerabilityDevignDetection',
    'CodeVulnerabilityDevignDetectionFewShot',
    'CVEFix',
    'CyberBattleChain2',
    'CyberBattleChain4',
    'CyberBattleChain10',
    'CyberBattleTiny',
    'CyberBattleToyCTF',
]

benchmark_small_v0 = [
    'PhishingTextSmall',
    'PhishingTextFewShotSmall',
    'PhishingWebSmall',
    'PhishingWebFewShotSmall',
    'CyberThreatIntelligenceMultiChoiceQuestionsSmall',
    'CyberThreatIntelligenceMultiChoiceQuestionsWithContextSmall',
    'CodeVulnerabilityDetectionSmall',
    'CodeVulnerabilityDetectionFewShotSmall',
    'CodeVulnerabilityDevignDetectionSmall',
    'CodeVulnerabilityDevignDetectionFewShotSmall',
    'CVEFixSmall',
    'CyberBattleChain2',
    'CyberBattleChain4',
    'CyberBattleChain10',
    'CyberBattleTiny',
    'CyberBattleToyCTF',
]
