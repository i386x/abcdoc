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

from .keywords import \
    COMPONENT_KEYS, KW_DEPENDENCIES, KW_FROM, KW_NAME, KW_PARAMETERS, KW_RENDER
from .utils import read_yaml_file
from .validators import \
    expect_type, get_and_check, list_of_params, list_of_strings, valid_keys

class Component(object):
    """
    """
    __slots__ = ["name"]

    def __init__(self, name):
        """
        """

        self.name = name
    #-def
#-class

class ImportedComponent(Component):
    """
    """
    __slots__ = ["source"]

    def __init__(self, name, source):
        """
        """

        Component.__init__(self, name)
        self.source = source
    #-def
#-class

class DefinedComponent(Component):
    """
    """
    __slots__ = ["template", "params", "deps"]

    def __init__(self, name, template, params=None, deps=None):
        """
        """

        Component.__init__(self, name)
        self.template = template
        self.params = list_of_params(params) or name.wrap([])
        self.deps = list_of_strings(deps, unique=True) or name.wrap([])
    #-def
#-class

class ComponentSet(object):
    """
    """
    __slots__ = ["template", "components"]

    def __init__(self, template):
        """
        """

        self.template = template
        self.components = {}
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
            return ImportedComponent(name, source)
        template = get_and_check(component, KW_RENDER, value_type=str)
        params = get_and_check(component, KW_PARAMETERS)
        deps = get_and_check(component, KW_DEPENDENCIES)
        return DefinedComponent(name, template, params, deps)
    #-def
#-class
