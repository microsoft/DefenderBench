import logging
import os
import json
from typing import Optional
import urllib.request
from random import shuffle
from sklearn.model_selection import train_test_split
from os.path import join as pjoin

from defenderbench.config import DEFENDERBENCH_CACHE_HOME, DEFENDERBENCH_FORCE_DOWNLOAD
from defenderbench.utils import download

# Source: https://huggingface.co/datasets/ealvaradob/phishing-dataset
TEXTS_URL = "https://huggingface.co/datasets/ealvaradob/phishing-dataset/resolve/main/texts.json"
WEBS_URL = "https://huggingface.co/datasets/ealvaradob/phishing-dataset/resolve/main/webs.json"
DEFENDERBENCH_CACHE_PHISHING = pjoin(DEFENDERBENCH_CACHE_HOME, "phishing")

DEFENDERBENCH_CACHE_PHISHING_TEXT_DATA = pjoin(DEFENDERBENCH_CACHE_PHISHING, "texts.json")
DEFENDERBENCH_CACHE_PHISHING_TEXT_DATA_TRAIN = pjoin(DEFENDERBENCH_CACHE_PHISHING, "texts_train.json")
DEFENDERBENCH_CACHE_PHISHING_TEXT_DATA_TEST = pjoin(DEFENDERBENCH_CACHE_PHISHING, "texts_test.json")

DEFENDERBENCH_CACHE_PHISHING_WEB_DATA = pjoin(DEFENDERBENCH_CACHE_PHISHING, "webs.json")
DEFENDERBENCH_CACHE_PHISHING_WEB_DATA_TRAIN = pjoin(DEFENDERBENCH_CACHE_PHISHING, "webs_train.json")
DEFENDERBENCH_CACHE_PHISHING_WEB_DATA_TEST = pjoin(DEFENDERBENCH_CACHE_PHISHING, "webs_test.json")


def remap_labels(dataset):
    return [
        {"content": item["text"], "category": "malicious" if item["label"] == 1 else "legitimate"}
        for item in dataset
    ]


def prepare_text_data(force=DEFENDERBENCH_FORCE_DOWNLOAD):
    all_files_exist = (
        os.path.exists(DEFENDERBENCH_CACHE_PHISHING_TEXT_DATA_TRAIN)
        and os.path.exists(DEFENDERBENCH_CACHE_PHISHING_TEXT_DATA_TEST)
    )
    if all_files_exist and not force:
        return

    download(TEXTS_URL, os.path.dirname(DEFENDERBENCH_CACHE_PHISHING_TEXT_DATA), force=force)
    text_data = json.load(open(DEFENDERBENCH_CACHE_PHISHING_TEXT_DATA))
    logging.info(f"PhishingText: Total examples: {len(text_data)}")

    # TODO: smarter split by balancing the classes and the embeddings
    train_data, test_data = train_test_split(text_data, test_size=0.2, random_state=42)
    logging.info(f"PhishingText: train|test splits: {len(train_data)}|{len(test_data)}")

    # downsample the data
    subset_test_data = test_data[:500]

    logging.info(f"PhishingText: Total test subset: {len(subset_test_data)}")
    subset_test_data = remap_labels(subset_test_data)
    with open(DEFENDERBENCH_CACHE_PHISHING_TEXT_DATA_TEST, "w") as f:
        json.dump(subset_test_data, f, indent=2)

    # Downsample the train data while keeping the classes balanced.
    positive_data = [item for item in train_data if item["label"] == 1]
    negative_data = [item for item in train_data if item["label"] == 0]

    subset_train_data = []
    for i in range(10):
        subset_train_data.append(positive_data[i])
        subset_train_data.append(negative_data[i])

    logging.info(f"PhishingText: Total train subset: {len(subset_train_data)}")
    subset_train_data = remap_labels(subset_train_data)
    with open(DEFENDERBENCH_CACHE_PHISHING_TEXT_DATA_TRAIN, "w") as f:
        json.dump(subset_train_data, f, indent=2)


def prepare_web_data(force=DEFENDERBENCH_FORCE_DOWNLOAD):
    all_files_exist = (
        os.path.exists(DEFENDERBENCH_CACHE_PHISHING_WEB_DATA_TRAIN)
        and os.path.exists(DEFENDERBENCH_CACHE_PHISHING_WEB_DATA_TEST)
    )
    if all_files_exist and not force:
        return

    download(WEBS_URL, os.path.dirname(DEFENDERBENCH_CACHE_PHISHING_WEB_DATA), force=force)
    web_data = json.load(open(DEFENDERBENCH_CACHE_PHISHING_WEB_DATA))
    logging.info(f"PhishingWeb: Total examples: {len(web_data)}")

    # Filter out website content with less than 100 characters.
    web_data = [item for item in web_data if len(item["text"]) > 100]

    # TODO: smarter split by balancing the classes and the embeddings
    train_data, test_data = train_test_split(web_data, test_size=0.2, random_state=42)
    logging.info(f"PhishingWeb: train|test splits: {len(train_data)}|{len(test_data)}")

    # downsample the data
    subset_test_data = test_data[:500]

    logging.info(f"PhishingWeb: Total test subset: {len(subset_test_data)}")
    subset_test_data = remap_labels(subset_test_data)
    with open(DEFENDERBENCH_CACHE_PHISHING_WEB_DATA_TEST, "w") as f:
        json.dump(subset_test_data, f, indent=2)

    # Downsample the train data while keeping the classes balanced.
    positive_data = [item for item in train_data if item["label"] == 1]
    negative_data = [item for item in train_data if not item["label"] == 0]

    subset_train_data = []
    for i in range(10):
        subset_train_data.append(positive_data[i])
        subset_train_data.append(negative_data[i])

    logging.info(f"PhishingWeb: Total train subset: {len(subset_train_data)}")
    subset_train_data = remap_labels(subset_train_data)
    with open(DEFENDERBENCH_CACHE_PHISHING_WEB_DATA_TRAIN, "w") as f:
        json.dump(subset_train_data, f, indent=2)


def get_text_data(name, limit: Optional[int] = None):
    prepare_text_data()  # make sure the data is ready

    if name == "train":
        return json.load(open(DEFENDERBENCH_CACHE_PHISHING_TEXT_DATA_TRAIN))
    elif name == "test":
        data = json.load(open(DEFENDERBENCH_CACHE_PHISHING_TEXT_DATA_TEST))
        return data[:limit] if limit else data
    else:
        raise ValueError(f"Invalid data name: {name} for PhishingText environment.")


def get_web_data(name, limit: Optional[int] = None):
    prepare_web_data()  # make sure the data is ready

    if name == "train":
        return json.load(open(DEFENDERBENCH_CACHE_PHISHING_WEB_DATA_TRAIN))
    elif name == "test":
        data = json.load(open(DEFENDERBENCH_CACHE_PHISHING_WEB_DATA_TEST))
        return data[:limit] if limit else data
    else:
        raise ValueError(f"Invalid data name: {name} for PhishingWeb environment.")
