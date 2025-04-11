import os


DEFAULT_DEFENDERBENCH_CACHE_HOME = os.path.expanduser("~/.cache/defenderbench")
DEFENDERBENCH_CACHE_HOME = os.getenv("DEFENDERBENCH_CACHE_HOME", DEFAULT_DEFENDERBENCH_CACHE_HOME)
os.environ["DEFENDERBENCH_CACHE_HOME"] = DEFENDERBENCH_CACHE_HOME  # Set the environment variable, in case it wasn't.
os.makedirs(DEFENDERBENCH_CACHE_HOME, exist_ok=True)

# Check if cache is flag is set to force download
DEFENDERBENCH_FORCE_DOWNLOAD = os.getenv("DEFENDERBENCH_FORCE_DOWNLOAD", "false").lower() in ("yes", "true", "t", "1")
