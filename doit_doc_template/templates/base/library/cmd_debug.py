#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/templates/base/library/cmd_debug.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-07-20 19:26:34 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
debug command.\
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

from sphinx.util import logging

from doit_doc_template.core.keywords import KW_NODE

logger = logging.getLogger(__name__)

def p(msg, *args):
    """
    """

    logger.info(msg.format(*args), color="blue")
#-def

def show_node(node):
    """
    """

    p("======== Showing node {} ========", repr(node))
    for attrname in dir(node):
        attr = getattr(node, attrname)
        if not hasattr(attr, "__call__"):
            p("- {}: {}", attrname, repr(attr))
    p("======== Edn of node {} =========", repr(node))
#-def

def cmd_debug(action, context):
    """
    """

    show_node(context.kwargs.get(KW_NODE))
    p("Flattened args: {}", repr(context.evaluate_args(action.flatten_args())))
#-def
