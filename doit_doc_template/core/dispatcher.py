#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/core/dispatcher.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-04-20 13:42:49 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Dispatcher.\
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

from .action import Action
from .errors import UnhandledEventError
from .keywords import ACTION_KEYS, KW_ACTION, KW_ARGS
from .utils import read_yaml_file
from .validators import \
    expect_type, get_and_check, invalid_data, valid_keys

class Dispatcher(object):
    """
    """
    __slots__ = ["template", "handlers"]

    def __init__(self, template):
        """
        """

        self.template = template
        self.handlers = {}
    #-def

    def handle_event(self, name, context):
        """
        """

        if name not in self.handlers:
            raise UnhandledEventError(name)
        self.handlers[name](context)
    #-def

    def load_from_file(self, filename):
        """
        """

        data = read_yaml_file(filename)
        if data is None:
            return
        expect_type(data, dict)
        for k in data:
            expect_type(k, str)
            self.handlers[k] = self.compile_handler(data, k)
    #-def

    @classmethod
    def compile_handler(cls, data, name):
        """
        """

        if not name.startswith("visit_") \
        or not name.startswith("depart_") \
        or not name.endswith("_hook"):
            invalid_data(data, "invalid handler name '{}'".format(name))
        return cls.compile_handler_body(get_and_check(data, name, [], list))
    #-def

    @classmethod
    def compile_handler_body(cls, body):
        """
        """

        return [cls.compile_handler_action(a) for a in body]
    #-def

    @classmethod
    def compile_handler_action(cls, action):
        """
        """

        if isinstance(action, str):
            return Action(action)
        if not isinstance(action, dict):
            invalid_data(action, "action should be string or dictionary")
        # dictionary (one item)
        if len(action) == 1:
            name = list(action)[0]
            args = get_and_check(action, name)
            expect_type(name, str)
            return Action(name, args)
        # dictionary (more items)
        with valid_keys(action, ACTION_KEYS) as vk:
            vk(KW_ACTION).is_required
        name = get_and_check(action, KW_ACTION, value_type=str)
        args = get_and_check(action, KW_ARGS)
        return Action(name, args)
    #-def
#-class
