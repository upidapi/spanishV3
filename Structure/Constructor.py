from . import Node


def convert(text: str, flags: list) -> Node:
    return convert_linear_word(text)


def convert_linear_word(text: str) -> Node:
    cur = Node("head")
    for char in text:
        next_node = Node(char)
        cur.adopt(next_node)
        cur = next_node
    cur.adopt(Node("tail"))
    return next(iter(cur.get_head().children))


def or_convert(text: str) -> Node:
    text.split("/")

    return Node("")  # temporary


def find_all(find_str: str, struct_node: Node) -> list[list[Node]]:
    """
    fins all "find_str" in struct_node
    """

    valid_options = [[node] for node in struct_node.get_all()]
    next_opt = []
    for char in find_str:
        for valid_option in valid_options:
            for child in valid_option[-1].children:
                if child.data == char:
                    next_opt.append(valid_option + [child])

        valid_options = next_opt

    return valid_options


def add_option(replace_str: str, with_str: str, struct_node: Node) -> None:
    """
    Adds "with_str" at all "replace_str" in "struct_node".
    """

    for valid_option in find_all(replace_str, struct_node):
        repl = convert_linear_word(with_str)
        repl.parents = valid_option[0].parents
        repl.children = valid_option[-1].children


def replace(replace_str: str, with_str: str, struct_node: Node) -> None:
    """
    Replaces all "replace_str" with "with_str".
    """

    add_option(replace_str, with_str, struct_node)

    for valid_option in find_all(replace_str, struct_node):
        for node in valid_option:
            if len(node.children) == 1 and len(node.parents) == 1:
                node.remove()


def make_optional(replace_str: str, struct_node: Node) -> None:
    replace(replace_str, "", struct_node)
