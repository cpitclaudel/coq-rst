"""A Coq domain for Sphinx.

Currently geared towards Coq's manual, rather than Coq source files, but one
could imagine extending it.
"""

# pylint: disable=too-few-public-methods

import re
from itertools import chain
from collections import defaultdict

from docutils import nodes, utils
from docutils.transforms import Transform
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.roles import code_role #, set_classes
from docutils.parsers.rst.directives.admonitions import BaseAdmonition

from sphinx import addnodes
from sphinx.roles import XRefRole
from sphinx.util.nodes import set_source_info, set_role_source_info, make_refnode
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType, Index
from sphinx.ext.mathbase import MathDirective, displaymath

from . import coqdoc
from .repl import ansicolors
from .repl.coqtop import CoqTop
from .notations.sphinx import sphinxify
from .notations.plain import stringify_with_ellipses

def parse_notation(notation, source, line, rawtext=None):
    """Parse notation and wrap it in an inline node"""
    node = nodes.inline(rawtext or notation, '', *sphinxify(notation), classes=['notation'])
    node.source, node.line = source, line
    return node

def highlight_using_coqdoc(sentence):
    """Lex sentence using coqdoc, and yield inline nodes for each token"""
    tokens = coqdoc.lex(utils.unescape(sentence, 1))
    for classes, value in tokens:
        yield nodes.inline(value, value, classes=classes)

def make_target(objtype, targetid):
    """Create a target to an object of type objtype and id targetid"""
    return "coq:{}.{}".format(objtype, targetid)

class CoqObject(ObjectDescription):
    """A generic Coq object; all Coq objects are subclasses of this.

    The fields and methods to override are listed at the top of this class'
    implementation.  Each object supports the :name: option, which gives an
    explicit name to link to.

    See the documentation of CoqDomain for high-level information.
    """

    # The semantic domain in which this object lives.
    # It matches exactly one of the roles used for cross-referencing.
    subdomain = None

    # The suffix to use in indices for objects of this type
    index_suffix = None

    # The annotation to add to headers of objects of this type
    annotation = None

    def _name_from_signature(self, signature): # pylint: disable=no-self-use, unused-argument
        """Convert a signature into a name to link to.

        Returns None by default, in which case no name will be automatically
        generated.
        """
        return None

    def _render_signature(self, signature, signode):
        """Render a signature, placing resulting nodes into signode."""
        raise NotImplementedError(self)

    option_spec = {
        # One can give an explicit name to each documented object
        'name': directives.unchanged
    }

    def _subdomain(self):
        if self.subdomain is None:
            raise ValueError()
        return self.subdomain

    def handle_signature(self, signature, signode):
        """Prefix signature with the proper annotation, then render it using
        _render_signature.

        :returns: the name given to the resulting node, if any
        """
        if self.annotation:
            annotation = self.annotation + ' '
            signode += addnodes.desc_annotation(annotation, annotation)
        self._render_signature(signature, signode)
        return self._name_from_signature(signature)

    @property
    def _index_suffix(self):
        if self.index_suffix:
            return " " + self.index_suffix

    def _record_name(self, name, target_id):
        """Record a name, mapping it to target_id

        Warns if another object of the same name already exists.
        """
        names_in_subdomain = self.env.domaindata['coq']['objects'][self._subdomain()]
        # Check that two objects in the same domain don't have the same name
        if name in names_in_subdomain:
            self.state_machine.reporter.warning(
                'Duplicate Coq object: {}; other is at {}'.format(
                    name, self.env.doc2path(names_in_subdomain[name][0])),
                line=self.lineno)
        names_in_subdomain[name] = (self.env.docname, self.objtype, target_id)

    def _add_target(self, signode, name):
        """Register a link target ‘name’, pointing to signode."""
        targetid = make_target(self.objtype, nodes.make_id(name))
        if targetid not in self.state.document.ids:
            signode['ids'].append(targetid)
            signode['names'].append(name)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            self._record_name(name, targetid)
        return targetid

    def _add_index_entry(self, name, target):
        """Add name (with target) to the main index."""
        index_text = name + self._index_suffix
        self.indexnode['entries'].append(('single', index_text, target, '', None))

    def run(self):
        """Small extension of the parent's run method, handling user-provided names."""
        [idx, node] = super().run()
        custom_name = self.options.get("name")
        if custom_name:
            self.add_target_and_index(custom_name, "", node.children[0])
        return [idx, node]

    def add_target_and_index(self, name, _, signode):
        """Create a target and an index entry for name"""
        if name:
            target = self._add_target(signode, name)
            self._add_index_entry(name, target)
            return target

