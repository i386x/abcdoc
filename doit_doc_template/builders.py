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
import sys

from docutils.frontend import OptionParser
from docutils.io import FileOutput

from sphinx.builders import Builder
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.osutil import SEP

from .writers import DoItHtmlTranslator, DoItHtmlWriter

logger = logging.getLoger(__name__)

class DoItHtmlBuilder(Builder):
    """
    """
    name = 'doit-html'
    format = 'html'
    epilog = "The HTML pages are in %(outdir)s."

    out_suffix = '.html'
    default_translator_class = DoItHtmlTranslator
    supported_image_types = [ 'image/png' ]

    def __init__(self, app):
        """
        """

        super().__init__(app)
    #-def

    def init(self):
        """
        """

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

        if docname == 'index':
            return ""
        if docname.endswith(SEP + 'index'):
            return docname[:-5]
        return docname + SEP
    #-def

    def prepare_writing(self, docnames):
        """
        """

        self.template = self.get_template()
        self.docwriter = DoItHtmlWriter(self)
        self.docsettings = OptionParser(
            defaults = self.env.settings,
            components = (self.docwriter,),
            read_config_files = True
        ).get_default_values()
    #-def

    def write_doc(self, docname, doctree):
        """
        """

        html_file_suffix = self.get_builder_config('file_suffix', 'html')

        if html_file_suffix is not None:
            self.out_suffix = html_file_suffix

        docfile = docname + self.out_suffix
        destination = FileOutput(
            destination_path = os.path.join(self.outdir, docfile),
            encoding = 'utf-8'
        )
        doctree.settings = self.docsettings
        self.docwriter.write(doctree, destination)
    #-def

    def finish(self):
        """
        """

        pass
    #-def

    def get_template(self):
        """
        """

        app = self.app
        confdir = app.confdir
        config = app.config
        default_template = load_template('default')
        template = None

        if confdir is None:
            logger.warning(__(
                "'confdir' is not specified, using default template."
            ))
            return default_template

        templates_path = get_config_value(config, 'templates_path') or []
        html_theme_path = self.get_builder_config('theme_path', 'html') or []
        templates_path = html_theme_path + templates_path
        templates_path = [os.path.join(confdir, p) for p in templates_path]

        if not templates_path:
            logger.warning(__(
                "Path to templates is not specified, using default template."
            ))
            return default_template

        html_theme = self.get_builder_config('theme', 'html')

        if not html_theme:
            logger.warning(__("HTML theme is not specified, using default."))
            return default_template

        with Importer(templates_path, False):
            module = __import__(html_theme, None, None, ['load'])
            if hasattr(module, 'load'):
                template = module.load()

        if template is None:
            template = load_template(html_theme)

        if template is None:
            logger.warning(__(
                "Template/Theme '%s' was not found, using default."
            ) % (html_theme,))
            template = default_template

        return template
    #-def
#-class
