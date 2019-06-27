#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/core/yaml.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2019-05-18 16:03:58 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Loading YAML files.\
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

import datetime

from yaml import MappingNode, MarkedYAMLError
from yaml.composer import Composer
from yaml.constructor import ConstructorError, SafeConstructor
from yaml.parser import Parser
from yaml.reader import Reader
from yaml.resolver import Resolver
from yaml.scanner import Scanner

class YamlObject(object):
    """
    """

    def __init__(self):
        """
        """

        self.mark = None
    #-def

    def wrap(self, value):
        """
        """

        if isinstance(value, bool):
            data = YamlBool(value)
        elif isinstance(value, int):
            data = YamlInt(value)
        elif isinstance(value, float):
            data = YamlFloat(value)
        elif isinstance(value, bytes):
            data = YamlBytes(value)
        elif isinstance(value, datetime.date):
            data = YamlDate(value.year, value.month, value.day)
        elif isinstance(value, datetime.datetime):
            data = YamlDateTime(
                value.year, value.month, value.day,
                value.hour, value.minute, value.second,
                value.microsecond
            )
        elif isinstance(value, str):
            data = YamlStr(value)
        elif isinstance(value, list):
            data = YamlList(value)
        elif isinstance(value, dict):
            data = YamlDict(value)
        else:
            raise MarkedYAMLError(
                "while wrapping value", self.mark,
                "invalid type of value to wrap ('{}')".format(
                    type(value).__name__
                ),
                self.mark
            )
        data.mark = self.mark
        return data
    #-def
#-class

class YamlBool(YamlObject):
    """
    """
    __slots__ = ["__value"]

    def __init__(self, value):
        """
        """

        YamlObject.__init__(self)
        self.__value = value
    #-def

    def __bool__(self):
        """
        """

        return self.__value
    #-def
#-class

class YamlInt(int, YamlObject):
    """
    """
    __slots__ = []

    def __new__(cls, *args, **kwargs):
        """
        """

        return super(YamlInt, cls).__new__(cls, *args, **kwargs)
    #-def

    def __init__(self, *args, **kwargs):
        """
        """

        int.__init__(self)
        YamlObject.__init__(self)
    #-def
#-class

class YamlFloat(float, YamlObject):
    """
    """
    __slots__ = []

    def __new__(cls, *args, **kwargs):
        """
        """

        return super(YamlFloat, cls).__new__(cls, *args, **kwargs)
    #-def

    def __init__(self, *args, **kwargs):
        """
        """

        float.__init__(self)
        YamlObject.__init__(self)
    #-def
#-class

class YamlBytes(bytes, YamlObject):
    """
    """
    __slots__ = []

    def __new__(cls, *args, **kwargs):
        """
        """

        return super(YamlBytes, cls).__new__(cls, *args, **kwargs)
    #-def

    def __init__(self, *args, **kwargs):
        """
        """

        bytes.__init__(self)
        YamlObject.__init__(self)
    #-def
#-class

class YamlDate(datetime.date, YamlObject):
    """
    """
    __slots__ = []

    def __init__(self, *args, **kwargs):
        """
        """

        datetime.date.__init__(self, *args, **kwargs)
        YamlObject.__init__(self)
    #-def
#-class

class YamlDateTime(datetime.datetime, YamlObject):
    """
    """
    __slots__ = []

    def __init__(self, *args, **kwargs):
        """
        """

        datetime.datetime.__init__(self, *args, **kwargs)
        YamlObject.__init__(self)
    #-def
#-class

class YamlStr(str, YamlObject):
    """
    """
    __slots__ = []

    def __new__(cls, *args, **kwargs):
        """
        """

        return super(YamlStr, cls).__new__(cls, *args, **kwargs)
    #-def

    def __init__(self, *args, **kwargs):
        """
        """

        str.__init__(self)
        YamlObject.__init__(self)
    #-def
#-class

class YamlList(list, YamlObject):
    """
    """
    __slots__ = []

    def __init__(self, *args, **kwargs):
        """
        """

        list.__init__(self, *args, **kwargs)
        YamlObject.__init__(self)
    #-def
#-class

class YamlDict(dict, YamlObject):
    """
    """
    __slots__ = []

    def __init__(self, *args, **kwargs):
        """
        """

        dict.__init__(self, *args, **kwargs)
        YamlObject.__init__(self)
    #-def
#-class