class PlainObject(CoqObject):
    """A base class for objects whose signatures should be rendered literaly."""
    def _render_signature(self, signature, signode):
        signode += addnodes.desc_name(signature, signature)

class NotationObject(CoqObject):
    """A base class for objects whose signatures should be rendered as nested boxes."""
    def _render_signature(self, signature, signode):
        position = self.state_machine.get_source_and_line(self.lineno)
        tacn_node = parse_notation(signature, *position)
        signode += addnodes.desc_name(signature, '', tacn_node)

class TacticObject(PlainObject):
    """An object to represent Coq tactics"""
    subdomain = "tac"
    index_suffix = "(tactic)"
    annotation = None

class GallinaObject(PlainObject):
    """An object to represent Coq theorems"""
    subdomain = "thm"
    index_suffix = "(theorem)"
    annotation = "Theorem"

class VernacObject(NotationObject):
    """An object to represent Coq commands"""
    subdomain = "cmd"
    index_suffix = "(command)"
    annotation = "Command"

    def _name_from_signature(self, signature):
        return stringify_with_ellipses(signature)

class VernacVariantObject(VernacObject):
    """An object to represent variants of Coq commands"""
    index_suffix = "(command variant)"
    annotation = "Variant"

class TacticNotationObject(NotationObject):
    """An object to represent Coq tactic notations"""
    subdomain = "tacn"
    index_suffix = "(tactic notation)"
    annotation = None

class TacticNotationVariantObject(TacticNotationObject):
    """An object to represent variants of Coq tactic notations"""
    index_suffix = "(tactic variant)"
    annotation = "Variant"

class OptionObject(NotationObject):
    """An object to represent variants of Coq options"""
    subdomain = "opt"
    index_suffix = "(option)"
    annotation = "Option"

    def _name_from_signature(self, signature):
        return stringify_with_ellipses(signature)

class ExceptionObject(NotationObject):
    """An object to represent Coq errors."""
    subdomain = "exn"
    index_suffix = "(error)"
    annotation = "Error"
    # Uses “exn” since “err” already is a CSS class added by “writer_aux”.

    # Generate names automatically
    def _name_from_signature(self, signature):
        return stringify_with_ellipses(signature)

def NotationRole(role, rawtext, text, lineno, inliner, options={}, content=[]):
    #pylint: disable=unused-argument, dangerous-default-value
    """And inline role for notations"""
    notation = utils.unescape(text, 1)
    position = inliner.reporter.get_source_and_line(lineno)
    return [nodes.literal(rawtext, '', parse_notation(notation, *position, rawtext=rawtext))], []

def coq_code_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    #pylint: disable=dangerous-default-value
    """And inline role for Coq source code"""
    options['language'] = 'Coq'
    return code_role(role, rawtext, text, lineno, inliner, options, content)
    ## Too heavy:
    ## Forked from code_role to use our custom tokenizer; this doesn't work for
    ## snippets though: for example CoqDoc swallows the parentheses around this:
    ## “(a: A) (b: B)”
    # set_classes(options)
    # classes = ['code', 'coq']
    # code = utils.unescape(text, 1)
    # node = nodes.literal(rawtext, '', *highlight_using_coqdoc(code), classes=classes)
    # return [node], []

