from agents import function_tool
from src.utils.python_executor import execute_python

@function_tool
async def code_interpreter(code: str) -> str:
    """
    A tool that interprets and executes Python code snippets.
    This tool uses a secure sandbox environment to run the code safely.
    DO NOT use this tool to execute untrusted code. Be cautious about security implications.

    You can use the following libraries in your code:
    - math
    - pandas
    - numpy
    - matplotlib
    - json
    - re
    - datetime
    - random
    - statistics
    - itertools
    - collections
    - os
    - sys
    - io
    - traceback
    - time
    - builtins
    - typing

    To get the result of your code, assign it to a variable named `out`.

    Args:
        code: A string containing the Python code to be executed.

    Returns:
        The output of the executed code or an error message.
    """
    import math
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import json
    import re
    import datetime
    import random
    import statistics
    import itertools
    import collections
    import os
    import sys
    import io
    import traceback
    import time
    import builtins
    import typing

    result = execute_python(code, context={
        "math": math,
        "pd": pd,
        "np": np,
        "plt": plt,
        "json": json,
        "re": re,
        "datetime": datetime,
        "random": random,
        "statistics": statistics,
        "itertools": itertools,
        "collections": collections,
        "os": os,
        "sys": sys,
        "io": io,
        "traceback": traceback,
        "time": time,
        "builtins": builtins,
        "typing": typing,
    })
    print("Code Interpreter Execution Result:", result)
    return result