#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/templates/base/library/cmd_render.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-06-29 23:19:44 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
render command.\
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

from doit_doc_template.core.errors import ComponentNotFoundError
from doit_doc_template.core.keywords import KW__0

def parse_args(args):
    """
    """

    name = list(args)[0]
    params = args[name]
    if isinstance(params, str):
        params = params.wrap([params])
    return name, params
#-def

def cmd_render(action, context):
    """
    """

    name, args = parse_args(action.args)
    template = context.template
    renderer = template.components.get_wrapper(name)
    if renderer is None:
        raise ComponentNotFoundError(name)
    args = context.evaluate_args(args)
    context.setvar(KW__0, renderer(*args))
#-def