# TODO pass different languages?
LtacRole = GallinaRole = VernacRole = coq_code_role

class CoqtopDirective(Directive):
    """A reST directive to describe interactions with Coqtop.

    Usage::

       .. coqtop:: (options)+

          Coq code to send to coqtop

    Example::

       .. coqtop:: in reset undo

          Print nat.
          Definition a := 1.

    Here is a list of permissible options:

    Display
      - ‘all’: Display input and output
      - ‘in’: Display only input
      - ‘out’: Display only output
      - ‘none’: Display neither (useful for setup commands)
    Behaviour
      - ‘reset’: Send a `Reset Initial` command before running this block
      - ‘undo’: Send an `Undo n` (n=number of sentences) command after running
        all the commands in this block
    """
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True

    def run(self):
        # Uses a ‘container’ instead of a ‘literal_block’ to disable
        # Pygments-based post-processing (we could also set rawsource to '')
        content = '\n'.join(self.content)
        options = self.arguments[0].split() if self.arguments else ['in']
        if 'all' in options:
            options.extend(['in', 'out'])
        node = nodes.container(content, coqtop_options = list(set(options)),
                               classes=['coqtop', 'literal-block'])
        self.add_name(node)
        return [node]

class CoqdocDirective(Directive):
    """A reST directive to display Coqtop-formatted source code"""
    # TODO implement this as a Pygments highlighter?
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        # Uses a ‘container’ instead of a ‘literal_block’ to disable
        # Pygments-based post-processing (we could also set rawsource to '')
        content = '\n'.join(self.content)
        node = nodes.inline(content, '', *highlight_using_coqdoc(content))
        wrapper = nodes.container(content, node, classes=['coqdoc', 'literal-block'])
        return [wrapper]

class ExampleDirective(BaseAdmonition):
    """A reST directive for examples"""
    node_class = nodes.admonition

    def run(self):
        # ‘BaseAdmonition’ checks whether ‘node_class’ is ‘nodes.admonition’,
        # and uses arguments[0] as the title in that case (in other cases, the
        # title is unset, and it is instead set in the HTML visitor).
        assert not self.arguments # Arguments have been parsed as content
        self.arguments = ['Example']
        self.options['classes'] = ['admonition', 'note']
        return super().run()

class PreambleDirective(MathDirective):
    r"""A reST directive for hidden math.

    Mostly useful to let MathJax know about `\def`s and `\newcommand`s
    """
    def run(self):
        self.options['nowrap'] = True
        [node] = super().run()
        node['classes'] = ["math-preamble"]
        return [node]

class InferenceDirective(Directive):
    r"""A small example of what directives let you do in Sphinx.

    Usage::

       .. inference:: name

          \n-separated premisses
          ----------------------
          conclusion

    Example::

       .. inference:: Prod-Pro

          \WTEG{T}{s}
          s \in \Sort
          \WTE{\Gamma::(x:T)}{U}{\Prop}
          -----------------------------
          \WTEG{\forall~x:T,U}{\Prop}
    """
    required_arguments = 1
    optional_arguments = 0
    has_content = True

    def make_math_node(self, latex):
        node = displaymath()
        node['latex'] = latex
        node['label'] = None # Otherwise equations are numbered
        node['nowrap'] = False
        node['docname'] = self.state.document.settings.env.docname
        return node

    @staticmethod
    def prepare_latex_operand(op):
        # TODO: Could use a fancier inference class in LaTeX
        return '%\n\\hspace{3em}%\n'.join(op.strip().splitlines())

    def prepare_latex(self, content):
        parts = re.split('^ *----+ *$', content, flags=re.MULTILINE)
        if len(parts) != 2:
            raise self.error('Expected two parts in inference::, separated by a rule (----).')

        top, bottom = tuple(InferenceDirective.prepare_latex_operand(p) for p in parts)
        return "%\n".join(("\\frac{", top, "}{", bottom, "}"))

    def run(self):
        self.assert_has_content()

        title = self.arguments[0]
        content = '\n'.join(self.content)
        math_node = self.make_math_node(self.prepare_latex(content))

        tid = nodes.make_id(title)
        target = nodes.target('', '', ids=['inference-' + tid])
        self.state.document.note_explicit_target(target)

        dli = nodes.definition_list_item()
        dli += target
        dli += nodes.term('', title)
        dli += nodes.description('', math_node)
        dl = nodes.definition_list(content, dli)
        set_source_info(self, dl)
        return [dl]

