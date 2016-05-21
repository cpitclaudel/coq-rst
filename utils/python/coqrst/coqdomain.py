import re
from itertools import chain
from collections import defaultdict

from docutils import nodes, utils
from docutils.transforms import Transform
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.roles import code_role #, set_classes
from docutils.parsers.rst.directives.admonitions import BaseAdmonition

from sphinx import addnodes
# from sphinx.locale import l_
from sphinx.roles import XRefRole
from sphinx.util.nodes import set_source_info, make_refnode
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType, Index
from sphinx.ext.mathbase import MathDirective, displaymath

from .repl import CoqTop, ansicolors
from . import coqdoc
from .notations.sphinx import sphinxify
from .notations.plain import stringify_with_ellipses

def parse_notation(notation, source, line, rawtext=None):
    node = nodes.inline(rawtext or notation, '', *sphinxify(notation), classes=['notation'])
    node.source, node.line = source, line
    return node

def highlight_using_coqdoc(sentence):
    tokens = coqdoc.lex(utils.unescape(sentence, 1))
    for classes, value in tokens:
        yield nodes.inline(value, value, classes=classes)

def make_target(objtype, targetid):
    return "coq:{}.{}".format(objtype, targetid)

class CoqObject(ObjectDescription):
    TARGET_TEXTS = {
        # Object type → suffix in indices
        'tacn': " (tactic notation)",
        'tacv': " (tactic variant)",
        'tac': " (tactic)",
        'opt': " (option)",
        'exn': " (error)",
        'cmd': " (command)",
    }

    option_spec = {
        'name': directives.unchanged
    }

    """The semantic domain in which this object lives.
    It matches exactly one of the roles used for cross-referencing."""
    subdomain = None

    def _subdomain(self):
        if self.subdomain is None:
            raise ValueError()
        return self.subdomain

    @property
    def _annotation(self):
        raise NotImplementedError(self)

    def _name_from_signature(self, signature):
        return None

    def _render_signature(self, signature, signode):
        raise NotImplementedError(self)

    def handle_signature(self, signature, signode):
        if self._annotation:
            annotation = self._annotation + ' '
            signode += addnodes.desc_annotation(annotation, annotation)
        self._render_signature(signature, signode)
        return self._name_from_signature(signature)

    @property
    def _index_suffix(self):
        return CoqObject.TARGET_TEXTS.get(self.objtype, "")

    def _record_name(self, name, target_id):
        names_in_subdomain = self.env.domaindata['coq']['objects'][self._subdomain()]
        # Check that two objects in the same domain don't have the same name
        if name in names_in_subdomain:
            self.state_machine.reporter.warning(
                'Duplicate Coq object: {}; other is at {}'.format(
                    name, self.env.doc2path(names_in_subdomain[name][0])),
                line=self.lineno)
        names_in_subdomain[name] = (self.env.docname, self.objtype, target_id)

    def _add_target(self, signode, name):
        targetid = make_target(self.objtype, nodes.make_id(name))
        if targetid not in self.state.document.ids:
            signode['ids'].append(targetid)
            signode['names'].append(name)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            self._record_name(name, targetid)
        return targetid

    def _add_index_entry(self, name, target):
        index_text = name + self._index_suffix
        self.indexnode['entries'].append(('single', index_text, target, '', None))

    def run(self):
        [idx, node] = super().run()
        custom_name = self.options.get("name")
        if custom_name:
            self.add_target_and_index(custom_name, "", node.children[0])
        return [idx, node]

    def add_target_and_index(self, name, _, signode):
        if name:
            target = self._add_target(signode, name)
            self._add_index_entry(name, target)
            return target

class PlainObject(CoqObject):
    def _render_signature(self, signature, signode):
        signode += addnodes.desc_name(signature, signature)

class NotationObject(CoqObject):
    def _render_signature(self, signature, signode):
        position = self.state_machine.get_source_and_line(self.lineno)
        tacn_node = parse_notation(signature, *position)
        signode += addnodes.desc_name(signature, '', tacn_node)

class TacticObject(CoqObject):
    subdomain = "tac"

class GallinaObject(CoqObject):
    subdomain = "thm"

class VernacObject(NotationObject):
    subdomain = "cmd"

    @property
    def _annotation(self):
        return "Command"

    def _name_from_signature(self, signature):
        return stringify_with_ellipses(signature)

class VernacVariantObject(VernacObject):
    @property
    def _annotation(self):
        return "Variant"

class TacticNotationObject(NotationObject):
    subdomain = "tacn"

    @property
    def _annotation(self):
        return None

class TacticNotationVariantObject(TacticNotationObject):
    @property
    def _annotation(self):
        return "Variant"

class OptionObject(NotationObject):
    subdomain = "opt"

    @property
    def _annotation(self):
        return "Option"

    def _name_from_signature(self, signature):
        return stringify_with_ellipses(signature)

# Uses “exn” since “err” already is a CSS class added by “writer_aux”.
class ExceptionObject(NotationObject):
    subdomain = "exn"

    @property
    def _annotation(self):
        return "Error"

    def _name_from_signature(self, signature):
        return stringify_with_ellipses(signature)

