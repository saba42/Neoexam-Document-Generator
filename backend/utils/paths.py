import os
import sys

def get_base_dir():
    """Works for both local and Render"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

def get_data_path(*subpaths):
    return os.path.join(
        get_base_dir(), "data", *subpaths
    )

def get_cache_path(*subpaths):
    """Use /tmp on Linux server"""
    if os.path.exists("/tmp"):
        cache_dir = "/tmp/.exam_cache"
    else:
        cache_dir = os.path.join(
            get_base_dir(), ".cache"
        )
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, *subpaths)

def get_output_path(filename):
    """Use /tmp on Linux server"""
    if os.path.exists("/tmp"):
        out_dir = "/tmp/exam_outputs"
    else:
        out_dir = os.path.join(
            get_base_dir(), "outputs"
        )
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, filename)
