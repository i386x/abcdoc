#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/templates/base/library/__init__.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-06-20 07:30:16 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Base template library.\
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

from .cmd_adduri import cmd_adduri
from .cmd_debug import cmd_debug
from .cmd_newpage import cmd_newpage
from .cmd_pass import cmd_pass
from .cmd_popmark import cmd_popmark
from .cmd_pushlabel import cmd_pushlabel
from .cmd_pushmark import cmd_pushmark
from .cmd_render import cmd_render
from .cmd_skip import cmd_skip
from .type_page import type_page

def load(library):
    """
    """

    library.commands["adduri"] = cmd_adduri
    library.commands["debug"] = cmd_debug
    library.commands["newpage"] = cmd_newpage
    library.commands["pass"] = cmd_pass
    library.commands["popmark"] = cmd_popmark
    library.commands["pushlabel"] = cmd_pushlabel
    library.commands["pushmark"] = cmd_pushmark
    library.commands["render"] = cmd_render
    library.commands["skip"] = cmd_skip
    library.types["page"] = type_page
#-def
