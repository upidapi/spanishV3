from . import Node


def get_direct_char_connections(node):
    out = set()
    for child in node.children:
        if child.data == "point":
            out |= get_direct_char_connections(child)
        out.add(child)
    return out


def check_correct(node: Node, text: str):
    node.head_tail_simplify()

    valid_nodes: set[Node] = {node.get_head()}

    for char in text:
        valid_next_steps: set[Node] = set()
        for valid_node in valid_nodes:
            valid_next_steps |= set([child for child in get_direct_char_connections(valid_node)
                                     if child.data == char])
        valid_nodes = valid_next_steps

    tail = node.get_tail()
    return any([valid_end in tail for valid_end in valid_nodes])