class YamlConstructor(SafeConstructor):
    """
    """
    __slots__ = ["__filename"]

    def __init__(self, filename=None):
        """
        """

        SafeConstructor.__init__(self)
        self.__filename = filename
    #-def

    def construct_yaml_null(self, node):
        """
        """

        mark = node.start_mark
        if self.__filename is not None:
            mark.name = self.__filename
        raise ConstructorError(
            "while constructing", mark,
            "null values are forbidden by the customized YAML loader", mark
        )
    #-def

    def construct_yaml_bool(self, node):
        """
        """

        data = YamlBool(SafeConstructor.construct_yaml_bool(self, node))
        mark = node.start_mark
        if self.__filename is not None:
            mark.name = self.__filename
        data.mark = mark
        return data
    #-def

    def construct_yaml_int(self, node):
        """
        """

        data = YamlInt(SafeConstructor.construct_yaml_int(self, node))
        mark = node.start_mark
        if self.__filename is not None:
            mark.name = self.__filename
        data.mark = mark
        return data
    #-def

    def construct_yaml_float(self, node):
        """
        """

        data = YamlFloat(SafeConstructor.construct_yaml_float(self, node))
        mark = node.start_mark
        if self.__filename is not None:
            mark.name = self.__filename
        data.mark = mark
        return data
    #-def

    def construct_yaml_binary(self, node):
        """
        """

        data = YamlBytes(SafeConstructor.construct_yaml_binary(self, node))
        mark = node.start_mark
        if self.__filename is not None:
            mark.name = self.__filename
        data.mark = mark
        return data
    #-def

    def construct_yaml_timestamp(self, node):
        """
        """

        timestamp = SafeConstructor.construct_yaml_timestamp(self, node)
        if isinstance(timestamp, datetime.date):
            data = YamlDate(timestamp.year, timestamp.month, timestamp.day)
        else:
            data = YamlDateTime(
                timestamp.year, timestamp.month, timestamp.day,
                timestamp.hour, timestamp.minute, timestamp.second,
                timestamp.microsecond
            )
        mark = node.start_mark
        if self.__filename is not None:
            mark.name = self.__filename
        data.mark = mark
        return data
    #-def

    def construct_yaml_omap(self, node):
        """
        """

        mark = node.start_mark
        if self.__filename is not None:
            mark.name = self.__filename
        raise ConstructorError(
            "while constructing", mark,
            "ordered maps are not supported by the customized YAML loader,"
            " please use an ordinary map", mark
        )
    #-def

    def construct_yaml_pairs(self, node):
        """
        """

        mark = node.start_mark
        if self.__filename is not None:
            mark.name = self.__filename
        raise ConstructorError(
            "while constructing", mark,
            "pairs are not supported by the customized YAML loader,"
            " please use a list of maps", mark
        )
    #-def

    def construct_yaml_set(self, node):
        """
        """

        mark = node.start_mark
        if self.__filename is not None:
            mark.name = self.__filename
        raise ConstructorError(
            "while constructing", mark,
            "sets are not supported by the customized YAML loader,"
            " please use an ordinary map", mark
        )
    #-def

    def construct_yaml_str(self, node):
        """
        """

        data = YamlStr(SafeConstructor.construct_yaml_str(self, node))
        mark = node.start_mark
        if self.__filename is not None:
            mark.name = self.__filename
        data.mark = mark
        return data
    #-def

    def construct_yaml_seq(self, node):
        """
        """

        data = YamlList([])
        yield data
        data.extend(self.construct_sequence(node))
        mark = node.start_mark
        if self.__filename is not None:
            mark.name = self.__filename
        data.mark = mark
    #-def

    def construct_yaml_map(self, node):
        """
        """

        data = YamlDict({})
        yield data
        data.update(self.construct_mapping(node))
        mark = node.start_mark
        if self.__filename is not None:
            mark.name = self.__filename
        data.mark = mark
    #-def

    def construct_yaml_object(self, node):
        """
        """

        mark = node.start_mark
        if self.__filename is not None:
            mark.name = self.__filename
        raise ConstructorError(
            "while constructing", mark,
            "constructing arbitrary objects is not supported by the customized"
            " YAML loader", mark
        )
    #-def

    def construct_mapping(self, node, deep=False):
        """
        """

        mark = node.start_mark
        if self.__filename is not None:
            mark.name = self.__filename
        if not isinstance(node, MappingNode):
            raise ConstructorError(
                None, None,
                "expected a mapping node, but found {}".format(node.id), mark
            )
        self.flatten_mapping(node)
        mapping = YamlDict({})
        mapping.mark = mark
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise ConstructorError(
                    "while constructing a mapping", mark,
                    "found unacceptable key ({})".format(str(exc)),
                    key_node.start_mark
                )
            if key in mapping:
                raise ConstructorError(
                    "while constructing a mapping", mark,
                    "found a duplicate dict key ({})".format(str(key)),
                    key_node.start_mark
                )
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping
    #-def
#-class

YamlConstructor.add_constructor(
    "tag:yaml.org,2002:null",
    YamlConstructor.construct_yaml_null
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:python/none",
    YamlConstructor.construct_yaml_null
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:bool",
    YamlConstructor.construct_yaml_bool
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:python/bool",
    YamlConstructor.construct_yaml_bool
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:int",
    YamlConstructor.construct_yaml_int
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:python/int",
    YamlConstructor.construct_yaml_int
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:float",
    YamlConstructor.construct_yaml_float
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:python/float",
    YamlConstructor.construct_yaml_float
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:binary",
    YamlConstructor.construct_yaml_binary
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:timestamp",
    YamlConstructor.construct_yaml_timestamp
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:omap",
    YamlConstructor.construct_yaml_omap
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:pairs",
    YamlConstructor.construct_yaml_pairs
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:set",
    YamlConstructor.construct_yaml_set
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:str",
    YamlConstructor.construct_yaml_str
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:python/str",
    YamlConstructor.construct_yaml_str
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:python/unicode",
    YamlConstructor.construct_yaml_str
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:seq",
    YamlConstructor.construct_yaml_seq
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:python/list",
    YamlConstructor.construct_yaml_seq
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:map",
    YamlConstructor.construct_yaml_map
)
YamlConstructor.add_constructor(
    "tag:yaml.org,2002:python/dict",
    YamlConstructor.construct_yaml_map
)

class YamlLoader(Reader, Scanner, Parser, Composer, YamlConstructor, Resolver):
    """
    """
    __slots__ = []

    def __init__(self, stream, filename=None):
        """
        """

        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        YamlConstructor.__init__(self, filename)
        Resolver.__init__(self)
    #-def
#-class
