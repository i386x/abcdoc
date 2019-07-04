#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/core/library.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-06-16 11:41:11 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Library loader and holder.\
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

from .keywords import \
    PRE_CMD, PRE_CMD_LEN, PRE_FILTER, PRE_FILTER_LEN, PRE_TYPE, PRE_TYPE_LEN
from .utils import Importer

class Library(object):
    """
    """
    __slots__ = ["template", "commands", "filters", "types", "rbases"]

    def __init__(self, template):
        """
        """

        self.template = template
        self.commands = {}
        self.filters = {}
        self.types = {}
        self.rbases = []
    #-def

    def setup(self):
        """
        """

        bases = self.template.bases
        self.rbases.extend(bases)
        self.rbases.reverse()
        filters = {}
        for base in bases:
            filters.update(base.filters)
        filters.update(self.filters)
        self.filters = filters
    #-def

    def get_command(self, name, visited=None):
        """
        """

        if visited is None:
            visited = []
        if self in visited:
            return None
        visited.append(self)
        if name in self.commands:
            return self.commands[name]
        for base in self.rbases:
            command = base.library.get_command(name, visited)
            if command:
                return command
        return None
    #-def

    def get_type(self, name, visited=None):
        """
        """

        if visited is None:
            visited = []
        if self in visited:
            return None
        visited.append(self)
        if name in self.types:
            return self.types[name]
        for base in self.rbases:
            typ = base.library.get_type(name, visited)
            if typ:
                return typ
        return None
    #-def

    def load(self, path, name):
        """
        """

        with Importer([path], False):
            module = __import__(name, None, None, ["load"])
            if hasattr(module, "load"):
                library = module.load(self)
                for k in library:
                    if k.startswith(PRE_CMD):
                        self.commands[k[PRE_CMD_LEN:]] = library[k]
                    elif k.startswith(PRE_FILTER):
                        self.filters[k[PRE_FILTER_LEN:]] = library[k]
                    elif k.startswith(PRE_TYPE):
                        self.types[k[PRE_TYPE_LEN:]] = library[k]
    #-def
#-class
