from __future__ import annotations

from typing import Iterable

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
        # head = []
        # if self.data == "head":
        #     head.append(self)
        # for parent in self.parents:
        #     if parent.data == "head":
        #         return parent
        #     if parent != self:
        #         head.append(parent.get_head())
        head = []
        for node in self.get_all():
            if node.data == "head":
                head.append(node)

        if len(head) == 1:
            return head[0]
        if len(head) == 0:
            raise TypeError("0 heads found")
        raise TypeError("multiple heads found")

        # self.sync()
        # return self.get_head()

    def get_tail(self) -> Node:
        # if self.data == "tail":
        #     tail.append(self)
        # for child in self.children:
        #     if child.data == "tail":
        #         return child
        #     tail.append(child.get_tail())
        tail = []
        for node in self.get_all():
            if node.data == "tail":
                tail.append(node)

        if len(tail) == 1:
            return tail[0]
        if len(tail) == 0:
            raise TypeError("0 tails found")
        raise TypeError("multiple tails found")

    def weak_connections(self) -> set[Node]:
        """
        all nodes that eventually connects to node without any intermediate text-nodes
        :return:
        """
        connections = set()
        for parent in self.parents:
            if parent.data == "point":
                connections |= parent.weak_connections()
            else:
                connections.add(parent)
        return connections
    # </editor-fold>

    # <editor-fold desc="data fixers">
    def point_remove(self):
        """
        removes all points
        """
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

            # all children of
            possible: list[tuple[Node, set[node]]] = []
            for child in node.children:
                weak_connections = child.weak_connections()
                if len(weak_connections) >= 2:
                    possible.append((child, weak_connections))

            if len(possible) == 0:
                continue

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

    def box_convert(self: Node) -> StructureType:
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

        def eventually_connect(node: Node) -> set[Node]:
            """
            all nodes that current node eventually leeds to
            """
            out = children_in_front(node)
            for child in out.copy():
                out |= eventually_connect(child)

            return out

        def eventually_connect_from(node: Node) -> set[Node]:
            out = parents_behind(node)
            for parent in out.copy():
                out |= eventually_connect_from(parent)

            return out

        def parents_behind(node: Node) -> set[Node]:
            return node.parents & set(behind(node))

        def get_box_end(children) -> tuple[Node, bool]:
            """
            gets the first node that all children leeds to
                If they lead exclusively to that node then it
                returns (Node, False) ("improper_bounding_box" is false).
                Otherwise, it returns (Node, True).
            """
            improper_bounding_box = False  # flag
            shared_forward_nodes = set.intersection(*[eventually_connect(child) | {child} for child in children])

            # add all children in "f_ch" that are before the first "shared_backwards_nodes" to
            # "nodes_to_iterate"
            for part in sectioned_list:
                # break when it finds the first "shared_backwards_nodes"
                if any(x in shared_forward_nodes for x in part):
                    # get the last_node
                    last_node = shared_forward_nodes & set(part)

                    if len(last_node) > 1:
                        raise TypeError(f"there should be a point from "
                                        f"{[x.data for x in shared_forward_nodes]} to"
                                        f"{[x.data for x in last_node]}")

                    last_node = last_node.pop()

                    # check if it's an "improper_bounding_box"
                    if len(set.intersection(*[children_in_front(parent) for parent in parents_behind(last_node)])) > 1:
                        improper_bounding_box = True
                        continue
                        # continue until you actually find a "proper_box"

                    return last_node, improper_bounding_box

        def get_box_start(parents, find_proper_bounding_box=True) -> tuple[Node, bool]:
            """
            reverse of get_box_end()
            """
            improper_bounding_box = False  # flag
            shared_backwards_nodes = set.intersection(*[
                eventually_connect_from(parent) | {parent} for parent in parents])

            # add all children in "f_ch" that are before the first "shared_backwards_nodes" to
            # "nodes_to_iterate"
            for part in sectioned_list[::-1]:
                # break when it finds the first "shared_backwards_nodes"
                if any(x in shared_backwards_nodes for x in part):
                    # get the first_node
                    first_node = shared_backwards_nodes & set(part)

                    if len(first_node) > 1:
                        raise TypeError(f"there should be a point from "
                                        f"{[x.data for x in shared_backwards_nodes]} to"
                                        f"{[x.data for x in first_node]}")

                    first_node = first_node.pop()

                    # check if it's an "improper_bounding_box"
                    if len(set.intersection(*[parents_behind(child) for child in children_in_front(first_node)])) > 1:
                        improper_bounding_box = True
                        if find_proper_bounding_box:
                            # continue until you actually find a "proper_box"
                            continue

                    return first_node, improper_bounding_box

        def iterate_to(start: Node, end: Node) -> tuple[Node, StructureType]:
            """
            builds the struct from "start" to node before "end"
            (unless that node is an end of a

            iterate_to(a, d) => c, [a, b, c]
               a - b - c - d
            """

            node_iter = start
            part_struct: StructureType = [start]

            while True:
                f_ch = children_in_front(node_iter)

                if len(f_ch) == 0:
                    raise TypeError(f"got to tail before finding end ({end=} is before {start=})")

                elif len(f_ch) == 1:
                    out = f_ch.pop()

                    if out != end:
                        node_iter = out
                        part_struct.append(out)
                        continue

                else:
                    next_node, sub_part_struct = next_box(node_iter)
                    part_struct += sub_part_struct

                    if next_node != end:
                        node_iter = next_node
                        continue

                return node_iter, part_struct

        # def restrictive_iterate_to(start: Node, end: Node, allowed: set[Node]):
        #     behind_end = parents_behind(end)
        #     node_iter = start
        #     part_struct = [start]
        #
        #     while True:
        #         next_node, sub_part_struct = next_box(node_iter)
        #         part_struct += sub_part_struct
        #
        #         if next_node in behind_end:  # not checking if it's in front
        #             return part_struct
        #         else:
        #             node_iter = next_node

        def handle_improper_bounding_box():  # first_node: Node, last_node: Node):
            raise NotImplementedError("improper_bounding_box")
            # struct_part = []
            # to_be_cataloged = eventually_connect(first_node) & set(sum(sectioned_list[:section_index(last_node)], []))
            # for part in sectioned_list[section_index(first_node):section_index(last_node)]:
            #     struct_part += part
            #     # sub_part = []
            #     # for node in to_be_cataloged & set(part):
            #     #     f_ch = children_in_front(node)
            #     #     last_node, improper_bounding_box = get_box_end(f_ch)
            #     #
            #     #     if improper_bounding_box:
            #     #         continue
            # scope = eventually_connect(first_node) & eventually_connect_from(last_node)

            # struct_part = []
            # for sectioned_list_part in sectioned_list:

            # struct_part = [set(sectioned_list_part) & scope for sectioned_list_part in sectioned_list]

            # return {last_node}, struct_part + [last_node]

        def handle_proper_bounding_box(first_node: Node, last_node: Node):
            """
            handle_proper_bounding_box(a) => d, [(b, c), d]
                a - b - d
                  - c -
            """

            struct_part: StructureType = []
            cataloged_last_nodes = set()

            step_forward = children_in_front(first_node)

            # iterate all sub-parts inside box
            for child in set(step_forward):
                if child == last_node:
                    raise TypeError(f"Start of a box can't connect to it's own end. "
                                    f"((first_node: {first_node}) connects to "
                                    f"(last_node: {last_node}))")

                sub_nodes_before_last, sub_struct_part = iterate_to(child, last_node)
                struct_part.append(sub_struct_part)
                cataloged_last_nodes.add(sub_nodes_before_last)

            struct_part = [tuple(struct_part)]
            # struct_part.append(cataloged_last_nodes)
            # if all last_nodes are cataloged, complete the box.
            if len(parents_behind(last_node)) == len(cataloged_last_nodes):
                # return finished box
                return {last_node}, struct_part + [last_node]
            
            # return incomplete box 
            return set(cataloged_last_nodes), struct_part

        def next_box(node: Node) -> tuple[Node, StructureType]:
            """
            computes the next box after node

            see "handle_proper_bounding_box()" and "handle_improper_bounding_box()" for examples
            """

            f_ch = children_in_front(node)

            last_node, improper_bounding_box = get_box_end(f_ch)

            if improper_bounding_box:
                nodes_connected_to_last, struct_part = handle_improper_bounding_box()  # node, last_node)
            else:
                nodes_connected_to_last, struct_part = handle_proper_bounding_box(node, last_node)

            return nodes_connected_to_last.pop(), struct_part

        def resolve_hidden_boxes(node: Node) -> None:
            """
            Adds a point before some "hidden" boxes.

            A hidden box is a box whose start is the same as
            another box start. The point is added so that the
            start is a point instead of the same as the other
            start.
            """

            def compute_part(current: set[Node], options: list[set[Node]]):
                if len(current) == 1:
                    return current

                possible = []
                for option in options:
                    if next(iter(option)) in current and len(current) > len(option):
                        possible.append(option)

                some_point = Node("point")

                possible.sort(key=lambda x: len(x), reverse=True)

                cataloged = set()
                while len(possible) > 0:
                    cataloged |= set(possible[0])
                    sub_point, possible = compute_part(possible[0], possible)
                    some_point.add_connection(sub_point)

                for connection_node in set(current) - cataloged:
                    some_point.add_connection(connection_node)

                return some_point, possible

            box_starts = []
            for node in node.get_all():
                parents_behind_node = parents_behind(node)
                if len(parents_behind_node) > 1:
                    box_start, improper_bounding_box = get_box_start(parents_behind_node)
                    box_starts.append((box_start, node))

            while True:
                if len(box_starts) <= 1:
                    break

                box_start_node = box_starts[0][0]

                # all nodes with the same "box start"
                same_box_start = [box_start[1] for box_start in box_starts
                                  if box_start[0] == box_start_node]

                box_starts = [box_start for box_start in box_starts
                              if box_start[0] != box_start_node]

                if len(same_box_start) == 1:
                    break

                box_start_children = children_in_front(box_start_node)
                # list of all children of all same_box_start
                points_children = [box_start_children & eventually_connect_from(node)
                                   for node in same_box_start]

                for rm_connection_node in box_start_children:
                    box_start_node.remove_connection(rm_connection_node)

                box_start_node.add_connection(compute_part(
                    max(points_children, key=lambda x: len(x)),
                    points_children)[0])

                next(iter(box_start_node.children)).contract()

        def prevent_start_end_connection(node: Node) -> None:
            """
            Prevents all "box start" from connecting to its own "box end".

            By adding a point in the middle.
            """

            for node in node.get_all():
                children_in_front_node = children_in_front(node)
                if len(children_in_front_node) > 1:
                    box_end, _ = get_box_end(children_in_front_node)
                    if box_end in children_in_front_node:
                        node.remove_connection(box_end)
                        some_point = Node("point")
                        node.adopt(some_point)
                        box_end.r_adopt(some_point)

        sectioned_list = self.sectioned_list()
        resolve_hidden_boxes(self)
        sectioned_list = self.sectioned_list()
        prevent_start_end_connection(self)
        sectioned_list = self.sectioned_list()
        tail = self.get_tail()
        head = self.get_head()

        return iterate_to(head, tail)[1] + [tail]

    def structure_image(self: Node, text_size=100):
        def get_width(image):
            return image.size[0]

        def get_height(image):
            return image.size[1]

        def compute_part(part_struct) -> Image:

            def should_draw_line(j):
                if isinstance(part_struct[j], tuple):
                    return False

                if j < len(part_struct) - 1:

                    if isinstance(part_struct[j], Node) and \
                            isinstance(part_struct[j + 1], Node):
                        return False

                    if isinstance(part_struct[j + 1], tuple):
                        return False

                return True

            if isinstance(part_struct, Node):
                if len(part_struct.data) > 1:
                    text = ""
                else:
                    text = part_struct.data

                _, _, width, height = font.getbbox(text)

                # make space for the line
                if height == 0:
                    height = 1

                sub_image = Image.new("RGBA", (width, height))
                draw = ImageDraw.Draw(sub_image)
                draw.rectangle((0, 0) + sub_image.size, fill=(255, 100, 255))
                draw.text((0, 0), text, fill=(0, 0, 0), font=font)

                return sub_image

            if isinstance(part_struct, list):
                ignored_first_connection = False
                total_width = 0
                max_height = 0
                image_parts = []

                for i, part in enumerate(part_struct):
                    img_part = compute_part(part)
                    image_parts.append(img_part)

                    total_width += get_width(img_part)

                    if should_draw_line(i) and ignored_first_connection:
                        total_width += x_margin
                    ignored_first_connection = True

                    max_height = max(max_height, get_height(img_part))

                sub_image = Image.new("RGBA", (total_width, max_height))
                draw = ImageDraw.Draw(sub_image)
                # draw.rectangle((0, 0) + sub_image.size, fill=(100, 0, 0))

                # add all image_parts
                cur_tot_width = 0
                for i, part in enumerate(image_parts):
                    pos = (cur_tot_width, (max_height - get_height(part)) // 2)

                    sub_image.paste(part, pos)

                    cur_tot_width += get_width(part)

                    if should_draw_line(i):
                        cur_tot_width += x_margin

                # connect image_parts
                mid_pos = max_height // 2
                cur_tot_width = 0
                for i, part in enumerate(image_parts):
                    cur_tot_width += get_width(part)

                    if i == 0:
                        continue

                    if should_draw_line(i):
                        cur_tot_width += x_margin
                        draw.line(((cur_tot_width, mid_pos), (cur_tot_width + x_margin, mid_pos)))

                return sub_image

            if isinstance(part_struct, tuple):
                total_height = 0
                max_width = 0
                image_parts = []

                for part in part_struct:
                    img_part = compute_part(part)
                    image_parts.append(img_part)

                    total_height += get_height(img_part)
                    max_width = max(max_width, get_width(img_part))

                total_height += y_margin * (len(image_parts) - 1)
                max_width += x_margin * 2

                sub_image = Image.new("RGBA", (max_width, total_height))
                draw = ImageDraw.Draw(sub_image)
                # draw.rectangle((0, 0) + sub_image.size, fill=(0, 0, 0))

                # add all image_parts
                cur_tot_height = 0
                start_pos = 0, total_height // 2
                end_pos = max_width, total_height // 2
                for part in image_parts:
                    x_pos = (max_width - get_width(part)) // 2
                    y_mid_pos = cur_tot_height + get_height(part) // 2

                    # draw image_part
                    sub_image.paste(part, (x_pos, cur_tot_height))

                    # connect image_part
                    draw.line(connect(
                        start_pos,
                        (x_margin, y_mid_pos)
                    ))

                    draw.line(connect(
                        (max_width - x_margin, y_mid_pos),
                        end_pos
                    ))

                    # line connect
                    draw.line((
                        (x_margin, y_mid_pos),
                        (x_pos, y_mid_pos)
                    ))

                    draw.line((
                        (x_pos + part.width, y_mid_pos),
                        (max_width - x_margin, y_mid_pos)
                    ))

                    cur_tot_height += get_height(part) + y_margin

                return sub_image

        structure = self.box_convert()

        font = ImageFont.truetype('arial.ttf', text_size)
        _, _, x_margin, text_height = font.getbbox("ooo")
        y_margin = text_height // 4
        x_margin = x_margin // 2

        img = compute_part(structure)
        img.show()

    # </editor-fold>


# typehint for structure
StructurePartType = Iterable['structure_type'] | Node
StructureType = tuple[StructurePartType] | list[StructurePartType]
