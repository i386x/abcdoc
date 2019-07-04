#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/core/component.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-05-18 22:41:36 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Component set holder.\
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

from .errors import \
    ArgumentCountError, ComponentNotFoundError, TypeNotFoundError
from .keywords import \
    COMPONENT_KEYS, KW_DEPENDENCIES, KW_FROM, KW_NAME, KW_PARAMETERS, KW_RENDER
from .utils import dictmerge, read_yaml_file, resolve_path, Importer
from .validators import \
    expect_type, get_and_check, list_of_params, list_of_strings, valid_keys

class Component(object):
    """
    """
    __slots__ = ["container", "name"]

    def __init__(self, container, name):
        """
        """

        self.container = container
        self.name = name
    #-def
#-class

class ImportedComponent(Component):
    """
    """
    __slots__ = ["source"]

    def __init__(self, container, name, source):
        """
        """

        Component.__init__(self, container, name)
        self.source = source
    #-def
#-class

class DefinedComponent(Component):
    """
    """
    __slots__ = ["template", "params", "deps"]

    def __init__(self, container, name, template, params=None, deps=None):
        """
        """

        Component.__init__(self, container, name)
        self.template = template
        self.params = list_of_params(params) or name.wrap([])
        self.deps = list_of_strings(deps, unique=True) or name.wrap([])
    #-def
#-class

class ComponentSet(object):
    """
    """
    __slots__ = ["template", "components", "wrappers", "rbases"]

    def __init__(self, template):
        """
        """

        self.template = template
        self.components = {}
        self.wrappers = {}
        self.rbases = []
    #-def

    def setup(self):
        """
        """

        self.rbases.extend(self.template.bases)
        self.rbases.reverse()
    #-def

    def get_component(self, name, visited=None):
        """
        """

        if visited is None:
            visited = []
        if self in visited:
            return None
        visited.append(self)
        if name in self.components:
            return self.components[name]
        for base in self.rbases:
            component = base.get_component(name, visited)
            if component:
                return component
        return None
    #-def

    def get_wrapper(self, name):
        """
        """

        if name in self.wrappers:
            return self.wrappers[name]
        closure = self.compute_closure(name)
        for c in closure:
            self.create_wrapper(c)
        return self.wrappers.get(name)
    #-def

    def compute_closure(self, name):
        """
        """

        closure = []
        workset = [name]
        while workset:
            n = workset.pop(0)
            c = self.get_component(n)
            if c is None:
                raise ComponentNotFoundError(n)
            if c in closure:
                continue
            if isinstance(c, DefinedComponent):
                workset.extend(c.deps)
            closure.append(c)
        return closure
    #-def

    def create_wrapper(self, component):
        """
        """

        context = component.container.template.context
        j2env = context.j2env
        j2context = context.j2context
        name = component.name
        wrappers = self.wrappers
        if isinstance(component, ImportedComponent):
            path = resolve_path(
                j2env.from_string(component.source).render(j2context)
            )
            with Importer([path], False):
                module = __import__(".", None, None, [name])
                if hasattr(module, name):
                    wrappers[name] = getattr(module, name)
        elif isinstance(component, DefinedComponent):
            template = component.template
            paramspec = self.make_paramspec(component)
            def wrapper(*args):
                params = paramspec(*args)
                return j2env.from_string(template).render(
                    dictmerge(j2context, wrappers, params)
                )
            wrappers[name] = wrapper
    #-def

    def make_paramspec(self, component):
        """
        """

        name = component.name
        library = component.container.template.library
        params = []
        for p in component.params:
            pname = list(p)[0]
            ptype = library.get_type(p[pname])
            if ptype is None:
                raise TypeNotFoundError(p[pname])
            params.append((pname, ptype))
        nparams = len(params)
        def paramspec(*args):
            pvars = {}
            nargs = len(args)
            if nargs != nparams:
                raise ArgumentCountError(name, nparams, nargs)
            i = 0
            while i < nargs:
                p, t = params[i]
                pvars[p] = t(args[i])
                i += 1
            return pvars
        return paramspec
    #-def

    def load_from_file(self, filename):
        """
        """

        data = read_yaml_file(filename)
        if data is None:
            return
        expect_type(data, list)
        for c in data:
            component = ComponentSet.compile_component(c)
            self.components[component.name] = component
    #-def

    @classmethod
    def compile_component(cls, component):
        """
        """

        with valid_keys(component, COMPONENT_KEYS) as vk:
            vk(KW_NAME).is_required
            vk(KW_FROM, KW_RENDER).just_one_is_required
            vk(KW_FROM).can_be_only_with(KW_NAME)
        # name
        name = get_and_check(component, KW_NAME, value_type=str)
        # either 'from' or 'render'
        if KW_FROM in component:
            source = get_and_check(component, KW_FROM, value_type=str)
            return ImportedComponent(self, name, source)
        template = get_and_check(component, KW_RENDER, value_type=str)
        params = get_and_check(component, KW_PARAMETERS)
        deps = get_and_check(component, KW_DEPENDENCIES)
        return DefinedComponent(self, name, template, params, deps)
    #-def
#-class
