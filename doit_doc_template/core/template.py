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

import os

from .component import ComponentSet
from .context import Context
from .dispatcher import Dispatcher
from .info import TemplateInfo
from .keywords import CONFIG_KEYS, KW_BASES
from .layout import LayoutSet
from .library import Library
from .meta import TemplateMeta
from .static import StaticContent
from .utils import read_yaml_file
from .validators import get_and_check, list_of_strings, valid_keys

class Template(object):
    """
    """
    __slots__ = [
        "builder", "bases", "locals", "context", "dispatcher", "components",
        "layouts", "static", "meta", "info", "library"
    ]

    def __init__(self, builder):
        """
        """

        self.builder = builder
        self.bases = []
        self.locals = {}
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

        if templatedir in self.builder.template_stack:
            return self
        self.builder.template_stack.append(templatedir)
        self.locals["_templatedir"] = templatedir
        self.load_config(templatedir)
        self.context.load_from_file(
            os.path.join(templatedir, "context", "main.yml")
        )
        self.dispatcher.load_from_file(
            os.path.join(templatedir, "dispatcher", "main.yml")
        )
        self.components.load_from_file(
            os.path.join(templatedir, "components", "main.yml")
        )
        self.layouts.load_from_file(
            os.path.join(templatedir, "layouts", "main.yml")
        )
        self.static.load_from_file(
            os.path.join(templatedir, "static", "main.yml")
        )
        self.meta.load_from_file(
            os.path.join(templatedir, "meta", "main.yml")
        )
        self.info.load_from_file(
            os.path.join(templatedir, "info", "main.yml")
        )
        self.library.load(templatedir, "library")
        self.builder.template_stack.pop()
        return self
    #-def

    def load_config(self, templatedir):
        """
        """

        config = read_yaml_file(os.path.join(templatedir, "main.yml"))
        if config is None:
            return
        valid_keys(config, CONFIG_KEYS)
        self.load_bases(list_of_strings(get_and_check(config, KW_BASES, [])))
    #-def

    def load_bases(self, bases):
        """
        """

        for base in bases:
            self.bases.append(self.builder.get_template(base))
    #-def

    def setup(self, visited=None):
        """
        """

        if visited is None:
            visited = []
        if self in visited:
            return
        visited.append(self)
        for base in self.bases:
            base.setup(visited)
        self.context.setup()
        self.dispatcher.setup()
        self.components.setup()
        self.library.setup()
        self.context.post_setup()
        return self
    #-def
#-class
