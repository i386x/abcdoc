#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/core/keywords.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-05-18 12:06:12 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
String constants.\
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

KW_ACTION = "action"
KW_ARE_REQUIRED = "are_required"
KW_ARGS = "args"
KW_BASES = "bases"
KW_DEPENDENCIES = "dependencies"
KW_FROM = "from"
KW_IS_REQUIRED = "is_required"
KW_JUST_ONE_IS_REQUIRED = "just_one_is_required"
KW_LAYOUT = "layout"
KW_NAME = "name"
KW_PARAMETERS = "parameters"
KW_RENDER = "render"
KW_VARIABLES = "variables"

ACTION_KEYS = (KW_ACTION, KW_ARGS)
COMPONENT_KEYS = (KW_DEPENDENCIES, KW_FROM, KW_NAME, KW_PARAMETERS, KW_RENDER)
CONFIG_KEYS = (KW_BASES,)
CONTEXT_KEYS = (KW_VARIABLES,)
LAYOUT_KEYS = (KW_FROM, KW_LAYOUT, KW_NAME, KW_PARAMETERS)
