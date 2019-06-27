#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/core/validators.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-05-18 16:23:03 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Data validators.\
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

from yaml import MarkedYAMLError

from .errors import InternalError, YamlDataFormatError
from .keywords import KW_ARE_REQUIRED, KW_IS_REQUIRED, KW_JUST_ONE_IS_REQUIRED
from .utils import \
    caller_name, intersect, typename_from_data, typename_from_type

def check_subset(set_a, set_b, fail_action, *args, **kwargs):
    """
    """

    for x in set_a:
        if x not in set_b:
            fail_action(x, *args, **kwargs)
#-def

def invalid_data(data, detail):
    """
    """

    raise YamlDataFormatError(
        MarkedYAMLError("while verifying data", data.mark, detail, data.mark)
    )
#-def

def expect_type(data, data_type):
    """
    """

    if not isinstance(data, data_type):
        invalid_data(
            data,
            "expected {}, but found {}".format(
                typename_from_type(data_type), typename_from_data(data)
            )
        )
#-def

def get_and_check(data, key, default=None, value_type=None):
    """
    """

    value = data.get(key)
    # Missing item means use default value
    if value is None:
        if default is None:
            return None
        value = data.wrap(default)
    # 'None' means no type checking
    if value_type is None:
        return value
    if value is None:
        invalid_data(data, "key '{}' holds no value".format(key))
    expect_type(value, value_type)
    return value
#-def

def param_specfunc(item):
    """
    """

    if isinstance(item, str):
        return item
    if not isinstance(item, dict):
        invalid_data(
            item,
            "expected string or dictionary, but found {}".format(
                typename_from_data(item)
            )
        )
    if len(item) != 1:
        invalid_data(item, "expected dictionary of length 1")
    param_name = list(item)[0]
    param_type = item[param_name]
    expect_type(param_name, str)
    expect_type(param_type, str)
    return param_name
#-def

def string_specfunc(item):
    """
    """

    if not isinstance(item, str):
        invalid_data(
            item,
            "expected string, but found {}".format(typename_from_data(item))
        )
    return item
#-def

def list_of(data, specfunc, unique=False, **kwargs):
    """
    """

    if data is None:
        return None
    expect_type(data, list)
    unique_items = []
    for item in data:
        item_name = specfunc(item, **kwargs)
        if unique and item_name in unique_items:
            invalid_data(item, "duplicit '{}'".format(item_name))
        if item_name not in unique_items:
            unique_items.append(item_name)
    return data
#-def

def list_of_params(data, unique=True):
    """
    """

    return list_of(data, param_specfunc, unique=unique)
#-def

def list_of_strings(data, unique=False):
    """
    """

    return list_of(data, string_specfunc, unique=unique)
#-def

class KeyValidatorHelper(object):
    """
    """
    __slots__ = ["kvobj", "keylist"]

    def __init__(self, kvobj, keylist):
        """
        """

        self.kvobj = kvobj
        self.keylist = keylist
        check_subset(self.keylist, self.kvobj.valid_keys, self.__invalid_key)
    #-def

    def __getattr__(self, name):
        """
        """

        if name in (KW_IS_REQUIRED, KW_ARE_REQUIRED):
            return self._is_required()
        elif name == KW_JUST_ONE_IS_REQUIRED:
            return self._just_one_is_required()
        return object.__getattribute__(self, name)
    #-def

    def _is_required(self):
        """
        """

        check_subset(self.keylist, self.kvobj.data, self.__missing_key)
    #-def

    def _just_one_is_required(self):
        """
        """

        if len(intersect(self.keylist, self.kvobj.data)) != 1:
            invalid_data(
                self.kvobj.data,
                "just one key from {} is required".format(self.keylist)
            )
    #-def

    def can_be_only_with(self, *args):
        """
        """

        check_subset(args, self.valid_keys, self.__invalid_key)
        if len(intersect(self.keylist, self.kvobj.data)) == 0:
            return
        keys = self.keylist + args
        check_subset(self.kvobj.data, keys, self.__conflicting_keys, keys)
    #-def

    def __invalid_key(self, key):
        """
        """

        raise InternalError(
            __file__, caller_name(1, self.__class__),
            "key '{}' is not a valid key of 'kvobj.data'".format(key)
        )
    #-def

    def __missing_key(self, key):
        """
        """

        invalid_data(
            self.kvobj.data, "required key '{}' is missing".format(key)
        )
    #-def

    def __conflicting_keys(self, key, keys):
        """
        """

        invalid_data(
            self.kvobj.data,
            "key '{}' cannot be together with {}".format(key, keys)
        )
    #-def
#-class

class KeyValidator(object):
    """
    """
    __slots__ = ["data", "valid_keys"]

    def __init__(self, data, valid_keys):
        """
        """

        expect_type(data, dict)
        self.data = data
        self.valid_keys = valid_keys
        check_subset(self.data, self.valid_keys, self.__invalid_key)
    #-def

    def __enter__(self):
        """
        """

        return self
    #-def

    def __exit__(self, exc_type, exc_value, traceback):
        """
        """

        pass
    #-def

    def __call__(self, *args):
        """
        """

        return KeyValidatorHelper(self, args)
    #-def

    def __invalid_key(self, key):
        """
        """

        invalid_data(self.data, "invalid key '{}'".format(key))
    #-def
#-class

valid_keys = KeyValidator