class AnsiColorsParser():
    """Parse ANSI-colored output from Coqtop into Sphinx nodes."""

    # Coqtop's output crashes ansi.py, because it contains a bunch of extended codes
    # This class is a fork of the original ansi.py, released under a BSD license in sphinx-contribs

    COLOR_PATTERN = re.compile('\x1b\\[([^m]+)m')

    def __init__(self):
        self.new_nodes, self.pending_nodes = [], []

    def _finalize_pending_nodes(self):
        self.new_nodes.extend(self.pending_nodes)
        self.pending_nodes = []

    def _add_text(self, raw, beg, end):
        if beg < end:
            text = raw[beg:end]
            if self.pending_nodes:
                self.pending_nodes[-1].append(nodes.Text(text))
            else:
                self.new_nodes.append(nodes.inline('', text))

    def colorize_str(self, raw):
        """Parse raw (an ANSI-colored output string from Coqtop) into Sphinx nodes."""
        last_end = 0
        for match in AnsiColorsParser.COLOR_PATTERN.finditer(raw):
            self._add_text(raw, last_end, match.start())
            last_end = match.end()
            classes = ansicolors.parse_ansi(match.group(1))
            if 'ansi-reset' in classes:
                self._finalize_pending_nodes()
            else:
                node = nodes.inline()
                self.pending_nodes.append(node)
                node['classes'].extend(classes)
        self._add_text(raw, last_end, len(raw))
        self._finalize_pending_nodes()
        return self.new_nodes

