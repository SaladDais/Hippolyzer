import abc
import ast
import typing

from arpeggio import Optional, ZeroOrMore, EOF, \
    ParserPython, PTNodeVisitor, visit_parse_tree
from arpeggio import RegExMatch as _


def literal():
    return [
        # Nightmare. str or bytes literal.
        # https://stackoverflow.com/questions/14366401/#comment79795017_14366904
        _(r'''b?(\"\"\"|\'\'\'|\"|\')((?<!\\)(\\\\)*\\\1|.)*?\1'''),
        _(r'\d+(\.\d+)?'),
        "None",
        "True",
        "False",
        # vector3 (tuple)
        _(r'\(\s*\d+(\.\d+)?\s*,\s*\d+(\.\d+)?\s*,\s*\d+(\.\d+)?\s*\)'),
        # vector4 (tuple)
        _(r'\(\s*\d+(\.\d+)?\s*,\s*\d+(\.\d+)?\s*,\s*\d+(\.\d+)?\s*,\s*\d+(\.\d+)?\s*\)'),
    ]


def identifier():
    return _(r'[a-zA-Z*]([a-zA-Z0-9*]+)?')


def field_specifier():
    return identifier, ZeroOrMore('.', identifier)


def unary_field_specifier():
    return field_specifier


def unary_expression():
    return Optional(["!"]), [unary_field_specifier, ("(", expression, ")")]


def meta_field_specifier():
    return "Meta", ".", identifier


def compare_val():
    return [literal, meta_field_specifier]


def binary_expression():
    return field_specifier, ["==", "!=", "^=", "$=", "~=", ">", ">=", "<", "<="], compare_val


def term():
    return [binary_expression, unary_expression]


def expression():
    return term, ZeroOrMore(["||", "&&"], expression)


def message_filter():
    return expression, EOF


class BaseFilterNode(abc.ABC):
    @abc.abstractmethod
    def match(self, msg) -> bool:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def children(self):
        raise NotImplementedError()


class UnaryFilterNode(BaseFilterNode, abc.ABC):
    def __init__(self, node):
        self.node: BaseFilterNode = node

    @property
    def children(self):
        return self.node


class BinaryFilterNode(BaseFilterNode, abc.ABC):
    def __init__(self, left_node, right_node):
        super().__init__()
        self.left_node: BaseFilterNode = left_node
        self.right_node: BaseFilterNode = right_node

    @property
    def children(self):
        return self.left_node, self.right_node


class UnaryNotFilterNode(UnaryFilterNode):
    def match(self, msg) -> bool:
        return not self.node.match(msg)


class OrFilterNode(BinaryFilterNode):
    def match(self, msg) -> bool:
        return self.left_node.match(msg) or self.right_node.match(msg)


class AndFilterNode(BinaryFilterNode):
    def match(self, msg) -> bool:
        return self.left_node.match(msg) and self.right_node.match(msg)


class MessageFilterNode(BaseFilterNode):
    def __init__(self, selector: typing.Sequence[str], operator: typing.Optional[str], value: typing.Optional):
        self.selector = selector
        self.operator = operator
        self.value = value

    def match(self, msg) -> bool:
        return msg.matches(self)

    @property
    def children(self):
        return self.selector, self.operator, self.value


class MetaFieldSpecifier(str):
    pass


class LiteralValue:
    """Only exists because we can't return `None` in a visitor, need to box it"""
    def __init__(self, value):
        self.value = value


class MessageFilterVisitor(PTNodeVisitor):
    def visit_identifier(self, node, children):
        return str(node.value)

    def visit_field_specifier(self, node, children):
        return children

    def visit_literal(self, node, children):
        return LiteralValue(ast.literal_eval(node.value))

    def visit_meta_field_specifier(self, node, children):
        return MetaFieldSpecifier(children[0])

    def visit_unary_field_specifier(self, node, children):
        # Looks like a bare field specifier with no operator
        return MessageFilterNode(tuple(children), None, None)

    def visit_unary_expression(self, node, children):
        if len(children) == 1:
            if isinstance(children[0], BaseFilterNode):
                return children[0]
            else:
                raise ValueError("What?")
        # Might have a unary !
        if children[0] == "!":
            return UnaryNotFilterNode(children[1])
        else:
            raise ValueError(f"Unrecognized unary prefix {children[0]}")

    def visit_binary_expression(self, node, children):
        return MessageFilterNode(tuple(children[0]), children[1], children[2])

    def visit_expression(self, node, children):
        if self.debug:
            print("Expression {}".format(children))
        if len(children) > 1:
            if children[1] == "&&":
                return AndFilterNode(children[0], children[2])
            elif children[1] == "||":
                return OrFilterNode(children[0], children[2])
            else:
                raise ValueError(f"Unrecognized operator {children[1]}")
        return children[0]


def compile_filter(filter_str) -> BaseFilterNode:
    filter_str = filter_str.strip()
    if not filter_str.strip():
        filter_str = "*"
    elif filter_str == "!":
        filter_str = "!*"
    parser = ParserPython(message_filter)
    parse_tree = parser.parse(filter_str)
    return visit_parse_tree(parse_tree, MessageFilterVisitor())
