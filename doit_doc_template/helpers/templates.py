#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/helpers/templates.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-04-20 14:32:29 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Templates management.\
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

import os

from jinja2 import BaseLoader, TemplateNotFound

from .utils import read_utf8_file

class TeplateFileLoader(BaseLoader):
    """
    """

    def __init__(self, *args):
        """
        """

        super().__init__()
        self.path = args
    #-def

    def get_source(self, environment, template):
        """
        """

        for p in self.path:
            path = os.path.join(p, template)
            source = read_utf8_file(path)
            if source is None:
                continue
            return source, path, lambda: False
        raise TemplateNotFound(template)
    #-def
#-class

class Component(object):
    """
    """
    MACRO = 1
    GROUP = 2
    types = dict(macro = MACRO, group = GROUP)
    __slots__ = [ 'name', 'type', 'files', 'requires', 'location' ]

    def __init__(
        self, name,
        type = None, files = None, requires = None, location = None
    ):
        """
        """

        self.name = name
        self.type = type
        self.files = files
        self.requires = requires or []
        self.location = location or "???"
    #-def

    @classmethod
    def from_yaml_node(cls, node):
        """
        """

        node.check_key('name')
        node.check_value('name', lambda x: isinstance(x, str))
        node.check_value('type', lambda x: x in cls.types)
        node.check_value('files', lambda x: isinstance(x, list))
        node.check_value('requires', lambda x: isinstance(x, list))

        d = node.data
        return cls(
            d['name'], d.get('type'), d.get('files'), d.get('requires'),
            str(node.location)
        )
    #-def
#-class

class Template(object):
    """
    """
    __slots__ = [ 'builder', 'components', 'dispatcher' ]

    def __init__(self, builder):
        """
        """

        self.builder = builder
        self.components = []
        self.dispatcher = Dispatcher()
    #-def

    def add(self,)
#-class