class CoqtopBlocksTransform(Transform):
    """Filter handling the actual work for the coqtop directive

    Adds coqtop's responses, colorizes input and output, and merges consecutive
    coqtop directives for better visual rendition.
    """
    default_priority = 10

    @staticmethod
    def is_coqtop_block(node):
        return isinstance(node, nodes.Element) and 'coqtop_options' in node

    @staticmethod
    def split_sentences(source):
        """Split Coq sentences in source. Could be improved."""
        return re.split(r"(?<=(?<!\.)\.)\s+", source)

    @staticmethod
    def parse_options(options):
        """Parse options according to the description in CoqtopDirective."""
        opt_undo = 'undo' in options
        opt_reset = 'reset' in options
        opt_all, opt_none = 'all' in options, 'none' in options
        opt_input, opt_output = opt_all or 'in' in options, opt_all or 'out' in options

        unexpected_options = list(set(options) - set(('reset', 'undo', 'all', 'none', 'in', 'out')))
        if unexpected_options:
            raise ValueError("Unexpected options for .. coqtop:: {}".format(unexpected_options))
        elif (opt_input or opt_output) and opt_none:
            raise ValueError("Inconsistent options for .. coqtop:: ‘none’ with ‘in’, ‘out’, or ‘all’")
        elif opt_reset and opt_undo:
            raise ValueError("Inconsistent options for .. coqtop:: ‘undo’ with ‘reset’")

        return opt_undo, opt_reset, opt_input and not opt_none, opt_output and not opt_none

    @staticmethod
    def block_classes(should_show, contents=None):
        """Compute classes to add to a node containing contents.

        :param should_show: Whether this node should be displayed"""
        is_empty = contents is not None and re.match(r"^\s*$", contents)
        if is_empty or not should_show:
            return ['coqtop-hidden']
        else:
            return []

    @staticmethod
    def make_rawsource(pairs, opt_input, opt_output):
        blocks = []
        for sentence, output in pairs:
            output = AnsiColorsParser.COLOR_PATTERN.sub("", output).strip()
            blocks.extend([sentence] * opt_input)
            blocks.extend([output + "\n"] * (opt_output and output != ""))
        return '\n'.join(blocks)

    def add_coqtop_output(self):
        """Add coqtop's responses to a Sphinx AST

        Finds nodes to process using is_coqtop_block."""
        # FIXME use a more generic setting for COQTOP_BIN
        with CoqTop(coqtop_bin="/build/coq-8.5/bin/coqtop", color=True) as repl:
            for node in self.document.traverse(CoqtopBlocksTransform.is_coqtop_block):
                options = node['coqtop_options']
                opt_undo, opt_reset, opt_input, opt_output = self.parse_options(options)

                if opt_reset:
                    repl.sendone("Reset Initial.")
                pairs = []
                for sentence in self.split_sentences(node.rawsource):
                    pairs.append((sentence, repl.sendone(sentence)))
                if opt_undo:
                    repl.sendone("Undo {}.".format(len(pairs)))

                dli = nodes.definition_list_item()
                for sentence, output in pairs:
                    # Use Coqdoq to highlight input
                    in_chunks = highlight_using_coqdoc(sentence)
                    dli += nodes.term(sentence, '', *in_chunks, classes=self.block_classes(opt_input))
                    # Parse ANSI sequences to highlight output
                    out_chunks = AnsiColorsParser().colorize_str(output)
                    dli += nodes.definition(output, *out_chunks, classes=self.block_classes(opt_output, output))
                node.clear()
                node.rawsource = self.make_rawsource(pairs, opt_input, opt_output)
                node['classes'].extend(self.block_classes(opt_input or opt_output))
                node += nodes.inline('', '', classes=['coqtop-reset'] * opt_reset)
                node += nodes.definition_list(node.rawsource, dli)

    def merge_consecutive_coqtop_blocks(self):
        """Merge consecutive divs wrapping lists of Coq sentences; keep ‘dl’s separate."""
        for node in self.document.traverse(CoqtopBlocksTransform.is_coqtop_block):
            if node.parent:
                for sibling in node.traverse(include_self=False, descend=False,
                                             siblings=True, ascend=False):
                    if CoqtopBlocksTransform.is_coqtop_block(sibling):
                        node.extend(sibling.children)
                        node.parent.remove(sibling)
                        sibling.parent = None
                    else:
                        break

    def apply(self):
        self.add_coqtop_output()
        self.merge_consecutive_coqtop_blocks()

class CoqSubdomainsIndex(Index):
    """Index subclass to provide subdomain-specific indices.

    Just as in the original manual, we want to have separate indices for each
    Coq subdomain (tactics, commands, options, etc)"""

    name, localname, shortname, subdomains = None, None, None, None # Must be overwritten

    def generate(self, docnames=None):
        content = defaultdict(list)
        items = chain(*(self.domain.data['objects'][subdomain].items()
                        for subdomain in self.subdomains))

        for itemname, (docname, _, anchor) in sorted(items, key=lambda x: x[0].lower()):
            if docnames and docname not in docnames:
                continue

            entries = content[itemname[0].lower()]
            entries.append([itemname, 0, docname, anchor, '', '', ''])

        collapse = False
        content = sorted(content.items())
        return content, collapse

class CoqVernacIndex(CoqSubdomainsIndex):
    name, localname, shortname, subdomains = "cmdindex", "Command Index", "commands", ["cmd"]

class CoqTacticIndex(CoqSubdomainsIndex):
    name, localname, shortname, subdomains = "tacindex", "Tactic Index", "tactics", ["tac", "tacn"]

class CoqOptionIndex(CoqSubdomainsIndex):
    name, localname, shortname, subdomains = "optindex", "Option Index", "options", ["opt"]

class CoqGallinaIndex(CoqSubdomainsIndex):
    name, localname, shortname, subdomains = "thmindex", "Gallina Index", "theorems", ["thm"]

