#                                                         -*- coding: utf-8 -*-
#! \file    ~/setup.py
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2018-08-26 20:27:49 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version See doit_doc_template.__version__
#! \brief   See __doc__
#
"""\
Package setup.\
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

from setuptools import setup

import doit_doc_template

def long_description():
    with open('README.md') as f:
        return f.read()

setup(
    name = doit_doc_template.__pkgname__,
    version = doit_doc_template.__version__,
    description = doit_doc_template.__doc__,
    long_description = long_description(),
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Plugins',
        'Framework :: Sphinx',
        'Framework :: Sphinx :: Extension',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Documentation',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML'
    ],
    keywords = 'sphinx extension builder',
    url = doit_doc_template.__url__,
    #download_url = None,
    author = doit_doc_template.__author__,
    author_email = doit_doc_template.__author_email__,
    license = 'MIT',
    packages = [doit_doc_template.__pkgname__],
    platforms = 'any',
    python_requires = '>= 3.4',
    install_requires = [
        'sphinx >= 0.6'
    ],
    #test_suite = None,
    #tests_require = ['unittest2'],
    extras_require = {
        'test': [
            'coverage >= 4.5.1',
            'flake8 >= 3.5.0',
            'pydocstyle >= 2.1.1'
        ]
    },
    #entry_points = {
    #    'console_scripts': ['script=path.to.module:entry_point_func']
    #}
    include_package_data = True,
    zip_safe = False
)
