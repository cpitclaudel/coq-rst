import re

from docutils import nodes, utils
from docutils.transforms import Transform
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.roles import code_role #, set_classes
from docutils.parsers.rst.directives.admonitions import BaseAdmonition

from sphinx import addnodes
from sphinx.roles import XRefRole
from sphinx.domains import Domain, ObjType
from sphinx.util.nodes import set_source_info
from sphinx.directives import ObjectDescription
from sphinx.ext.mathbase import MathDirective, displaymath

from . import coqdoc, notations
from .repl import CoqTop, ansicolors

def parse_notation(notation, source, line, rawtext=None):
    node = nodes.raw(rawtext or notation, notations.htmlize_str(notation), format="html")
    node.source, node.line = source, line
    return node

def highlight_using_coqdoc(sentence):
    tokens = coqdoc.lex(utils.unescape(sentence, 1))
    for classes, value in tokens:
        yield nodes.inline(value, value, classes=classes)

class CoqObject(ObjectDescription):
    TARGET_TEXTS = {
        'tacn': " (tactic notation)",
        'tacv': " (tactic variant)",
        'tac': " (tactic)",
        'opt': " (option)",
        'exn': " (error)",
        'vernac': " (command)",
    }

    option_spec = {
        'name': directives.unchanged
    }

    @property
    def _subdomain(self):
        raise NotImplementedError(self)

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

    def _record_name(self, name):
        # FIXME what happens if an option has the same name as a tactic notation?
        subdomain_names = self.env.domaindata['coq'][self._subdomain]
        if name in subdomain_names:
            self.state_machine.reporter.warning(
                'Duplicate Coq object: {}; other is at {}'.format(
                    name, self.env.doc2path(subdomain_names[name][0])),
                line=self.lineno)
        subdomain_names[name] = (self.env.docname, self.objtype)

    def _add_target(self, signode, name):
        targetid = "coq:{}.{}".format(self.objtype, nodes.make_id(name))
        if targetid not in self.state.document.ids:
            signode['ids'].append(targetid)
            signode['names'].append(name)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            self._record_name(name)
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

class LtacObject(CoqObject):
    @property
    def _subdomain(self):
        return "ltac"

class GallinaObject(CoqObject):
    @property
    def _subdomain(self):
        return "gallina"

class VernacObject(CoqObject):
    @property
    def _subdomain(self):
        return "vernac"

    def _name_from_signature(self, signature):
        return signature #FIXME

    def _render_signature(self, signature, signode):
        position = self.state_machine.get_source_and_line(self.lineno)
        tacn_node = parse_notation(signature, *position)
        signode += addnodes.desc_name(signature, '', tacn_node)

class PlainObject(CoqObject):
    def _render_signature(self, signature, signode):
        signode += addnodes.desc_name(signature, signature)

class NotationObject(CoqObject):
    def _render_signature(self, signature, signode):
        position = self.state_machine.get_source_and_line(self.lineno)
        tacn_node = parse_notation(signature, *position)
        signode += addnodes.desc_name(signature, '', tacn_node)

class TacticNotationObject(LtacObject, NotationObject):
    @property
    def _annotation(self):
        return None

class TacticNotationVariantObject(TacticNotationObject):
    @property
    def _annotation(self):
        return "Variant"

class TacticObject(LtacObject):
    #TODO
    pass

class OptionObject(VernacObject):
    @property
    def _annotation(self):
        return "Option"

# Uses “exn” since “err” already is a CSS class added by “writer_aux”.
class ExceptionObject(TacticNotationObject):
    @property
    def _subdomain(self):
        return "errors"

    @property
    def _annotation(self):
        return "Error"

    def _name_from_signature(self, signature):
        return signature

def NotationRole(role, rawtext, text, lineno, inliner, options={}, content=[]):
    notation = utils.unescape(text, 1)
    position = inliner.reporter.get_source_and_line(lineno)
    return [nodes.literal(rawtext, '', parse_notation(notation, *position, rawtext=rawtext))], []

