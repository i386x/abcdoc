#
# File:    ./tests/unit/utils.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2025-04-25 03:06:11 +0200
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#
"""
Unit tests utilities.

.. include:: defs.inc
"""

import copy
import pathlib

from docutils.core import Publisher
from docutils.io import NullOutput, StringInput, StringOutput
from docutils.writers import UnfilteredWriter
from sphinx.addnodes import toctree as TocTreeNode
from sphinx.builders.latex.transforms import BibliographyTransform
from sphinx.builders.latex.transforms import (
    CitationReferenceTransform as LaTeXCitationReferenceTransform,
)
from sphinx.builders.latex.transforms import (
    DocumentTargetTransform,
    FootnoteDocnameUpdater,
    IndexInSectionTitleTransform,
    LaTeXFootnoteTransform,
    LiteralBlockTransform,
    MathReferenceTransform,
    ShowUrlsTransform,
    SubstitutionDefinitionsRemover,
)
from sphinx.builders.linkcheck import HyperlinkCollector
from sphinx.domains._domains_container import _DomainsContainer
from sphinx.domains.c import AliasTransform as CAliasTransform
from sphinx.domains.c import CDomain
from sphinx.domains.changeset import ChangeSetDomain
from sphinx.domains.citation import (
    CitationDefinitionTransform,
    CitationDomain,
    CitationReferenceTransform,
)
from sphinx.domains.cpp import AliasTransform as CPPAliasTransform
from sphinx.domains.cpp import CPPDomain
from sphinx.domains.index import IndexDomain
from sphinx.domains.javascript import JavaScriptDomain
from sphinx.domains.math import MathDomain
from sphinx.domains.python import PythonDomain
from sphinx.domains.rst import ReSTDomain
from sphinx.domains.std import StandardDomain
from sphinx.environment import _CurrentDocument, default_settings
from sphinx.environment.adapters.toctree import _resolve_toctree
from sphinx.ext.extlinks import ExternalLinksChecker
from sphinx.ext.intersphinx._resolve import IntersphinxRoleResolver
from sphinx.io import SphinxStandaloneReader
from sphinx.parsers import RSTParser
from sphinx.transforms import (
    ApplySourceWorkaround,
    AutoIndexUpgrader,
    AutoNumbering,
    DefaultSubstitutions,
    DoctestTransform,
    ExtraTranslatableNodes,
    FilterSystemMessages,
    GlossarySorter,
    HandleCodeBlocks,
    MoveModuleTargets,
    ReorderConsecutiveTargetAndIndexNodes,
    SortIds,
    SphinxSmartQuotes,
    SphinxTransformer,
    UnreferencedFootnotesDetector,
)
from sphinx.transforms.compact_bullet_list import RefOnlyBulletListTransform
from sphinx.transforms.i18n import (
    AddTranslationClasses,
    Locale,
    PreserveTranslatableMessages,
    RemoveTranslatableInline,
    TranslationProgressTotaliser,
)
from sphinx.transforms.post_transforms import (
    OnlyNodeTransform,
    PropagateDescDomain,
    ReferencesResolver,
    SigElementFallbackTransform,
)
from sphinx.transforms.post_transforms.code import (
    HighlightLanguageTransform,
    TrimDoctestFlagsTransform,
)
from sphinx.transforms.post_transforms.images import (
    DataURIExtractor,
    ImageDownloader,
)
from sphinx.transforms.references import (
    SphinxDanglingReferences,
    SphinxDomains,
)
from sphinx.util.docutils import (
    docutils_namespace,
    patch_docutils,
    sphinx_domains,
)
from sphinx.util.rst import default_role
from sphinx.util.tags import Tags
from sphinx.versioning import UIDTransform
from sphinx.writers.html import HTMLWriter
from vutils.testing.mock import PatcherFactory, make_callable, make_mock

from sphinx_abcdoc_theme.theme import PutToCInsideSection
from sphinx_abcdoc_theme.writer import HtmlTranslator


class ModulePatcher(PatcherFactory):
    """
    Patch modules.

    Temporarily patch :mod:`sphinx_abcdoc_theme.writer`.
    """

    __slots__ = ("logs", "logger")

    def setup(self):
        """Set up the patcher."""
        #: The container for recording logs
        self.logs = []
        #: The logger mock
        self.logger = make_mock(["setLevel", "debug"])
        self.logger.debug = make_callable(
            lambda *args, **kwargs: self.logs.append((args, kwargs))
        )

        self.add_spec(
            "sphinx_abcdoc_theme.writer.getLogger",
            new=make_callable(lambda *args: self.logger),
        )


