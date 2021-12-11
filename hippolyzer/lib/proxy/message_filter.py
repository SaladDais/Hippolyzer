import abc
import ast
import typing

from arpeggio import Optional, ZeroOrMore, EOF, \
    ParserPython, PTNodeVisitor, visit_parse_tree, RegExMatch, OneOrMore


def literal():
    return [
        # Nightmare. str or bytes literal.
        # https://stackoverflow.com/questions/14366401/#comment79795017_14366904
        RegExMatch(r'''b?(\"\"\"|\'\'\'|\"|\')((?<!\\)(\\\\)*\\\1|.)*?\1'''),
        # base16
        RegExMatch(r'0x[0-9a-fA-F]+'),
        # base10 int or float.
        RegExMatch(r'\d+(\.\d+)?'),
        "None",
        "True",
        "False",
        # vector3 (tuple)
        RegExMatch(r'\(\s*\d+(\.\d+)?\s*,\s*\d+(\.\d+)?\s*,\s*\d+(\.\d+)?\s*\)'),
        # vector4 (tuple)
        RegExMatch(r'\(\s*\d+(\.\d+)?\s*,\s*\d+(\.\d+)?\s*,\s*\d+(\.\d+)?\s*,\s*\d+(\.\d+)?\s*\)'),
    ]


def identifier():
    # Identifiers are allowed to have "-". It's not a special character
    # in our grammar, and we expect them to show up some places, like header names.
    return RegExMatch(r'[a-zA-Z*]([a-zA-Z0-9_*-]+)?')


def field_specifier():
    return identifier, ZeroOrMore('.', identifier)


def unary_field_specifier():
    return field_specifier


def unary_expression():
    return Optional(["!"]), [unary_field_specifier, ("(", expression, ")")]


def meta_field_specifier():
    return "Meta", OneOrMore(".", identifier)


def enum_field_specifier():
    return identifier, ".", identifier


def compare_val():
    return [literal, meta_field_specifier, enum_field_specifier]


def binary_expression():
    return field_specifier, ["==", "!=", "^=", "$=", "~=", ">", ">=", "<", "<=", "&"], compare_val


def term():
    return [binary_expression, unary_expression]


def expression():
    return term, ZeroOrMore(["||", "&&"], expression)


def message_filter():
    return expression, EOF


class MatchResult(typing.NamedTuple):
    result: bool
    fields: typing.List[typing.Tuple]

    def __bool__(self):
        return self.result


class BaseFilterNode(abc.ABC):
    @abc.abstractmethod
    def match(self, msg, short_circuit=True) -> MatchResult:
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
    def match(self, msg, short_circuit=True) -> MatchResult:
        # Should we pass fields up here? Maybe not.
        return MatchResult(not self.node.match(msg, short_circuit), [])


class OrFilterNode(BinaryFilterNode):
    def match(self, msg, short_circuit=True) -> MatchResult:
        left_match = self.left_node.match(msg, short_circuit)
        if left_match and short_circuit:
            return MatchResult(True, left_match.fields)

        right_match = self.right_node.match(msg, short_circuit)
        if right_match and short_circuit:
            return MatchResult(True, right_match.fields)

        if left_match or right_match:
            # Fine since fields should be empty when result=False
            return MatchResult(True, left_match.fields + right_match.fields)
        return MatchResult(False, [])


class AndFilterNode(BinaryFilterNode):
    def match(self, msg, short_circuit=True) -> MatchResult:
        left_match = self.left_node.match(msg, short_circuit)
        if not left_match:
            return MatchResult(False, [])
        right_match = self.right_node.match(msg, short_circuit)
        if not right_match:
            return MatchResult(False, [])
        return MatchResult(True, left_match.fields + right_match.fields)


class MessageFilterNode(BaseFilterNode):
    def __init__(self, selector: typing.Sequence[str], operator: typing.Optional[str], value: typing.Optional):
        self.selector = selector
        self.operator = operator
        self.value = value

    def match(self, msg, short_circuit=True) -> MatchResult:
        return msg.matches(self, short_circuit)

    @property
    def children(self):
        return self.selector, self.operator, self.value


class MetaFieldSpecifier(tuple):
    pass


class EnumFieldSpecifier(typing.NamedTuple):
    enum_name: str
    field_name: str


class LiteralValue:
    """Only exists because we can't return `None` in a visitor, need to box it"""
    def __init__(self, value):
        self.value = value


class MessageFilterVisitor(PTNodeVisitor):
    def visit_identifier(self, node, _children):
        return str(node.value)

    def visit_field_specifier(self, _node, children):
        return children

    def visit_literal(self, node, _children):
        return LiteralValue(ast.literal_eval(node.value))

    def visit_meta_field_specifier(self, _node, children):
        return MetaFieldSpecifier(children)

    def visit_enum_field_specifier(self, _node, children):
        return EnumFieldSpecifier(*children)

    def visit_unary_field_specifier(self, _node, children):
        # Looks like a bare field specifier with no operator
        return MessageFilterNode(tuple(children), None, None)

    def visit_unary_expression(self, _node, children):
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

    def visit_binary_expression(self, _node, children):
        return MessageFilterNode(tuple(children[0]), children[1], children[2])

    def visit_expression(self, _node, children):
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
