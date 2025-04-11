import json

import gymnasium as gym
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from . import phishing_data
from ..utils import HistoryTracker, extract_code


class PhishingEnv(gym.Env):

    CLASS_LABELS = ["legitimate", "malicious"]

    def __init__(self, data, few_shot_data=None, nb_trials=5):
        self.data = data
        self.few_shot_data = few_shot_data
        self.history = HistoryTracker(nb_trials)

        self.nb_steps = len(self.data)
        self.nb_trials = nb_trials

    @property
    def instructions(self):
        return NotImplementedError()

    def build_observation(self):
        return (
            f"Content:\n```\n{self.current_sample}\n```"
        )

    def next_sample(self):
        self.sample_id += 1
        if self.sample_id >= len(self.data):
            return False

        self.current_sample = self.data[self.sample_id]["content"]
        self.sample_label = self.data[self.sample_id]["category"]
        self.gold_labels.append(self.sample_label)
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

            if prediction not in self.CLASS_LABELS:
                obs = 'Your answer is invalid. Your answer must be a JSON dictionary like {"answer": "malicious"/"legitimate"} where the value must be either "malicious" or "legitimate".'
                prediction = ''
            else:
                done = True
                reward = int(prediction == self.sample_label)
                obs = f"Your answer is {prediction}. "
                obs += f"This is the correct answer." if reward else f"This is the wrong answer."

        except (ValueError, IndexError, KeyError, AttributeError):
            obs = 'Your answer is invalid. Your answer must be a JSON dictionary like {"answer": "malicious"/"legitimate"} where the value must be either "malicious" or "legitimate".'
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


class PhishingText(PhishingEnv):
    def __init__(self, *args, limit=None, **kwargs):
        super().__init__(phishing_data.get_text_data("test", limit), *args, **kwargs)

    @property
    def instructions(self):
        return (
            "You need to carefully analyze whether a given message is malicious or legitimate."
            " The malicious content may be phishing email/SMS, smishing or spam email/SMS."
            ' Your answer must be a JSON dictionary like {"answer": "malicious"/"legitimate"} where the value must be either "malicious" or "legitimate".'
        )


class PhishingTextSmall(PhishingText):
    def __init__(self, *args, **kwargs):
        super().__init__(limit=100, *args, **kwargs)


class PhishingTextFewShot(PhishingText):
    fewshot = 4

    def __init__(self, *args, **kwargs):
        super().__init__(few_shot_data=phishing_data.get_text_data("train"), *args, **kwargs)

    @property
    def instructions(self):
        few_shot_samples = ""
        for i in range(self.fewshot):
            few_shot_samples += f"Content {i+1}:\n```\n{self.few_shot_data[i]['content']}\n```\n"
            few_shot_samples += f'Response {i+1}: {{"answer": "{self.few_shot_data[i]["category"].lower()}"}}\n'

        return super().instructions + (
            f"Here are {self.fewshot} samples for you to understand the task:\n"
            f"{few_shot_samples}\n"
            "Now, here is the actual content you need to analyze.\n"
        )


class PhishingTextFewShotSmall(PhishingTextFewShot):
    def __init__(self, *args, **kwargs):
        super().__init__(limit=100, *args, **kwargs)


class PhishingWeb(PhishingEnv):
    def __init__(self, *args, limit=None, **kwargs):
        super().__init__(phishing_data.get_web_data("test", limit), *args, **kwargs)

    @property
    def instructions(self):
        return (
            "You need to carefully analyze whether a given webpage is malicious or legitimate."
            ' Your answer must be a JSON dictionary like {"answer": "malicious"/"legitimate"} where the value must be either "malicious" or "legitimate".'
        )

class PhishingWebSmall(PhishingWeb):
    def __init__(self, *args, **kwargs):
        super().__init__(limit=100, *args, **kwargs)


class PhishingWebFewShot(PhishingWeb):
    fewshot = 2

    def __init__(self, *args, **kwargs):
        super().__init__(few_shot_data=phishing_data.get_web_data("train"), *args, **kwargs)

    @property
    def instructions(self):
        few_shot_samples = ""
        for i in range(self.fewshot):
            few_shot_samples += f"Content {i+1}:\n```\n{self.few_shot_data[i]['content']}\n```\n"
            few_shot_samples += f'Response {i+1}: {{"answer": "{self.few_shot_data[i]["category"].lower()}"}}\n'

        return super().instructions + (
            f"Here are {self.fewshot} samples for you to understand the task:\n"
            f"{few_shot_samples}\n"
            "Now, here is the actual content you need to analyze.\n"
        )


class PhishingWebFewShotSmall(PhishingWebFewShot):
    def __init__(self, *args, **kwargs):
        super().__init__(limit=100, *args, **kwargs)
