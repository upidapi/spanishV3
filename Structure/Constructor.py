from Main import Node


def convert(text: str) -> Node:
    cur = Node("head")
    for char in text:
        next_node = Node(char)
        cur.adopt(next_node)
        cur = next_node
    cur.adopt(Node("tail"))
    return next(iter(cur.get_head().children))