def make_registry():
    """
    Create a |SphinxComponentRegistry| mock.

    :return: the |SphinxComponentRegistry| mock
    """
    members = [
        "domains",
        "domain_directives",
        "domain_indices",
        "domain_object_types",
        "domain_roles",
        "enumerable_nodes",
        "post_transforms",
        "transforms",
        "create_domains",
        "get_transforms",
        "get_post_transforms",
    ]
    registry = make_mock(members)
    registry.domains = {
        "c": CDomain,
        "changeset": ChangeSetDomain,
        "citation": CitationDomain,
        "cpp": CPPDomain,
        "index": IndexDomain,
        "js": JavaScriptDomain,
        "math": MathDomain,
        "py": PythonDomain,
        "rst": ReSTDomain,
        "std": StandardDomain,
    }
    registry.domain_directives = {}
    registry.domain_indices = {}
    registry.domain_object_types = {}
    registry.domain_roles = {}
    registry.enumerable_nodes = {}
    registry.post_transforms = [
        SubstitutionDefinitionsRemover,
        BibliographyTransform,
        LaTeXCitationReferenceTransform,
        DocumentTargetTransform,
        IndexInSectionTitleTransform,
        LaTeXFootnoteTransform,
        LiteralBlockTransform,
        MathReferenceTransform,
        ShowUrlsTransform,
        HyperlinkCollector,
        CAliasTransform,
        CPPAliasTransform,
        ReferencesResolver,
        OnlyNodeTransform,
        SigElementFallbackTransform,
        PropagateDescDomain,
        HighlightLanguageTransform,
        TrimDoctestFlagsTransform,
        ImageDownloader,
        DataURIExtractor,
        ExternalLinksChecker,
        IntersphinxRoleResolver,
    ]
    registry.transforms = [
        FootnoteDocnameUpdater,
        CitationDefinitionTransform,
        CitationReferenceTransform,
        ApplySourceWorkaround,
        ExtraTranslatableNodes,
        DefaultSubstitutions,
        MoveModuleTargets,
        HandleCodeBlocks,
        SortIds,
        DoctestTransform,
        AutoNumbering,
        AutoIndexUpgrader,
        FilterSystemMessages,
        UnreferencedFootnotesDetector,
        SphinxSmartQuotes,
        GlossarySorter,
        ReorderConsecutiveTargetAndIndexNodes,
        RefOnlyBulletListTransform,
        PreserveTranslatableMessages,
        Locale,
        TranslationProgressTotaliser,
        AddTranslationClasses,
        RemoveTranslatableInline,
        SphinxDanglingReferences,
        SphinxDomains,
        UIDTransform,
        PutToCInsideSection,
    ]

    def create_domains(env):
        """
        Create domains from the registry and the build environment.

        :param env: The |BuildEnvironment| instance or mock
        :return: the iterable object containing domains
        """
        for domain_class in registry.domains.values():
            domain = domain_class(env)
            domain.directives.update(
                registry.domain_directives.get(domain.name, {})
            )
            domain.roles.update(registry.domain_roles.get(domain.name, {}))
            domain.indices.extend(registry.domain_indices.get(domain.name, []))
            for name, objtype in registry.domain_object_types.get(
                domain.name, {}
            ).items():
                domain.add_object_type(name, objtype)
            yield domain

    registry.create_domains = create_domains
    registry.get_transforms = make_callable(lambda: registry.transforms)
    registry.get_post_transforms = make_callable(
        lambda: registry.post_transforms
    )
    return registry


def make_event_manager(app):
    """
    Create an |EventManager| mock.

    :param app: The |Sphinx| application instance or mock
    :return: the |EventManager| mock
    """
    em = make_mock(["app", "emit"])
    em.app = app
    em.emit = make_callable(lambda *args, **kwargs: None)
    return em


