#
#! \file    ~/docs/Makefile
#! \author  Jiří Kučera, <sanczes AT gmail.com>
#! \stamp   2018-09-05 10:01:37 +0200
#! \project DoIt! Doc: Sphinx Extension for DoIt! Documentation
#! \license MIT
#! \version 0.0.0
#! \brief   Build documentation.
#

ME := $(lastword $(MAKEFILE_LIST))
HERE := $(dir $(abspath $(ME)))
SPHINXNAME := Sphinx

include $(HERE)/../utils/mkutils.mk

$(call AddTool, rm)

# Can be overriden by the user from command line
$(call AddVar, PYTHONS=LIST_OF_BINARIES, python3 python, \
    specify the list of Python interpreter candidates \
)
$(call AddVar, NEEDPYTHON=VERSION, 36, \
    specify the minimal required version of Python interpreter; /n \
    VERSION is a number created by concatenating major and minor /n \
    version numbers$(,) ommiting dots \
)
$(call SetVar, PYTHON=BINARY, \
    $(call NeedPython, PYTHONS, NEEDPYTHON), \
    specify the Python interpreter \
)
$(call AddVar, SPHINX_BUILD=COMMAND, $$(PYTHON) -m sphinx, \
    specify the command that runs $(SPHINXNAME) \
)
$(call DefVar, SPHINXOPTS=LIST_OF_OPTIONS,, \
    specify the additional options to $(SPHINXNAME) \
)
$(call AddVar, SOURCEDIR=PATH, $$(HERE), \
    specify the directory with source files \
)
$(call AddVar, BUILDDIR=PATH, build, \
    specify the output directory for built files \
)

$(call DefaultTarget, help)

# For internal use only
SPHINXFLAGS := -d $(BUILDDIR)/doctrees $(SPHINXOPTS) $(SOURCEDIR)

# Template for building targets
Builder = $(call $(0)_,$(strip $1),$(strip $2))
Builder_ = $(eval $(call $(0)a,$1,$(call $(0)b,$1),$2))
define Builder_a =
$$(call Target, $1, $3)
	$$(SPHINX_BUILD) -b $2 $$(SPHINXFLAGS) $$(BUILDDIR)/$1
endef
Builder_b = $(subst html,doit-html,$(subst syncheck,dummy,$1))

# Building targets
$(call Builder, html, generate HTML files)
$(call Builder, changes, \
    make an overview of all changed/added/deprecated /n \
    items \
)
$(call Builder, linkcheck, check all external links for integrity)
$(call Builder, doctest, run all doctests embedded in the documentation)
$(call Builder, coverage, run coverage check of the documentation)
$(call Builder, spelling, run a spell check of the documentation)
$(call Builder, syncheck, check syntax errors of document sources)

# Cleaning things up
$(call Target, clean, remove build products)
	$(RM) -rf $(BUILDDIR)/*

$(call GenerateHelp)
