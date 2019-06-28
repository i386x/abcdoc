#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/core/layout.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-06-14 23:29:15 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Layout set holder.\
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

from .keywords import KW_FROM, KW_LAYOUT, KW_NAME, KW_PARAMETERS, LAYOUT_KEYS
from .utils import read_yaml_file
from .validators import expect_type, get_and_check, list_of_strings, valid_keys

class Layout(object):
    """
    """
    __slots__ = ["name", "params"]

    def __init__(self, name, params=None):
        """
        """

        self.name = name
        self.params = list_of_strings(params, unique=True) or name.wrap([])
    #-def
#-class

class LayoutFromFile(Layout):
    """
    """
    __slots__ = ["filename"]

    def __init__(self, name, params, filename):
        """
        """

        Layout.__init__(self, name, params)
        self.filename = filename
    #-def
#-class

class LayoutFromString(Layout):
    """
    """
    __slots__ = ["layout"]

    def __init__(self, name, params, layout):
        """
        """

        Layout.__init__(self, name, params)
        self.layout = layout
    #-def
#-class

class LayoutSet(object):
    """
    """
    __slots__ = ["template", "layouts"]

    def __init__(self, template):
        """
        """

        self.template = template
        self.layouts = {}
    #-def

    def load_from_file(self, filename):
        """
        """

        data = read_yaml_file(filename)
        if data is None:
            return
        expect_type(data, list)
        for l in data:
            layout = LayoutSet.compile_layout(l)
            self.layouts[layout.name] = layout
    #-def

    @classmethod
    def compile_layout(cls, layout):
        """
        """

        with valid_keys(layout, LAYOUT_KEYS) as vk:
            vk(KW_NAME).is_required
            vk(KW_FROM, KW_LAYOUT).just_one_is_required
        # name
        name = get_and_check(layout, KW_NAME, value_type=str)
        # parameters
        params = get_and_check(layout, KW_PARAMETERS)
        # either 'from' or 'layout'
        if KW_FROM in layout:
            layout_file = get_and_check(layout, KW_FROM, value_type=str)
            return LayoutFromFile(name, params, layout_file)
        layout_string = get_and_check(layout, KW_LAYOUT, value_type=str)
        return LayoutFromString(name, params, layout_string)
    #-def
#-class
