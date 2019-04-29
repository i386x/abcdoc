#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/helpers/utils.py
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

import sys

from .errors import DataFormatError

class Importer(object):
    """
    """
    __slots__ = [ 'path', 'rethrow', 'syspath' ]

    def __init__(self, path = None, rethrow = True):
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

class YamlLocation(object):
    """
    """
    __slots__ = [ 'file', 'trace' ]

    def __init__(self, file = None):
        """
        """

        self.file = file
        self.trace = []
    #-def

    def enter(self):
        """
        """

        self.trace.append(None)
    #-def

    def leave(self):
        """
        """

        if self.trace:
            del self.trace[-1]
    #-def

    def move(self, i):
        """
        """

        if not self.trace:
            return
        self.trace[-1] = i
    #-def

    def __str__(self):
        """
        """

        return "%r: $%s" % (
            self.file, "".join(["[%r]" % i for i in self.trace])
        )
    #-def
#-class

class YamlNode(object):
    """
    """
    __slots__ = [ 'location', 'data' ]

    def __init__(self, location, data):
        """
        """

        self.location = location
        self.data = data
    #-def

    def check_type(self, t):
        """
        """

        if not isinstance(self.data, t):
            raise DataFormatError(
                "%s: expected %s type" % (self.location, t.__name__)
            )
    #-def

    def check_key(self, k):
        """
        """

        self.check_type(dict)
        if k not in self.data:
            raise DataFormatError(
                "%s: missing key: '%s'" % (self.location, k)
            )
    #-def

    def check_value(self, k, p):
        """
        """

        self.check_type(dict)
        if k in self.data and not p(self.data[k]):
            raise DataFormatError(
                "%s: key '%s': invalid value" % (self.location, k)
            )
    #-def
#-class

def read_utf8_file(path):
    """
    """

    try:
        with open(path, "r", encoding = 'utf-8') as f:
            return f.readall()
    except OSError:
        pass
    return None
#-def

def get_config_value(config, name, default = None):
    """
    """

    return config.values.get(name, [default])[0]
#-def
