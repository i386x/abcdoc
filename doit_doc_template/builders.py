#                                                         -*- coding: utf-8 -*-
#! \file    ~/doit_doc_template/builders.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2018-08-26 14:39:35 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Sphinx builder classes.\
"""

__license__ = """\
Copyright (c) 2014 - 2018 Jiří Kučera.
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

from docutils.frontend import OptionParser
from docutils.io import FileOutput

from sphinx.builders import Builder
from sphinx.errors import ExtensionError
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.osutil import SEP

from .core.keywords import KW_VARIABLES
from .core.utils import get_config_value, Importer
from .writers import DoItHtmlTranslator, DoItHtmlWriter

logger = logging.getLoger(__name__)

builtin_templates_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file)), "templates"
)

class DoItHtmlBuilder(Builder):
    """
    """
    name = "doit-html"
    format = "html"
    epilog = "The HTML pages are in %(outdir)s."

    out_suffix = ".html"
    default_translator_class = DoItHtmlTranslator
    supported_image_types = ["image/png"]

    __slots__ = [
        "context", "template_cache", "template", "docwriter", "docsettings"
    ]

    def __init__(self, app):
        """
        """

        Builder.__init__(self, app)
    #-def

    def init(self):
        """
        """

        self.context = {}
        self.template_cache = {}
        self.template = None
        self.docwriter = None
        self.docsettings = None
    #-def

    def get_outdated_docs(self):
        """
        """

        for docname in self.env.found_docs:
            yield docname
    #-def

    def get_target_uri(self, docname, typ=None):
        """
        """

        if docname == "index":
            return ""
        if docname.endswith(SEP + "index"):
            return docname[:-5]
        return docname + SEP
    #-def

    def prepare_writing(self, docnames):
        """
        """

        self.init_variables()
        self.get_template()
        self.docwriter = DoItHtmlWriter(self)
        self.docsettings = OptionParser(
            defaults = self.env.settings,
            components = (self.docwriter,),
            read_config_files = True
        ).get_default_values()
        self.template.deploy()
    #-def

    def write_doc(self, docname, doctree):
        """
        """

        html_file_suffix = self.get_builder_config("file_suffix", "html")

        if html_file_suffix is not None:
            self.out_suffix = html_file_suffix

        docfile = docname + self.out_suffix
        destination = FileOutput(
            destination_path = os.path.join(self.outdir, docfile),
            encoding = "utf-8"
        )
        doctree.settings = self.docsettings
        self.docwriter.write(doctree, destination)
    #-def

    def finish(self):
        """
        """

        pass
    #-def

    def init_variables(self):
        """
        """

        app = self.app
        srcdir = app.srcdir
        config = app.config

        templates_path = get_config_value(config, "templates_path") or []
        html_theme_path = self.get_builder_config("theme_path", "html") or []
        templates_path = html_theme_path + templates_path
        templates_path = [os.path.join(srcdir, p) for p in templates_path]
        templates_path.append(builtin_templates_dir)

        html_theme = self.get_builder_config("theme", "html")

        if not html_theme:
            logger.warning(__("HTML theme is not specified, using default."))
            html_theme = "default"

        self.context[KW_VARIABLES] = dict(
            _srcdir = srcdir,
            _outdir = app.outdir,
            _config = config,
            _path = templates_path,
            _name = html_theme
        )
    #-def

    def get_template(self, name=None):
        """
        """

        variables = self.context[KW_VARIABLES]

        if name is None:
            name = variables["_name"]

        if name in self.template_cache:
            self.template = self.template_cache[name]
            return

        self.template = self.load_template(variables["_path"], name)
        if self.template is None:
            raise ExtensionError("Template '{}' was not found.".format(name))

        self.template_cache[name] = self.template
    #-def

    def load_template(self, path, name):
        """
        """

        with Importer(path, False):
            module = __import__(name, None, None, ["load"])
            if hasattr(module, "load"):
                return module.load(self)
        return None
    #-def
#-class
