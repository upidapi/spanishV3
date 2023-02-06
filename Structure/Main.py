from __future__ import annotations

from PIL import Image, ImageFont, ImageDraw

from Bezier import connect


class Node:
    """
    WARNING!
    Do not store references to "head" nor "tail". (and maby "point")
    They have the possibility of being removed. Instead, use
    instance.get_head() for the head or instance.get_tail()
    for the latter.
    """

    # <editor-fold desc="other">
    def __init__(self, data):
        """
        THIS IS NOT IMPLEMENTED
        When stored in json form it's stored with parent keys.
        Every node has an id which is used to reference it. Kinda
        like how python shows the address of an object (by default)
        as a sort of id in the .children and .parents sets.

        data stores the necessary data
          if len(data) == 1: => raw data
            matches only exact char
          else: => special data
            "any" matches any char
            "head" the abs start (gets removed when merged)
            "tail" the abs end (gets removed when merged)
            "point" always 'skipped' simplifies structures
        """
        self.data: str = data
        self.children: set[Node] = set()
        self.parents: set[Node] = set()

    def __repr__(self):
        return self.data

    @property
    def siblings(self):
        out = set()
        for parent in self.parents:
            out |= parent.children
        # should the children.parents be included?
        # for parent in self.parents:
        #     out += parent.children
        return out

    @property
    def super_siblings(self):
        out = set()
        for parent in self.parents:
            for child in parent.children:
                if child.parents == self.parents and \
                        child.children == self.children:
                    out.add(child)
        return out

    @property
    def word_exclusive_child(self):
        if len(self.children) == 1:
            only_child = next(iter(self.children))
            if len(only_child.data) == 1:
                if len(only_child.parents) == 1:
                    return only_child

    # </editor-fold>

    # <editor-fold desc="child / parent managing">
    def remove_connection(self, child):
        self.children.remove(child)
        child.parents.remove(self)

    def add_connection(self, child):
        """
        connects self and child
        """
        self.children.add(child)
        child.parents.add(self)

    def remove(self) -> None:
        """
        Removes all references internal structure references to self.
        Does not remove the data contained by self, i.e. self.children,
        self.data etc.
        """
        for child in self.children:
            child.parents.remove(self)
        for parent in self.parents:
            parent.children.remove(self)

    def adopt(self, child) -> None:
        # remove head when merge
        if self.data == "tail" and len(self.parents) > 1 and \
                child.data == "head" and len(child.children) > 1:
            self.data = "point"
            for sub_child in child.children:
                self.adopt(sub_child)
            child.remove()
        elif self.data == "tail":
            # what happens when you r_adopt a lonely "tail"?
            for parent in self.parents:
                parent.adopt(child)
            self.remove()
        elif child.data == "head":
            # what happens when you adopt a lonely "head"?
            for sub_child in child.children:
                self.adopt(sub_child)
            child.remove()
        else:
            self.add_connection(child)

    def r_adopt(self, parent) -> None:
        parent.adopt(self)

    def parallelize(self, other) -> None:
        """parallelize self with respect to other"""
        for child in other.children:
            self.add_connection(child)
        for parent in other.parents:
            parent.add_connection(self)

    def insert(self, other) -> None:
        """
        inserts other between self and its children
        self => other => self.children
        """
        other.children = self.children
        for child in self.children:
            child.parents.remove(self)
            child.parents.add(other)

        self.children = {other}
        other.parents = {self}

    def r_insert(self, other) -> None:
        """
        inserts other between self and self its parents
        self.parents => other => self
        (kinda the direct opposite if insert)
        """
        other.parents = self.parents
        for parent in self.parents:
            parent.children.remove(self)
            parent.children.add(other)

        self.parents = {other}
        other.children = {self}

    def contract(self) -> None:
        """
        WARNING
        this practically removes self

        reverses the effect of instance.insert(self)
        self.parents => self => self.children
        =>
        self.parents => self.children
        """
        if len(self.parents) >= 2 and len(self.children) >= 2:
            self.data = "point"
        else:
            for parent in self.parents:
                for child in self.children:
                    parent.adopt(child)
            self.remove()

    def merge(self, other):
        self.get_tail().adopt(other.get_head())

    # </editor-fold>

    # <editor-fold desc="data retrieve">
    def get_all(self) -> set[Node]:
        last_len = 0
        cataloged = set()
        cataloged.add(self)
        while len(cataloged) != last_len:
            last_len = len(cataloged)
            for thing in cataloged.copy():
                cataloged |= thing.children
                cataloged |= thing.parents
        return cataloged

    def get_head(self) -> Node:
        head = []
        if self.data == "head":
            head.append(self)
        for parent in self.parents:
            if parent.data == "head":
                return parent
            if parent != self:
                head.append(parent.get_head())
        if len(head) == 1:
            return head[0]
        if len(head) == 0:
            raise TypeError("0 heads found")
        raise TypeError("multiple heads found")

        # self.sync()
        # return self.get_head()

    def get_tail(self) -> Node:
        tail = []
        if self.data == "tail":
            tail.append(self)
        for child in self.children:
            if child.data == "tail":
                return child
            tail.append(child.get_tail())
        if len(tail) == 1:
            return tail[0]
        if len(tail) == 0:
            raise TypeError("0 tails found")
        raise TypeError("multiple tails found")

    def nodes_to(self) -> set[Node]:
        connections = set()
        for parent in self.parents:
            if parent.data == "point":
                connections |= parent.nodes_to()
            else:
                connections.add(parent)
        return connections
    # </editor-fold>

    # <editor-fold desc="data fixers">
    def point_remove(self):
        for node in self.get_all():
            if node.data == "point":
                node.contract()

    def make_head_tail(self) -> None:
        """
        syncs the head/tail by
          merging all heads/tails
          adds things with no parents/children
        """

        heads = set()
        tails = set()
        for thing in self.get_all():
            if thing.data == "head":
                heads |= thing.children
                thing.remove()
            elif len(thing.parents) == 0:
                heads.add(thing)
            if thing.data == "tail":
                tails |= thing.parents
                thing.remove()
            elif len(thing.children) == 0:
                tails.add(thing)

        # don't accidentally remove head nor tail if it's "self"
        if self.data == "head":
            self.children = set()
            head = self
        else:
            head = Node("head")
        if self.data == "tail":
            self.children = set()
            tail = self
        else:
            tail = Node("tail")

        for thing in heads:
            head.adopt(thing)
        for thing in tails:
            thing.adopt(tail)

    def point_simplify(self):
        """
        Tries to visually simplify the structure by creating points where
        multiple things connects to the same nodes.
        """
        def recursion(n=0) -> list[list[list, set]]:
            """
            gets all permutations of different children inside "possible" (effectively)
            eg the children p[1], p[2], p[5] (p = possible)
            also returns their collective parents p[1].a & p[2].a & p[5].a (a = parents)
            returns [[[children], {collective parents}], ...]
            return list will also contain [[], None] the empty type
            """

            # [[children],{collective_parents}]
            if n == len(possible) - 1:
                return [[
                    [], None
                ], [
                    [possible[n][0]], set(possible[n][1])
                ]]

            out = []
            for part in recursion(n + 1):
                if part[1] is None:
                    out.append([[], None])
                    out.append([[possible[n][0]], set(possible[n][1])])
                else:
                    out.append(part)

                    collective_parents = part[1] & possible[n][1]
                    if len(collective_parents) >= 2:
                        out.append([
                            part[0] + [possible[n][0]],
                            collective_parents
                        ])

            return out

        for node in self.get_all():

            if len(node.children) < 2:
                continue

            possible = []
            for child in node.children:
                temp = child.nodes_to()
                if len(temp) >= 2:
                    possible.append((child, temp))

            if len(possible) > 0:
                temp = recursion()

                connection_options = []
                possible_connection_options = []

                for thing in temp:
                    children, parents = thing

                    if len(children) >= 2 and parents is not None:
                        possible_connection_options.append((set(thing[0]), parents))

                while len(possible_connection_options) > 0:

                    for i, option in enumerate(possible_connection_options):
                        direct_parents = []
                        children, parents = option

                        for child in children:
                            direct_parents += child.parents & parents

                        if len(direct_parents) >= max(len(parents), len(children)):
                            connection_options.append((i, direct_parents, children, parents))

                    if len(connection_options) == 0:
                        break

                    i, _, children, parents = \
                        max(connection_options, key=lambda x: len(x[1]))
                    possible_connection_options.pop(i)

                    for child in children:
                        for parent in child.parents & parents:
                            parent.remove_connection(child)

                    connection_point = Node("point")
                    for parent in parents:
                        parent.adopt(connection_point)
                    for child in children:
                        child.r_adopt(connection_point)

    def sync(self):
        self.make_head_tail()
        self.point_simplify()
    # </editor-fold>

    # <editor-fold desc="display functions">
    def sectioned_list_word_combine(self: Node):
        def push_forward(node):
            for x in layers:
                try:
                    x.remove(node)
                except ValueError:
                    pass
                else:
                    things.remove(node)

        def word_extend(node):
            if len(node.children) == 1:
                one_child = next(iter(node.children))
                if len(one_child.parents) == 1 and len(one_child.data) == 1:
                    return [node] + word_extend(one_child)
            return [node]

        ignore_push = set()  # don't push anything from ignore
        things = []
        layers = []
        queue = [self.get_head()]

        while len(queue) > 0:
            next_queue = set()
            layers.append(queue)
            things += queue

            for thing in queue:
                if things.count(thing) == 1:  # same as "< 2"
                    children = set(x for x in thing.children if x != thing) - ignore_push
                    for child in children:
                        if child not in ignore_push:
                            push_forward(child)
                            temp = set(word_extend(child))
                            next_queue |= temp
                            temp.remove(child)
                            ignore_push |= temp

            queue = list(next_queue)

        return layers

    def sectioned_list(self: Node):
        def remove_from_layers(node):
            for x in layers:
                try:
                    x.remove(node)
                except ValueError:
                    pass
                else:
                    things.remove(node)

        things = []
        layers = []
        queue = [self.get_head()]

        while len(queue) > 0:
            next_queue = set()
            layers.append(queue)
            things += queue

            for thing in queue:
                if things.count(thing) == 1:  # same as "< 2"
                    children = set(x for x in thing.children if x != thing)  # don't push self
                    next_queue |= set(children)

                    for child in children:
                        remove_from_layers(child)

            queue = list(next_queue)

        return layers

    def f_ch(self, sectioned_list):
        # todo might optimize (very inefficient)
        for i, part in enumerate(sectioned_list):
            if self in part:
                out = []
                for f_part in sectioned_list:
                    out += f_part
                return out

    # def section_groups(self: Node):
    #     sectioned_list = self.sectioned_list()
    #     f_ch = self.f_ch(sectioned_list)
    #     if len(f_ch) == 1:

    def section_groups(self: Node):
        sectioned_list = self.sectioned_list_word_combine()
        queue = [self.get_head()]

        while len(queue) > 0:
            cur = queue[-1]

    def box_convert(self: Node):
        def section_index(node: Node) -> int:
            for i, part in enumerate(sectioned_list):
                if node in part:
                    return i

        def in_front(node: Node) -> list[Node]:
            out = []
            node_index = section_index(node)
            for part in sectioned_list[node_index:]:
                out += part
            return out

        def behind(node: Node) -> list[Node]:
            out = []
            node_index = section_index(node)
            for part in sectioned_list[:node_index]:
                out += part
            return out

        def children_in_front(node: Node) -> set[Node]:
            return node.children & set(in_front(node))

        def parents_behind(node: Node) -> set[Node]:
            return node.parents & set(behind(node))

        def e_cn(node: Node) -> set[Node]:
            """
            all nodes that current node eventually leeds to
            """
            out = children_in_front(node)
            for child in out.copy():
                out |= e_cn(child)

            return out

        # <editor-fold desc="separated parts">
        def get_last_node(children) -> tuple[Node, int]:
            shared_forward_nodes = set.intersection(*[e_cn(child) for child in children])

            # add all children in "f_ch" that are before the first "shared_forward_nodes" to
            # "nodes_to_iterate"
            for part in enumerate(sectioned_list):
                # break when it finds the first "shared_forward_nodes"
                if any(x in shared_forward_nodes for x in part):
                    # get the last_node
                    last_node = shared_forward_nodes & set(part)

                    if len(last_node) > 1:
                        raise f"there should be a point from " \
                              f"{[x.data for x in shared_forward_nodes]} to" \
                              f"{[x.data for x in last_node]}"

                    last_node = last_node.pop()


                    return last_node
        # </editor-fold>

        # name is fucking misleading
        def iterate_to(start: Node, end: Node):
            behind_end = parents_behind(end)
            node_iter = start
            part_struct = [start]

            while True:
                next_node, sub_part_struct = step_forward(node_iter)
                part_struct += sub_part_struct

                if len(next_node) == 1:
                    next_node = next(iter(next_node))
                    if next_node in behind_end:  # not checking if it's in front
                        return part_struct
                    else:
                        node_iter = next_node

        def step_forward(node: Node, struct_part=None) -> tuple[set[Node], list[Node | list]]:  # , structure):
            if struct_part is None:
                struct_part = []

            f_ch = children_in_front(node)

            if len(f_ch) == 1:
                return f_ch, [node]

            last_node, last_index = get_last_node(f_ch)
            nodes_before_last = set(behind(last_node))

            nodes_connected_to_last = []
            stepped_forward = f_ch.copy()

            for child in set(stepped_forward) & nodes_before_last:
                sub_nodes_before_last, sub_struct_part = iterate_to(child, last_node)
                struct_part += sub_struct_part
                nodes_before_last.add(sub_nodes_before_last)

            # while True:
            #     nodes_to_iterate = set(stepped_forward) & nodes_before_last  # nodes to step forward later
            #
            #     if not len(nodes_to_iterate):
            #         break
            #
            #     stepped_forward = []
            #     for child in nodes_to_iterate:
            #         next_nodes, sub_part_struct = step_forward(child)
            #
            #         if child in parents_behind(last_node) or \
            #                 len(next_nodes) > 1:
            #             nodes_connected_to_last += next_nodes
            #             continue
            #
            #         stepped_forward += next_nodes

            # if we have all f_connections to last_node

            struct_part.append(nodes_connected_to_last)
            if len(parents_behind(last_node)) == len(nodes_connected_to_last):
                struct_part.append(last_node)

                return {last_node}, struct_part
            return set(nodes_connected_to_last), struct_part

        sectioned_list = self.sectioned_list_word_combine()

        return iterate_to(self.get_head(), self.get_tail()) + [self.get_tail()]

    def order_list(self: Node):
        things_left: list[list[Node]] = self.sectioned_list_word_combine()
        path: list[Node] = [self.get_head()]
        ordered: list[list[Node]] = [[] for _ in range(len(things_left))]
        ordered[0] = path.copy()

        while len(path) > 0:
            cur = path[-1]
            pos = len(path) - 1

            # prio:  same_row_reference => child => super_sibling => parent
            # prio pos dif: (0) => (> 0) => ("0") => (< 0)

            # same_row_reference
            if len(cur.children) == 1 and cur.children & set(things_left[pos]):
                one_child = next(iter(cur.children))
                if len(one_child.parents) == 1:
                    things_left[pos].remove(one_child)
                    ordered[pos].append(one_child)
                    path[-1] = one_child
                    continue

            # child
            if pos + 1 < len(things_left):
                t = list(cur.children & set(things_left[pos + 1]))
                if t:
                    things_left[pos + 1].remove(t[0])
                    ordered[pos + 1].append(t[0])
                    path.append(t[0])
                    continue

            # super_sibling
            t = list(cur.super_siblings & set(things_left[pos]))
            if t:
                things_left[pos].remove(t[0])
                ordered[pos].append(t[0])
                path[-1] = t[0]
                continue

            # # siblings
            # t = list(cur.siblings & set(things_left[pos]))
            # if t:
            #     things_left[pos].remove(t[0])
            #     ordered[pos].append(t[0])
            #     path[-1] = t[0]
            #     continue

            # parent
            path.pop(-1)

        return ordered

    def display_nodes(self: Node):
        # might need to check if node.word_exclusive_child is in column
        def recursion(node):
            temp = node.word_exclusive_child
            if temp:
                return [node, *recursion(temp)]
            return [node]

        if len(self.data) == 1:
            return recursion(self)
        return []

    @staticmethod
    def convert_nodes_text(nodes: list[Node]):
        word = ""
        for node in nodes:
            word += node.data
        return word

    def get_width(self):
        return font.getbbox(
            self.convert_nodes_text(self.display_nodes())
        )[2]


    def gui_convert(self: Node, text_size=100):
        # ordered_list = structure.order_list()
        global font

        # ordered_list = [["head", ], ["a", "b", "c", ], ["d", "point", ], ["e", "f", "g", ], ["tail", ]]
        ordered_list = self.order_list()

        font = ImageFont.truetype('arial.ttf', text_size)
        _, _, x_margin, text_height = font.getbbox("ooo")
        y_margin = text_height // 2

        text_x = []
        for col in ordered_list:
            max_x = 0
            for node in col:
                max_x = max(node.get_width(), max_x)
            text_x.append(max_x)

        text_y = [text_height * len(col) for col in ordered_list]
        # print(text_x, text_y)

        img = Image.new("RGBA", (
            sum(text_x) + x_margin * (len(text_x) - 1),
            max(text_y) + y_margin * (len(text_y) - 1)))
        draw = ImageDraw.Draw(img)

        text_pos = {}
        for i, col in enumerate(ordered_list):
            x_pos = sum(text_x[:i]) + i * x_margin

            for j, row in enumerate(col):
                y_pos = j * (text_height + y_margin)
                width = row.get_width()

                text_pos[row] = x_pos, y_pos, width, col

        text_pos_left = text_pos.copy()
        while len(text_pos_left) > 0:
            # img.show()
            node = next(iter(text_pos_left.keys()))
            x, y, w, col = text_pos[node]
            del text_pos_left[node]

            if len(node.data) == 1:
                nodes_displayed = node.display_nodes()
                for rm_node in nodes_displayed:
                    text_pos_left.pop(rm_node, None)
                draw.text((x, y), node.convert_nodes_text(nodes_displayed), fill=(0, 0, 0), font=font)
                w = node.get_width()
                node = nodes_displayed[-1]

            if node.data == "head":
                for child in node.children:
                    cx, cy, cw, _ = text_pos[child]
                    draw.line(((0, cy + text_height // 2),
                               (cx, cy + text_height // 2)))
                continue
            for child in node.children:
                cx, cy, cw, _ = text_pos[child]
                if child.data == "tail":
                    draw.line(((x + w, y + text_height // 2),
                               (cx + cw + 10, y + text_height // 2)))

                    continue
                draw.line(connect((x + w, y + text_height // 2),
                                  (cx, cy + text_height // 2)))
                # draw.line(((x + w, y + text_height // 2),
                #           (cx, cy + text_height // 2)))

        img.show()
    # </editor-fold>

# todo rename "thing" to "node"
# todo add typehints
