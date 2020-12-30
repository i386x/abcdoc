#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/templates/base/library/type_page.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-07-04 09:41:22 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Page type.\
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

from sphinx.errors import ExtensionError

from doit_doc_template.core.errors import BadTypeError
from doit_doc_template.core.utils import simplerep

class PageStackError(ExtensionError):
    """
    """
    message = "Page element stack corrupted: {}."
    bad_mark_message = "Element '{}' is not identical with mark '{}'"
    no_mark_message = "Hitting the stack bottom while waiting for '{}' mark"
    __slots__ = []

    def __init__(self, detail):
        """
        """

        ExtensionError.__init__(self, message.format(detail))
    #-def

    @classmethod
    def bad_mark(cls, elem, mark):
        """
        """

        return cls(bad_mark_message.format(simplerep(elem), simplerep(mark)))
    #-def

    @classmethod
    def no_mark(cls, mark):
        """
        """

        return cls(no_mark_message.format(simplerep(mark)))
    #-def
#-class

class Page(object):
    """
    """
    __slots__ = ["urimap", "pending_labels", "stack"]

    def __init__(self):
        """
        """

        self.urimap = {}
        self.pending_labels = []
        self.stack = []
    #-def

    def adduri(self, name, uri):
        """
        """

        self.urimap[name] = uri
    #-def

    def pushlabel(self, label):
        """
        """

        self.pending_labels.append(label)
    #-def

    def pushmark(self, mark):
        """
        """

        self.stack.append(mark)
    #-def

    def popmark(self, mark, markcls):
        """
        """

        result = []
        while self.stack:
            elem = self.stack.pop()
            if elem is mark:
                return result
            if isinstance(elem, markcls):
                raise PageStackError.bad_mark(elem, mark)
            result.append(elem)
        raise PageStackError.no_mark(mark)
    #-def
#-class

def type_page(param, obj):
    """
    """

    if not isinstance(obj, Page):
        raise BadTypeError(param, obj, Page)
    return obj
#-def
