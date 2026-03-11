import os, sys

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

def get_data_path(*sub):
    return os.path.join(get_base_dir(), "data", *sub)

def get_cache_path(*sub):
    d = os.path.join(get_base_dir(), ".cache")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, *sub)

def get_output_path(filename):
    d = os.path.join(get_base_dir(), "outputs")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, filename)

def get_env_path():
    return os.path.join(get_base_dir(), ".env")
