from io import StringIO
import itertools
import logging
import os
import copy
import shutil
import requests
import tempfile

from os.path import join as pjoin

from tqdm import tqdm


class HistoryTracker:

    def __init__(self, max_steps) -> None:
        self.max_steps = max_steps
        self.game_step = 0
        self.reset()

    def step(self, info) -> None:
        self.info.append(copy.copy(info))
        if len(self.info) > self.max_steps:
            self.info.pop(0)
        self.game_step += 1

    def reset(self) -> None:
        self.info = []
        self.game_step = 0

    def describe(self, game_step=None):
        if len(self.info) == 0:
            return ""
        game_step = self.game_step if game_step is None else game_step
        result = "Most recent {} steps of the assistant's action observation:\n\n".format(len(self.info))
        for i, info in enumerate(self.info):
            result += "Observation Step {}:\n".format(game_step - len(self.info) + i)
            result += info["obs"] + "\n\n"
        return result.strip()

    def score(self):
        return sum([info["score"] for info in self.info])


def describe_act(action_list):
    return "List of all actions:\n" + "\n".join(["{}. {}".format(i+1, s) for i,s in enumerate(action_list)])


def mkdirs(dirpath: str) -> str:
    """ Create a directory and all its parents.

    If the folder already exists, its path is returned without raising any exceptions.

    Arguments:
        dirpath: Path where a folder need to be created.

    Returns:
        Path to the (created) folder.
    """
    try:
        os.makedirs(dirpath)
    except FileExistsError:
        pass

    return dirpath


def download(url, dst, force=False):
    """ Download a remote file using HTTP get request.

    Args:
        url (str): URL where to get the file.
        dst (str): Destination folder where to save the file.
        force (bool, optional):
            Download again if it exists]. Defaults to False.

    Returns:
        str: Path to the downloaded file.

    Notes:
        This code is inspired by
        https://github.com/huggingface/transformers/blob/v4.0.0/src/transformers/file_utils.py#L1069
    """
    filename = url.split('/')[-1]
    path = pjoin(mkdirs(dst), filename)

    if os.path.isfile(path) and not force:
        return path

    # Download to a temp folder first to avoid corrupting the cache
    # with incomplete downloads.
    temp_dir = mkdirs(pjoin(tempfile.gettempdir(), "cyberbench"))
    temp_path = pjoin(temp_dir, filename)
    with open(temp_path, 'ab') as temp_file:
        headers = {}
        resume_size = temp_file.tell()
        if resume_size:
            headers['Range'] = f'bytes={resume_size}-'
            headers['x-ms-version'] = "2020-04-08"  # Needed for Range support.

        r = requests.get(url, stream=True, headers=headers)
        if r.headers.get("x-ms-error-code") == "InvalidRange" and r.headers["Content-Range"].rsplit("/", 1)[-1] == str(resume_size):
            shutil.move(temp_path, path)
            return path

        r.raise_for_status()  # Bad request.
        content_length = r.headers.get("Content-Length")
        total = resume_size + int(content_length)
        pbar = tqdm(
            unit="B",
            initial=resume_size,
            unit_scale=True,
            total=total,
            desc="Downloading {}".format(filename),
        )

        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                pbar.update(len(chunk))
                temp_file.write(chunk)

    shutil.move(temp_path, path)

    pbar.close()
    return path


def take(n, iterable):
    "Return first n items of the iterable as a list."
    # Ref: https://docs.python.org/3/library/itertools.html#itertools-recipes
    return list(itertools.islice(iterable, n))


def extract_code(raw_response, code_type="json", return_last=True):
    # Postprocess response, keep only the code chunks between "```" and "```"
    # Iterate over all code chunks and return the last one or biggest chunk if option is provided.
    code = ""
    code_chunks = raw_response.split("```")
    for i in range(1, len(code_chunks), 2):
        code_chunk = code_chunks[i]
        if code_chunk.startswith(f"{code_type}\n"):
            code_chunk = code_chunk[len(code_type)+1:]

        if return_last or len(code_chunk) > len(code):
            code = code_chunk

    return code or raw_response


class catch_logging:
    def __enter__(self):
        # Capture logging warnings
        self.logger = logging.getLogger()
        self.logger_handlers = self.logger.handlers
        self.logger.handlers = []

        # Set new handler
        self.stream_handler = logging.StreamHandler(StringIO())
        self.logger.addHandler(self.stream_handler)
        return self.stream_handler.stream

    def __exit__(self, exc_type, exc_value, traceback):
        # Restore original handlers
        self.logger.handlers = self.logger_handlers
        