def coqdoc_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    options['language'] = 'Coq'
    return code_role(role, rawtext, text, lineno, inliner, options, content)
    # Too heavy:
    # Forked from code_role to use our custom tokenizer
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
        node = nodes.container(content, *highlight_using_coqdoc(content), classes=['coqdoc', 'literal-block'])
        return [node]

class ExampleDirective(BaseAdmonition): #FIXME
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

    def add_coqtop_output(self):
        with CoqTop(coqtop_bin="/build/coq-8.5/bin/coqtop", color=True) as repl:
            for node in self.document.traverse(CoqtopBlocksTransform.is_coqtop_block):
                options = node['coqtop_options']

                opt_undo = 'undo' in options
                opt_reset = 'reset' in options
                opt_all, opt_none = 'all' in options, 'none' in options
                opt_in, opt_out = opt_all or 'in' in options, opt_all or 'out' in options

                unexpected_options = list(set(options) - set(('reset', 'undo', 'all', 'none', 'in', 'out')))
                if unexpected_options:
                    raise ValueError("Unexpected options for .. coqtop:: {}".format(unexpected_options))
                elif (opt_in or opt_out) and opt_none:
                    raise ValueError("Inconsistent options for .. coqtop:: ‘none’ with ‘in’, ‘out’, or ‘all’")
                elif opt_reset and opt_undo:
                    raise ValueError("Inconsistent options for .. coqtop:: ‘undo’ with ‘reset’")

                if opt_reset:
                    repl.sendline("Reset Initial.")
                pairs = []
                for sentence in node.rawsource.splitlines():
                    if sentence:
                        pairs.append((sentence, repl.sendline(sentence)))
                if opt_undo:
                    repl.sendline("Undo {}.".format(len(pairs)))

                dli = nodes.definition_list_item()
                dli['classes'] = ['coqtop-in'] * opt_in + ['coqtop-out'] * opt_out
                for sentence, output in pairs:
                    if opt_in:
                        # Use Coqdoq to highlight input
                        chunks = highlight_using_coqdoc(sentence)
                        dli += nodes.term(sentence, '', *chunks)
                    if opt_out:
                        # Convert automatic highlighting of output
                        chunks = AnsiColorsParser().colorize_str(output)
                        dli += nodes.definition(output, *chunks)
                node.children.clear()
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

class CoqDomain(Domain):
    """A domain to document Coq code."""

    name = 'coq'
    label = 'Coq'

    object_types = {
        # ObjType (= directive type) → (Local name, *xref-roles)
        'tacn': ObjType('tacn', 'tacn'),
        'tacv': ObjType('tacv', 'tacn'),
        'tac': ObjType('tac', 'tac'),
        'opt': ObjType('opt', 'opt'),
        'exn': ObjType('exn', 'exn'),
        'vernac': ObjType('vernac', 'vernac'),
    }

    directives = {
        'tacn': TacticNotationObject,
        'tacv': TacticNotationVariantObject,
        'tac': TacticObject,
        'opt': OptionObject,
        'exn': ExceptionObject,
        'vernac': VernacObject,
    }

    roles = { # FIXME merge some of these
        'tacn': XRefRole(),
        'tac': XRefRole(),
        'opt': XRefRole(),
        'exn': XRefRole(),
        'vernac': XRefRole(),
        'notation': NotationRole,
        'gallina': GallinaRole,
        'ltac': LtacRole,
        'n': NotationRole,
        'g': GallinaRole,
        'l': LtacRole,
    }

    data_version = 1
    initial_data = {
        'ltac': {},
        'gallina': {},
        'vernac': {},
        'errors': {},
    }

    def clear_doc(self, docname):
        dict().pop(docname, None)

def setup(app):
    app.add_domain(CoqDomain)
    app.add_directive("coqtop", CoqtopDirective)
    app.add_directive("coqdoc", CoqdocDirective)
    app.add_directive("example", ExampleDirective)
    app.add_directive("inference", InferenceDirective)
    app.add_directive("preamble", PreambleDirective)
    app.add_transform(CoqtopBlocksTransform)
    app.add_javascript("notations.js")
    app.add_stylesheet("notations.css")
    app.add_stylesheet("coqdoc.css")
    app.add_stylesheet("ansi.css")
    return {'version': '0.1'}   # identifies the version of our extension
