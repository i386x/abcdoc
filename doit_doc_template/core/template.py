#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/core/template.py
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

from .component import ComponentSet
from .context import Context
from .dispatcher import Dispatcher
from .info import TemplateInfo
from .layout import LayoutSet
from .library import Library
from .meta import TemplateMeta
from .static import StaticContent

class Template(object):
    """
    """
    __slots__ = [
        "builder", "bases", "context", "dispatcher", "components", "layouts",
        "static", "meta", "info", "library"
    ]

    def __init__(self, builder):
        """
        """

        self.builder = builder
        self.bases = []
        self.context = Context(self)
        self.dispatcher = Dispatcher(self)
        self.components = ComponentSet(self)
        self.layouts = LayoutSet(self)
        self.static = StaticContent(self)
        self.meta = TemplateMeta(self)
        self.info = TemplateInfo(self)
        self.library = Library(self)
    #-def

    def load(self, templatedir):
        """
        """

        return self
    #-def

    def deploy(self):
        """
        """

        return self
    #-def
#-class
