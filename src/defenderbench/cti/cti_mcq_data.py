import os
import logging
from typing import Optional

from sklearn.model_selection import train_test_split
from os.path import join as pjoin
import pandas as pd

from defenderbench.config import DEFENDERBENCH_CACHE_HOME, DEFENDERBENCH_FORCE_DOWNLOAD
from defenderbench.utils import download

# Source: https://huggingface.co/datasets/AI4Sec/cti-bench
CTI_MCQ_URL = "https://huggingface.co/datasets/AI4Sec/cti-bench/resolve/main/cti-mcq.tsv"
DEFENDERBENCH_CACHE_CTI = pjoin(DEFENDERBENCH_CACHE_HOME, "cyber_threat_intelligence")

DEFENDERBENCH_CACHE_CTI_MCQ_DATA = pjoin(DEFENDERBENCH_CACHE_CTI, "cti-mcq.tsv")
DEFENDERBENCH_CACHE_CTI_MCQ_DATA_TRAIN = pjoin(DEFENDERBENCH_CACHE_CTI, "cti-mcq_train.json")
DEFENDERBENCH_CACHE_CTI_MCQ_DATA_TEST = pjoin(DEFENDERBENCH_CACHE_CTI, "cti-mcq_test.json")

DEFENDERBENCH_CACHE_CTI_MCQ_HTML = pjoin(DEFENDERBENCH_CACHE_CTI, "html")


def prepare_mcq_data(force=DEFENDERBENCH_FORCE_DOWNLOAD):
    all_files_exist = (
        os.path.exists(DEFENDERBENCH_CACHE_CTI_MCQ_DATA_TRAIN)
        and os.path.exists(DEFENDERBENCH_CACHE_CTI_MCQ_DATA_TEST)
    )
    if all_files_exist and not force:
        return

    download(CTI_MCQ_URL, os.path.dirname(DEFENDERBENCH_CACHE_CTI_MCQ_DATA), force=force)
    cti_mcq_data = pd.read_csv(DEFENDERBENCH_CACHE_CTI_MCQ_DATA, sep="\t")
    logging.info(f"CyberThreatIntelligenceMultiChoiceQuestions: Total examples: {len(cti_mcq_data)}")

    # remove rows that url column is not with "http"
    cti_mcq_data = cti_mcq_data[cti_mcq_data["URL"].str.contains("http")]

    all_links = cti_mcq_data.URL.unique()

    # TODO: smarter split by balancing the classes and the embeddings
    train_data, test_data = train_test_split(cti_mcq_data, test_size=0.9, random_state=42)
    logging.info(f"CyberThreatIntelligenceMultiChoiceQuestions: train|test splits: {len(train_data)}|{len(test_data)}")

    subset_train_data = train_data.sample(n=20, random_state=42)
    subset_test_data = test_data.sample(n=500, random_state=42)
    logging.info(f"CyberThreatIntelligenceMultiChoiceQuestions: Total train subset: {len(subset_train_data)}")
    logging.info(f"CyberThreatIntelligenceMultiChoiceQuestions: Total test subset: {len(subset_test_data)}")

    subset_train_data.to_csv(DEFENDERBENCH_CACHE_CTI_MCQ_DATA_TRAIN, sep="\t", index=False)
    subset_test_data.to_csv(DEFENDERBENCH_CACHE_CTI_MCQ_DATA_TEST, sep="\t", index=False)


def get_mcq_data(name, limit: Optional[int] = None):
    prepare_mcq_data()  # make sure the data is ready

    if name == "train":
        return pd.read_csv(DEFENDERBENCH_CACHE_CTI_MCQ_DATA_TRAIN, sep="\t")
    elif name == "test":
        data = pd.read_csv(DEFENDERBENCH_CACHE_CTI_MCQ_DATA_TEST, sep="\t")
        return data[:limit] if limit else data
    else:
        raise ValueError(f"Invalid data name: {name} for CyberThreatIntelligenceMultiChoiceQuestions environment.")


def get_mcq_html_data(url):
    import requests
    html_filename = "{}.html".format(url.split("//")[-1].strip("/").replace("/", "-"))
    if os.path.exists(pjoin(DEFENDERBENCH_CACHE_CTI_MCQ_HTML, html_filename)) and not DEFENDERBENCH_FORCE_DOWNLOAD:
        with open(pjoin(DEFENDERBENCH_CACHE_CTI_MCQ_HTML, html_filename), "r") as f:
            return f.read()

    html = requests.get(url).text
    os.makedirs(DEFENDERBENCH_CACHE_CTI_MCQ_HTML, exist_ok=True)
    with open(pjoin(DEFENDERBENCH_CACHE_CTI_MCQ_HTML, html_filename), "w") as f:
        f.write(html)

    return html