def make_config(**config_overrides):
    """
    Create a |Config| mock.

    :param config_overrides: Configuration overrides
    :return: the |Config| mock

    Mocks the configuration for the |sphinx| documentation generator.
    """
    options = [
        "highlight_language",
        "language",
        "locale_dirs",
        "gettext_compact",
        "gettext_additional_targets",
        "translation_progress_classes",
        "default_role",
        "keep_warnings",
        "rst_epilog",
        "rst_prolog",
        "trim_footnote_reference_space",
        "root_doc",
        "source_encoding",
        "source_suffix",
        "smartquotes",
        "smartquotes_action",
        "smartquotes_excludes",
        "html_permalinks",
        "html_permalinks_icon",
        "html_compact_lists",
        "extlinks_detect_hardcoded_links",
        "abcdoc_debug",
        "abcdoctest_transforms",
        "abcdoctest_translator_class",
    ]
    config = make_mock(options)
    config.highlight_language = config_overrides.get(
        "highlight_language", "default"
    )
    config.language = config_overrides.get("language", "en")
    config.locale_dirs = config_overrides.get("locale_dirs", ["locales"])
    config.gettext_compact = config_overrides.get("gettext_compact", True)
    config.gettext_additional_targets = config_overrides.get(
        "gettext_additional_targets", []
    )
    config.translation_progress_classes = config_overrides.get(
        "translation_progress_classes", False
    )
    config.default_role = config_overrides.get("default_role", None)
    config.keep_warnings = config_overrides.get("keep_warnings", False)
    config.rst_epilog = config_overrides.get("rst_epilog", "")
    config.rst_prolog = config_overrides.get("rst_prolog", "")
    config.trim_footnote_reference_space = config_overrides.get(
        "trim_footnote_reference_space", False
    )
    config.root_doc = config_overrides.get("root_doc", "index")
    config.source_encoding = config_overrides.get(
        "source_encoding", "utf-8-sig"
    )
    config.source_suffix = config_overrides.get(
        "source_suffix", {".rst": "restructuredtext"}
    )
    config.smartquotes = config_overrides.get("smartquotes", True)
    config.smartquotes_action = config_overrides.get(
        "smartquotes_action", "qDe"
    )
    config.smartquotes_excludes = config_overrides.get(
        "smartquotes_excludes",
        {
            "languages": ["ja"],
            "builders": ["man", "text"],
        },
    )
    config.html_permalinks = config_overrides.get("html_permalinks", True)
    config.html_permalinks_icon = config_overrides.get(
        "html_permalinks_icon", "&#x00B6;"
    )
    config.html_compact_lists = config_overrides.get(
        "html_compact_lists", True
    )
    config.extlinks_detect_hardcoded_links = config_overrides.get(
        "extlinks_detect_hardcoded_links", False
    )
    config.abcdoc_debug = config_overrides.get("abcdoc_debug", False)
    config.abcdoctest_transforms = config_overrides.get(
        "abcdoctest_transforms", []
    )
    config.abcdoctest_translator_class = config_overrides.get(
        "abcdoctest_translator_class", HtmlTranslator
    )
    return config


def make_environment(app):
    """
    Create a |BuildEnvironment| mock.

    :param app: The |Sphinx| application instance or mock
    :return: the |BuildEnvironment| mock
    """
    members = [
        "app",
        "srcdir",
        "config",
        "events",
        "versioning_condition",
        "settings",
        "current_document",
        "domaindata",
        "domains",
        "_registry",
        "docname",
    ]
    env = make_mock(members)
    env.app = app
    env.srcdir = app.srcdir
    env.config = app.config
    env.events = app.events
    env.versioning_condition = False
    env.settings = default_settings.copy()
    env.settings["env"] = env
    env.settings["input_encoding"] = app.config.source_encoding
    env.settings["output_encoding"] = "unicode"
    env.settings["trim_footnote_reference_space"] = (
        app.config.trim_footnote_reference_space
    )
    env.settings["language_code"] = app.config.language
    env.settings["smart_quotes"] = True
    env.settings["traceback"] = True
    env.current_document = _CurrentDocument()
    env.domaindata = {}
    env._registry = app.registry
    env.docname = "<string>"
    env.domains = _DomainsContainer._from_environment(
        env, registry=app.registry
    )
    env.domains._setup()
    return env


def make_builder(app, env):
    """
    Create a |Builder| mock.

    :param app: The |Sphinx| application instance or mock
    :param env: The |BuildEnvironment| instance or mock
    :return: the |Builder| mock
    """
    members = [
        "name",
        "format",
        "srcdir",
        "app",
        "env",
        "events",
        "config",
        "tags",
        "create_translator",
    ]
    builder = make_mock(members)
    builder.name = "html"
    builder.format = "html"
    builder.srcdir = app.srcdir
    builder.app = app
    builder.env = env
    builder.events = app.events
    builder.config = app.config
    builder.tags = app.tags
    builder.tags.add(builder.format)
    builder.tags.add(builder.name)
    builder.tags.add(f"format_{builder.format}")
    builder.tags.add(f"builder_{builder.name}")
    builder.create_translator = make_callable(
        app.config.abcdoctest_translator_class
    )
    return builder