def NotationRole(role, rawtext, text, lineno, inliner, options={}, content=[]):
    notation = utils.unescape(text, 1)
    position = inliner.reporter.get_source_and_line(lineno)
    return [nodes.literal(rawtext, '', parse_notation(notation, *position, rawtext=rawtext))], []

def coqdoc_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
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

# FIXME pass different languages?
LtacRole = GallinaRole = VernacRole = coqdoc_role

class CoqtopDirective(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True

    def run(self):
        content = '\n'.join(self.content)
        options = self.arguments[0].split() if self.arguments else ['in']
        if 'all' in options:
            options = list(set(options + ['in', 'out']))
        node = nodes.container(content, coqtop_options = options, classes=['coqtop', 'literal-block'])
        self.add_name(node)
        return [node]

class CoqdocDirective(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        content = '\n'.join(self.content)
        node = nodes.inline(content, '', *highlight_using_coqdoc(content), classes=['coqdoc'])
        wrapper = nodes.container(content, node, classes=['literal-block'])
        return [wrapper]

class ExampleDirective(BaseAdmonition):
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
    def run(self):
        self.options['nowrap'] = True
        [node] = super().run()
        node['classes'] = ["math-preamble"]
        return [node]

class InferenceDirective(Directive):
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
        return r'\hspace{3em}'.join(op.strip().splitlines())

    def prepare_latex(self, content):
        parts = re.split('^ *----+ *$', content, flags=re.MULTILINE)
        if len(parts) != 2:
            raise self.error('Expected two parts in inference::, separated by a rule (----).')

        top, bottom = tuple(InferenceDirective.prepare_latex_operand(p) for p in parts)
        return "\\frac{" + top + "}{" + bottom + "}"

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
    """ Inserts output of embedded Coq code blocks commands. """
    default_priority = 10

    @staticmethod
    def is_coqtop_block(node):
        return ('coqtop_options' in node)

    @staticmethod
    def split_sentences(source):
        return re.split(r"(?<=(?<!\.)\.)\s+", source)

    @staticmethod
    def parse_options(options):
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
        is_empty = contents is not None and re.match(r"^\s*$", contents)
        if is_empty or not should_show:
            return ['coqtop-hidden']
        else:
            return []

    def add_coqtop_output(self):
        with CoqTop(coqtop_bin="/build/coq-8.5/bin/coqtop", color=True) as repl:
            for node in self.document.traverse(CoqtopBlocksTransform.is_coqtop_block):
                options = node['coqtop_options']
                opt_undo, opt_reset, opt_input, opt_output = self.parse_options(options)

                if opt_reset:
                    repl.sendline("Reset Initial.")
                pairs = []
                for sentence in self.split_sentences(node.rawsource):
                    pairs.append((sentence, repl.sendline(sentence)))
                if opt_undo:
                    repl.sendline("Undo {}.".format(len(pairs)))

                dli = nodes.definition_list_item()
                for sentence, output in pairs:
                    # Use Coqdoq to highlight input
                    in_chunks = highlight_using_coqdoc(sentence)
                    dli += nodes.term(sentence, '', *in_chunks, classes=self.block_classes(opt_input))
                    # Parse ANSI sequences to highlight output
                    out_chunks = AnsiColorsParser().colorize_str(output)
                    dli += nodes.definition(output, *out_chunks, classes=self.block_classes(opt_output, output))
                node.clear()
                node += nodes.definition_list(node.rawsource, dli)

    def merge_consecutive_coqtop_blocks(self):
        """Merge consecutive divs wraping lists of command; keep ‘dl’s separate."""
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
    """
    Index subclass to provide subdomain-specific indices.
    """

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
    lowercase = True,
    innernodeclass = nodes.inline
    warn_dangling = True

    def process_link(self, env, refnode, has_explicit_title, title, target):
        if not has_explicit_title:
            index = CoqDomain.find_index_by_name(target)
            if index:
                title = index.localname
        return title, target

class CoqDomain(Domain):
    """A domain to document Coq code."""

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
        'l': LtacRole,
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

def setup(app):
    app.add_domain(CoqDomain)
    app.add_directive("coqtop", CoqtopDirective)
    app.add_directive("coqdoc", CoqdocDirective)
    app.add_directive("example", ExampleDirective)
    app.add_directive("inference", InferenceDirective)
    app.add_directive("preamble", PreambleDirective)
    app.add_transform(CoqtopBlocksTransform)
    # app.add_javascript("jquery-ui.min.js")
    # app.add_stylesheet("jquery-ui.min.css")
    app.add_stylesheet("hint.min.css")
    app.add_stylesheet("ansi.css")
    app.add_stylesheet("coqdoc.css")
    app.add_javascript("notations.js")
    app.add_stylesheet("notations.css")
    # Sanity checks:
    subdomains = set(obj.subdomain for obj in CoqDomain.directives.values())
    assert subdomains == set(chain(*(idx.subdomains for idx in CoqDomain.indices)))
    assert subdomains.issubset(CoqDomain.roles.keys())
    return {'version': '0.1', "parallel_read_safe": True}
