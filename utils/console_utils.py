import time
import sys

def setup_progress_bar(toolbar_width):
    sys.stdout.write("[%s]" % (" " * toolbar_width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (toolbar_width+1))

def update_progress_bar():
    sys.stdout.write("-")
    sys.stdout.flush()

def close_progress_bar():
    sys.stdout.write("]\n")