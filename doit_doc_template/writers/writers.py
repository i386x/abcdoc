#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/writers.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2018-08-26 18:09:18 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Sphinx writer classes.\
"""

__license__ = """\
Copyright (c) 2014 - 2018 Jiří Kučera.
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

from docutils.nodes import NodeVisitor
from docutils.writers.html4css1 import Writer

from .core.keywords import KW_END_PAGE, KW_OUTPUT, KW_START_PAGE

class DoItHtmlWriter(Writer):
    """
    """
    __slots__ = ["builder"]

    def __init__(self, builder):
        """
        """

        Writer.__init__(self)
        self.builder = builder
    #-def

    def translate(self):
        """
        """

        self.visitor = visitor = self.builder.create_translator(
            self.builder, self.document
        )
        visitor.start_page()
        self.document.walkabout(visitor)
        visitor.end_page()
        self.output = visitor.astext()
    #-def
#-class

class DoItHtmlTranslator(NodeVisitor):
    """
    """
    __slots__ = ["builder", "dispatcher", "context"]

    def __init__(self, builder, *args, **kwargs):
        """
        """

        NodeVisitor.__init__(self, *args, **kwargs)
        self.builder = builder
        self.dispatcher = self.builder.template.dispatcher
        self.context = {}
    #-def

    def start_page(self):
        """
        """

        self.dispatcher.send(KW_START_PAGE, translator=self)
    #-def

    def end_page(self):
        """
        """

        self.dispatcher.send(KW_END_PAGE, translator=self)
    #-def

    def unknown_visit(self, node):
        """
        """

        self.dispatcher.visit(self, node)
    #-def

    def unknown_departure(self, node):
        """
        """

        self.dispatcher.depart(self, node)
    #-def

    def astext(self):
        """
        """

        return self.context.get(KW_OUTPUT, "")
    #-def
#-class
