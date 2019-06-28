#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/core/context.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-05-18 21:07:38 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Context definition holder.\
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

from jinja2 import Template

from .errors import CyclicDependencyError
from .keywords import CONTEXT_KEYS, KW_VARIABLES
from .utils import ensure_key, get_jinja2_template_variables, read_yaml_file
from .validators import expect_type, get_and_check, valid_keys

class Context(object):
    """
    """
    __slots__ = ["template", "variables"]

    def __init__(self, template):
        """
        """

        self.template = template
        self.variables = {}
    #-def

    def load_from_file(self, filename):
        """
        """

        data = read_yaml_file(filename)
        if data is None:
            return
        valid_keys(data, CONTEXT_KEYS)
        variables = get_and_check(data, KW_VARIABLES, {}, dict)
        for v in variables:
            expect_type(v, str)
            self.variables[v] = variables[v]
    #-def

    def resolve_variables(self):
        """
        """

        context = {}
        context.update(self.template.builder.context[KW_VARIABLES])
        context.update(self.template.locals)
        vardeps = dict([(x, set()) for x in self.variables])
        for u in self.variables:
            for v in get_jinja2_template_variables(self.variables[u]):
                if v in self.variables:
                    vardeps[u].add(v)
        while vardeps:
            leaves = set()
            for v in vardeps:
                if not vardeps[v]:
                    value = self.variables[v]
                    if isinstance(value, str):
                        value = Template(value).render(context)
                        self.variables[v] = value
                    context[v] = value
                    leaves.add(v)
            if not leaves:
                raise CyclicDependencyError(self.template, "variables")
            for l in leaves:
                del vardeps[l]
            for v in vardeps:
                vardeps[v] -= leaves
    #-def

    def get_variable(self, name):
        """
        """

        if name in self.template.locals:
            return self.template.locals[name]
        return self.template.builder.context[KW_VARIABLES].get(name)
    #-def

    def deploy_variables(self, force=False):
        """
        """

        context = self.template.builder.context
        ensure_key(context, KW_VARIABLES, {})
        variables = context.get(KW_VARIABLES)
        for var in self.variables:
            ensure_key(variables, var, self.variables[var], force)
    #-def
#-class
