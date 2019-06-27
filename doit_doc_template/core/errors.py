#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/core/errors.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-04-22 21:10:16 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Exception classes and error reporting.\
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

from sphinx.errors import ExtensionError

class InternalError(ExtensionError):
    """
    """
    __slots__ = []

    def __init__(self, filename, location, detail):
        """
        """

        ExtensionError.__init__(self, "[INTERNAL ERROR] <{}>::{}: {}.".format(
            os.path.realpath(filename), location, detail
        ))
    #-def
#-class

class ReadFileError(ExtensionError):
    """
    """
    __slots__ = []

    def __init__(self, filename):
        """
        """

        ExtensionError.__init__(
            self, "The content of <{}> cannot be read.".format(filename)
        )
    #-def
#-class

class YamlError(ExtensionError):
    """
    """
    __slots__ = []

    def __init__(self, error):
        """
        """

        ExtensionError.__init__(self, "Error {}".format(str(error)))
    #-def
#-class

class YamlDataFormatError(YamlError):
    """
    """
    __slots__ = []

    def __init__(self, error):
        """
        """

        YamlError.__init__(self, error)
    #-def
#-class

class CyclicDependencyError(ExtensionError):
    """
    """
    __slots__ = []

    def __init__(self, template, where):
        """
        """

        ExtensionError.__init__(
            self, "In {} template {}: cyclic dependencies detected.".format(
                template.locals["_templatedir"], where
            )
        )
    #-def
#-class

class DispatcherError(ExtensionError):
    """
    """
    __slots__ = []

    def __init__(self, detail):
        """
        """

        ExtensionError.__init__(self, detail)
    #-def
#-class

class UnhandledEventError(DispatcherError):
    """
    """
    __slots__ = []

    def __init__(self, event):
        """
        """

        DispatcherError.__init__(self, "Unhandled event '{}'.".format(event))
    #-def
#-class

class CommandNotFoundError(ExtensionError):
    """
    """
    __slots__ = []

    def __init__(self, name):
        """
        """

        mark = name.mark
        ExtensionError.__init__(
            self, "In <{}>, line {}, column {}: Unknown command: {}.".format(
                mark.name, mark.line + 1, mark.column + 1, name
            )
        )
    #-def
#-class
