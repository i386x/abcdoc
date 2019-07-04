#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/core/action.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-05-18 20:02:25 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Handler action.\
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

from .errors import CommandNotFoundError
from .utils import dictmerge

class ActionContext(object):
    """
    """
    __slots__ = ["handler", "template", "kwargs", "variables"]

    def __init__(self, handler, template, kwargs):
        """
        """

        self.handler = handler
        self.template = template
        self.kwargs = kwargs
        self.variables = {}
    #-def

    def getvar(self, name, default=None):
        """
        """

        return self.variables.get(name, default)
    #-def

    def setvar(self, name, value):
        """
        """

        self.variables[name] = value
    #-def

    def evaluate_args(self, args):
        """
        """

        tctx = self.template.context
        j2env = tctx.j2env
        j2context = tctx.j2context
        trcontext = self.template.builder.docwriter.visitor.context
        ctx = dictmerge(j2context, self.kwargs, trcontext)
        f = lambda x: (
            self.variables.get(x) if x in self.variables else (
                j2env.from_string(x).render(ctx) if isinstance(x, str) else x
            )
        )
        return [f(x) for x in args]
    #-def
#-class

class Action(object):
    """
    """
    __slots__ = ["name", "args"]

    def __init__(self, name, args=None):
        """
        """

        self.name = name
        self.args = args
    #-def

    def __call__(self, context):
        """
        """

        library = context.handler.dispatcher.template.library
        command = library.get_command(self.name)
        if command is None:
            raise CommandNotFoundError(self.name)
        command(self, context)
    #-def
#-class
