import traceback
import subprocess
import functools
import os
import io
import shlex
import textwrap
import platform
from pprint import pprint

import flask

app = flask.Flask(__name__)

def add_header_and_capture_exception(func):
    def wrapper(*args, **kwargs):
        header = f'# === {func.__name__}({shlex.join((*args, *kwargs.values()))}) ===\n'
        try:
            contents = [func(*args, **kwargs)]
        except Exception as e:
            contents = traceback.format_exception(e)
        return ''.join((header, *contents))
    return functools.update_wrapper(wrapper, func)

@app.route('/')
@add_header_and_capture_exception
def index():
    """Print index of available endpoints
    """
    return textwrap.dedent("""\
    Example of poorly written code.
    GET /          -> this index
    GET /getos     -> os-release dictionary
    GET /exec/date -> will give you the current date & time in the server
    GET /exec/cal  -> will give out the calendar for this month
    POST /files/filename -> Saves the data in file
    GET /files/filename  -> Retrieves the data from file
    """)

@app.route('/getos')
@add_header_and_capture_exception
def getos():
    out = io.StringIO()
    pprint(platform.freedesktop_os_release(), out)
    return out.getvalue()

@app.route('/exec/<path:cmd>')
@add_header_and_capture_exception
def exec(cmd):
    if 'date' not in cmd and 'cal' not in cmd:
        # FIXME: add a proper error response here
        print('Permission denied!')

    cmd = cmd.split()
    return subprocess.check_output(cmd, text=True)

@app.route('/files/<path:path>')
@add_header_and_capture_exception
def get(path):
    return open(f'files/{path}').read()

@app.post('/files/<path:path>')
@add_header_and_capture_exception
def put(path):
    os.makedirs('files', exist_ok=True)
    data = flask.request.get_data()
    with open(f'files/{path}', 'wb') as f:
        n = f.write(data)
    return f'OK. Wrote {n} bytes.\n'
