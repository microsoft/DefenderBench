import json

import gymnasium as gym

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from . import cti_mcq_data
from ..utils import HistoryTracker, extract_code


class MCQEnv(gym.Env):

    CLASS_LABELS = ["A", "B", "C", "D"]

    def __init__(self, data, nb_trials=5):
        self.data = data
        self.history = HistoryTracker(nb_trials)

        self.nb_steps = len(self.data)
        self.nb_trials = nb_trials

    @property
    def instructions(self):
        return (
            "You are given a multiple-choice question (MCQ) from a Cyber Threat Intelligence (CTI) knowledge benchmark dataset."
            " Your task is to choose the best option among the four provided."
            ' Your answer must be a JSON dictionary like {"answer": "A/B/C/D"} where the value must be a single letter: A, B, C, or D.'
        )

    def build_observation(self):
        return (
            f"Question: {self.sample_question}\n"
            f"Options:\n  A: {self.options[0]}\n  B: {self.options[1]}\n  C: {self.options[2]}\n  D: {self.options[3]}"
        )

    def next_sample(self):
        self.sample_id += 1
        if self.sample_id >= len(self.data):
            return False

        self.sample_question = self.data.iloc[self.sample_id]["Question"]
        self.sample_label = self.data.iloc[self.sample_id]["GT"]
        self.options = self.data.iloc[self.sample_id][2:6].values.tolist()

        self.gold_labels.append(self.sample_label.upper())
        self.predictions.append('')
        self.history.reset()
        self.trial_id = 0

        return True

    def reset(self):
        self.metrics = {
            "acc": 0,
            "macf1": 0,
            "macpre": 0,
            "macrec": 0,
        }

        self.gold_labels = []
        self.predictions = []
        self.sample_id = -1
        self.score = 0
        self.max_score = len(self.data)

        self.next_sample()
        info = {
            "obs": self.build_observation(),
            "instructions": self.instructions,
            "history": self.history.describe(),
            "score": 0,
            "max_score": self.max_score,
            "metrics": self.metrics,
            "last_action": None,
            "step_done": False,
            "actions": [json.dumps({'answer': label}) for label in self.CLASS_LABELS],
        }
        self.history.step(info)
        return 0, info

    def step(self, action):
        last_action = action
        action = extract_code(action, code_type="json")
        self.trial_id += 1

        prediction = ''
        done = False
        reward = 0
        try:
            prediction = json.loads(action.lower().replace("'", '"'))
            if type(prediction) is dict:
                prediction = prediction['answer']

            prediction = prediction.upper()
            if prediction not in self.CLASS_LABELS:
                obs = 'Your answer is invalid. Your answer must be a JSON dictionary like {"answer": "A/B/C/D"} where the value must be a single letter: A, B, C, or D.'
                prediction = ''
            else:
                done = True
                reward = int(prediction == self.sample_label)
                obs = f"Your answer is {prediction}. "
                obs += f"This is the correct answer." if reward else f"This is the wrong answer."

        except (ValueError, IndexError, KeyError, AttributeError):
            obs = 'Your answer is invalid. Your answer must be a JSON dictionary like {"answer": "A/B/C/D"} where the value must be a single letter: A, B, C, or D.'
            prediction = ''

        if self.trial_id >= self.nb_trials:
            done = True

        if done:
            self.score += reward
            self.predictions[-1] = prediction

        acc = accuracy_score(self.gold_labels, self.predictions)
        macf1 = f1_score(self.gold_labels, self.predictions, average='macro', zero_division=0, labels=self.CLASS_LABELS)
        macpre = precision_score(self.gold_labels, self.predictions, average='macro', zero_division=0, labels=self.CLASS_LABELS)
        macrec = recall_score(self.gold_labels, self.predictions, average='macro', zero_division=0, labels=self.CLASS_LABELS)

        self.metrics = {
            "acc": float(acc),
            "macf1": float(macf1),
            "macpre": float(macpre),
            "macrec": float(macrec),
        }

        step_done = done
        if done and self.next_sample():
            obs = self.build_observation()
            done = False
            last_action = None

        info = {
            "obs": obs,
            "last_action": last_action,
            "instructions": self.instructions,
            "history": self.history.describe(),
            "score": self.score,
            "max_score": self.max_score,
            "metrics": self.metrics,
            "step_done": step_done,
            "actions": [json.dumps({'answer': label}) for label in self.CLASS_LABELS],
        }
        self.history.step(info)

        return 0, reward, done, info


class CyberThreatIntelligenceMultiChoiceQuestions(MCQEnv):
    def __init__(self, *args, limit=None, **kwargs):
        super().__init__(cti_mcq_data.get_mcq_data("test", limit), *args, **kwargs)


class CyberThreatIntelligenceMultiChoiceQuestionsSmall(CyberThreatIntelligenceMultiChoiceQuestions):
    def __init__(self, *args, **kwargs):
        super().__init__(limit=100, *args, **kwargs)


class CyberThreatIntelligenceMultiChoiceQuestionsWithContext(CyberThreatIntelligenceMultiChoiceQuestions):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_observation(self):
        self.context_doc = cti_mcq_data.get_mcq_html_data(self.data.iloc[self.sample_id]["URL"])
        return (
            "Context: Here is a webpage that may help answer the question.\n"
            f"```\n{self.context_doc}\n```\n"
        ) + super().build_observation()


class CyberThreatIntelligenceMultiChoiceQuestionsWithContextSmall(CyberThreatIntelligenceMultiChoiceQuestionsWithContext):
    def __init__(self, *args, **kwargs):
        super().__init__(limit=100, *args, **kwargs)
