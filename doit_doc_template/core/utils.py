#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/core/utils.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-04-22 19:14:36 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Commonly used classes and functions.\
"""

__license__ = """\
Copyright (c) 2014 - 2019 Jiří Kučera.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.\
"""

import inspect
import sys

from yaml import load, MarkedYAMLError, YAMLError

from .errors import ReadFileError, YamlError
from .yaml import YamlLoader

def intersect(set_a, set_b):
    """
    """

    return [x for x in set_a if x in set_b]
#-def

def ensure_key(dictionary, key, value, always_overwrite=False):
    """
    """

    if always_overwrite or key not in dictionary:
        dictionary[key] = value
#-def

def caller_name(depth=0, klass=None):
    """
    """

    name = inspect.stack()[depth + 1][3]
    if klass is not None:
        name = "{}.{}".format(klass.__name__, name)
    return name
#-def

def typename_from_type(t):
    """
    """

    if issubclass(t, dict):
        return "dictionary"
    if issubclass(t, list):
        return "list"
    if issubclass(t, str):
        return "string"
    if hasattr(t, "__name__"):
        return t.__name__
    return "object"
#-def

def typename_from_data(data):
    """
    """

    return typename_from_type(type(data))
#-def

def add_filename_to_yaml_error(error, filename):
    """
    """

    if not isinstance(error, MarkedYAMLError):
        return
    if error.context_mark is not None:
        error.context_mark.name = filename
    if error.problem_mark is not None:
        error.problem_mark.name = filename
#-def

def read_utf8_file(filename):
    """
    """

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.readall()
    except OSError:
        pass
    return None
#-def

def read_yaml_file(filename):
    """
    """

    content = read_utf8_file(filename)
    if content is None:
        raise ReadFileError(filename)
    try:
        return load(content, YamlLoader)
    except YAMLError as error:
        add_filename_to_yaml_error(error, filename)
        raise YamlError(error)
    return None
#-def

def get_config_value(config, name, default=None):
    """
    """

    return config.values.get(name, [default])[0]
#-def

class Importer(object):
    """
    """
    __slots__ = ["path", "rethrow", "syspath"]

    def __init__(self, path=None, rethrow=True):
        """
        """

        self.path = path or []
        self.rethrow = rethrow
        self.syspath = []
    #-def

    def __enter__(self):
        """
        """

        self.syspath = sys.path
        sys.path = self.path + self.syspath
    #-def

    def __exit__(self, exc_type, exc_value, traceback):
        """
        """

        sys.path = self.syspath
        if self.rethrow:
            return None
        if exc_type is ImportError:
            return True
        return None
    #-def
#-class