def make_application(**config_overrides):
    """
    Create a |Sphinx| application mock.

    :param config_overrides: Configuration overrides
    :return: the |Sphinx| application mock
    """
    members = [
        "registry",
        "srcdir",
        "events",
        "tags",
        "config",
        "env",
        "builder",
    ]
    app = make_mock(members)
    app.registry = make_registry()
    app.srcdir = pathlib.Path("./.remove_me")
    app.events = make_event_manager(app)
    app.tags = Tags()
    app.config = make_config(**config_overrides)
    app.registry.transforms.extend(app.config.abcdoctest_transforms)
    app.env = make_environment(app)
    app.builder = make_builder(app, app.env)
    return app


class KeepDoctreeWriter(UnfilteredWriter):
    """Writer that keeps a generated document tree intact."""

    #: Formats supported by this component (necessary to keep ``meta`` nodes)
    supported = ("html",)

    __slots__ = ()

    def translate(self):
        """Do not touch the document tree."""


def make_publisher(app):
    """
    Create a publisher that converts a string to the doctree.

    :param app: The |Sphinx| application instance or mock
    :return: the publisher

    The publisher converts a string in the reStructuredText syntax to the
    document tree ready for further processing.
    """
    reader = SphinxStandaloneReader()
    reader.setup(app)
    parser = RSTParser()
    parser.set_application(app)

    pub = Publisher(
        reader=reader,
        parser=parser,
        writer=KeepDoctreeWriter(),
        source_class=StringInput,
        destination=NullOutput(),
    )
    defaults = {"traceback": True, **app.env.settings}
    pub.get_settings(**defaults)
    return pub


def rst2doctree(source, app):
    """
    Convert a string in reStructuredText to the document tree.

    :param source: The document source in reStructuredText format
    :param app: The |Sphinx| application instance or mock
    :return: the document tree
    """
    builder = app.builder
    pub = make_publisher(app)
    builder.env.current_document._parser = pub.parser
    with (
        sphinx_domains(builder.env),
        default_role("<string>", builder.config.default_role),
    ):
        pub.set_source(source)
        pub.publish()
    builder.env.current_document = _CurrentDocument()
    return pub.document


def doctree2html(doctree, app=None, **config_overrides):
    """
    Convert a document tree to HTML.

    :param doctree: The document tree
    :param app: The |Spinx| application instance or mock
    :param config_overrides: Configuration overrides
    :return: the HTML output

    If :xarg:`app` is :obj:`None`, create a |Sphinx| application mock with
    :xarg:`config_overrides`. Otherwise, use provided :xarg:`app`, in which
    case :xarg:`config_overrides` are left unused.

    The conversion is done via the custom |HtmlTranslator| class.
    """
    if app is None:
        app = make_application(**config_overrides)
    destination = StringOutput(encoding="utf-8")
    docwriter = HTMLWriter(app.builder)
    docwriter.write(doctree, destination)
    docwriter.assemble_parts()
    return docwriter.parts["fragment"]


def rst2html(source, **config_overrides):
    """
    Translate a document from reStructuredText to HTML.

    :param source: The source document
    :param config_overrides: Configuration overrides
    :return: the HTML output

    Mimics what |sphinx| does, with all transforms and domains, but without
    templating. Uses the custom |HtmlTranslator| class.
    """
    with patch_docutils("./docs"), docutils_namespace():
        app = make_application(**config_overrides)
        doctree = rst2doctree(source, app)

        backup = app.env.current_document
        new = copy.deepcopy(backup)
        new.docname = "<string>"
        try:
            app.env.current_document = new
            transformer = SphinxTransformer(doctree)
            transformer.set_environment(app.env)
            transformer.add_transforms(app.registry.get_post_transforms())
            transformer.apply_transforms()
        finally:
            app.env.current_document = backup

        for toctreenode in doctree.findall(TocTreeNode):
            result = _resolve_toctree(
                app.env,
                "<string>",
                app.builder,
                toctreenode,
                prune=True,
                includehidden=False,
                tags=app.builder.tags,
            )
            if result is None:
                toctreenode.parent.replace(toctreenode, [])
            else:
                toctreenode.replace_self(result)

        return doctree2html(doctree, app=app)