class CoqExceptionIndex(CoqSubdomainsIndex):
    name, localname, shortname, subdomains = "exnindex", "Error Index", "errors", ["exn"]

class IndexXRefRole(XRefRole):
    """A link to one of our domain-specific indices."""
    lowercase = True,
    innernodeclass = nodes.inline
    warn_dangling = True

    def process_link(self, env, refnode, has_explicit_title, title, target):
        if not has_explicit_title:
            index = CoqDomain.find_index_by_name(target)
            if index:
                title = index.localname
        return title, target

def GrammarProductionRole(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    """An inline role to declare grammar productions that are not in fact included
    in a `productionlist` directive.

    Useful to informally introduce a production, as part of running text
    """
    #pylint: disable=dangerous-default-value, unused-argument
    env = inliner.document.settings.env
    idname = 'grammar-token-{}'.format(text)
    node = nodes.literal(rawtext, text, role=typ.lower(), classes=['inline-grammar-production'], ids=[idname])
    set_role_source_info(inliner, lineno, node)
    inliner.document.note_implicit_target(node, node)
    env.domaindata['std']['objects']['token', text] = env.docname, idname
    return [node], []

class CoqDomain(Domain):
    """A domain to document Coq code.

    Sphinx has a notion of “domains”, used to tailor it to a specific language.
    Domains mostly consist in descriptions of the objects that we wish to
    describe (for Coq, this includes tactics, tactic notations, options,
    exceptions, etc.), as well as domain-specific roles and directives.

    Each domain is responsible for tracking its objects, and resolving
    references to them. In the case of Coq, this leads us to define Coq
    “subdomains”, which classify objects into categories in which names must be
    unique. For example, a tactic and a theorem may share a name, but two
    tactics cannot be named the same.
    """

    name = 'coq'
    label = 'Coq'

    object_types = {
        # ObjType (= directive type) → (Local name, *xref-roles)
        'cmd': ObjType('cmd', 'cmd'),
        'cmdv': ObjType('cmdv', 'cmd'),
        'tac': ObjType('tac', 'tac'),
        'tacn': ObjType('tacn', 'tacn'),
        'tacv': ObjType('tacv', 'tacn'),
        'opt': ObjType('opt', 'opt'),
        'thm': ObjType('thm', 'thm'),
        'exn': ObjType('exn', 'exn'),
        'index': ObjType('index', 'index', searchprio=-1)
    }

    directives = {
        # Note that some directives live in the same semantic subdomain; ie
        # there's one directive per object type, but some object types map to
        # the same role.
        'cmd': VernacObject,
        'cmdv': VernacVariantObject,
        'tac': TacticObject,
        'tacn': TacticNotationObject,
        'tacv': TacticNotationVariantObject,
        'opt': OptionObject,
        'thm': GallinaObject,
        'exn': ExceptionObject,
    }

    roles = {
        # Each of these roles lives in a different semantic “subdomain”
        'cmd': XRefRole(),
        'tac': XRefRole(),
        'tacn': XRefRole(),
        'opt': XRefRole(),
        'thm': XRefRole(),
        'exn': XRefRole(),
        # This one is special
        'index': IndexXRefRole(),
        # These are used for highlighting
        'notation': NotationRole,
        'gallina': GallinaRole,
        'ltac': LtacRole,
        'n': NotationRole,
        'g': GallinaRole,
        'l': LtacRole, #FIXME unused?
    }

    indices = [CoqVernacIndex, CoqTacticIndex, CoqOptionIndex, CoqGallinaIndex, CoqExceptionIndex]

    data_version = 1
    initial_data = {
        # Collect everything under a key that we control, since Sphinx adds
        # others, such as “version”
        'objects' : { # subdomain → name → docname, objtype, targetid
            'cmd': {},
            'tac': {},
            'tacn': {},
            'opt': {},
            'thm': {},
            'exn': {},
        }
    }

    @staticmethod
    def find_index_by_name(targetid):
        for index in CoqDomain.indices:
            if index.name == targetid:
                return index

    def get_objects(self):
        # Used for searching and object inventories (intersphinx)
        for _, objects in self.data['objects'].items():
            for name, (docname, objtype, targetid) in objects.items():
                yield (name, name, objtype, docname, targetid, self.object_types[objtype].attrs['searchprio'])
        for index in self.indices:
            yield (index.name, index.localname, 'index', "coq-" + index.name, '', -1)

    def merge_domaindata(self, docnames, otherdata):
        DUP = "Duplicate declaration: '{}' also defined in '{}'.\n"
        for subdomain, their_objects in otherdata['objects'].items():
            our_objects = self.data['objects'][subdomain]
            for name, (docname, objtype, targetid) in their_objects.items():
                if docname in docnames:
                    if name in our_objects:
                        self.env.warn(docname, DUP.format(name, our_objects[name][0]))
                    our_objects[name] = (docname, objtype, targetid)

    def resolve_xref(self, env, fromdocname, builder, role, targetname, node, contnode):
        # ‘target’ is the name that was written in the document
        # ‘role’ is where this xref comes from; it's exactly one of our subdomains
        if role == 'index':
            index = CoqDomain.find_index_by_name(targetname)
            if index:
                return make_refnode(builder, fromdocname, "coq-" + index.name, '', contnode, index.localname)
        else:
            resolved = self.data['objects'][role].get(targetname)
            if resolved:
                (todocname, _, targetid) = resolved
                return make_refnode(builder, fromdocname, todocname, targetid, contnode, targetname)

    def clear_doc(self, docname_to_clear):
        for subdomain_objects in self.data['objects'].values():
            for name, (docname, _, _) in list(subdomain_objects.items()):
                if docname == docname_to_clear:
                    del subdomain_objects[name]

def is_coqtop_or_coqdoc_block(node):
    return (isinstance(node, nodes.Element) and
       ('coqtop' in node['classes'] or 'coqdoc' in node['classes']))

def simplify_source_code_blocks_for_latex(app, doctree, fromdocname): # pylint: disable=unused-argument
    """Simplify coqdoc and coqtop blocks.

    In HTML mode, this does nothing; in other formats, such as LaTeX, it
    replaces coqdoc and coqtop blocks by plain text sources, which will use
    pygments if available.  This prevents the LaTeX builder from getting
    confused.
    """

    is_html = app.builder.tags.has("html")
    for node in doctree.traverse(is_coqtop_or_coqdoc_block):
        if is_html:
            node.rawsource = '' # Prevent pygments from kicking in
        else:
            node.replace_self(nodes.literal_block(node.rawsource, node.rawsource, language="Coq"))

def setup(app):
    """Register the Coq domain"""

    # A few sanity checks:
    subdomains = set(obj.subdomain for obj in CoqDomain.directives.values())
    assert subdomains == set(chain(*(idx.subdomains for idx in CoqDomain.indices)))
    assert subdomains.issubset(CoqDomain.roles.keys())

    # Add domain, directives, and roles
    app.add_domain(CoqDomain)
    app.add_role("production", GrammarProductionRole)
    app.add_directive("coqtop", CoqtopDirective)
    app.add_directive("coqdoc", CoqdocDirective)
    app.add_directive("example", ExampleDirective)
    app.add_directive("inference", InferenceDirective)
    app.add_directive("preamble", PreambleDirective)
    app.add_transform(CoqtopBlocksTransform)
    app.connect('doctree-resolved', simplify_source_code_blocks_for_latex)

    # Add extra styles
    app.add_stylesheet("hint.min.css")
    app.add_stylesheet("ansi.css")
    app.add_stylesheet("coqdoc.css")
    app.add_javascript("notations.js")
    app.add_stylesheet("notations.css")

    return {'version': '0.1', "parallel_read_safe": True}
