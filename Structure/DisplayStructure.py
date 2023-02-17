from . import Node, StructureType
from Bezier import connect

from PIL import Image, ImageFont, ImageDraw


def get_sectioned_list(struct_node: Node):
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
    queue = [struct_node.get_head()]

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


def get_section_index(node: Node, sectioned_list) -> int:
    for i, part in enumerate(sectioned_list):
        if node in part:
            return i


# <editor-fold desc="get specific node connections">
def in_front(node: Node, sectioned_list) -> list[Node]:
    out = []
    node_index = get_section_index(node, sectioned_list)
    for part in sectioned_list[node_index:]:
        out += part
    return out


def behind(node: Node, sectioned_list) -> list[Node]:
    out = []
    node_index = get_section_index(node, sectioned_list)
    for part in sectioned_list[:node_index]:
        out += part
    return out


def children_in_front(node: Node, sectioned_list) -> set[Node]:
    return node.children & set(in_front(node, sectioned_list))


def parents_behind(node: Node, sectioned_list) -> set[Node]:
    return node.parents & set(behind(node, sectioned_list))


def eventually_connect(node: Node, sectioned_list) -> set[Node]:
    """
    all nodes that current node eventually leeds to
    """
    out = children_in_front(node, sectioned_list)
    for child in out.copy():
        out |= eventually_connect(child, sectioned_list)

    return out


def eventually_connect_from(node: Node, sectioned_list) -> set[Node]:
    out = parents_behind(node, sectioned_list)
    for parent in out.copy():
        out |= eventually_connect_from(parent, sectioned_list)

    return out
# </editor-fold>


# <editor-fold desc="get box start/end">
def get_box_end(children, sectioned_list) -> tuple[Node, bool]:
    """
    gets the first node that all children leeds to
        If they lead exclusively to that node then it
        returns (Node, False) ("improper_bounding_box" is false).
        Otherwise, it returns (Node, True).
    """
    improper_bounding_box = False  # flag
    shared_forward_nodes = set.intersection(*[
        eventually_connect(child, sectioned_list) | {child}
        for child in children
    ])

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
            if len(set.intersection(*[
                children_in_front(parent, sectioned_list)
                for parent in parents_behind(last_node, sectioned_list)
            ])) > 1:
                improper_bounding_box = True
                continue
                # continue until you actually find a "proper_box"

            return last_node, improper_bounding_box


def get_box_start(parents, sectioned_list, find_proper_bounding_box=True) -> tuple[Node, bool]:
    """
    reverse of get_box_end()
    """
    improper_bounding_box = False  # flag
    shared_backwards_nodes = set.intersection(*[
        eventually_connect_from(parent, sectioned_list) | {parent} for parent in parents])

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
            if len(set.intersection(*[
                parents_behind(child, sectioned_list)
                for child in children_in_front(first_node, sectioned_list)
            ])) > 1:

                improper_bounding_box = True
                if find_proper_bounding_box:
                    # continue until you actually find a "proper_box"
                    continue

            return first_node, improper_bounding_box
# </editor-fold>


def fix_box_edge_cases(struct_node: Node):
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

        sectioned_list = get_sectioned_list(node)

        box_starts = []
        for node in node.get_all():
            parents_behind_node = parents_behind(node, sectioned_list)
            if len(parents_behind_node) > 1:
                box_start, improper_bounding_box = get_box_start(parents_behind_node, sectioned_list)
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

            box_start_children = children_in_front(box_start_node, sectioned_list)
            # list of all children of all same_box_start
            points_children = [box_start_children & eventually_connect_from(node, sectioned_list)
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

        sectioned_list = get_sectioned_list(node)

        for node in node.get_all():
            children_in_front_node = children_in_front(node, sectioned_list)
            if len(children_in_front_node) > 1:
                box_end, _ = get_box_end(children_in_front_node, sectioned_list)
                if box_end in children_in_front_node:
                    node.remove_connection(box_end)
                    some_point = Node("point")
                    node.adopt(some_point)
                    box_end.r_adopt(some_point)

    resolve_hidden_boxes(struct_node)
    prevent_start_end_connection(struct_node)


def box_convert(struct_node: Node) -> StructureType:
    def iterate_to(start: Node, end: Node) -> tuple[Node, StructureType]:
        """
        builds the struct from "start" to node before "end"
        unless that node is an end of a

        iterate_to(a, d) => c, [a, b, c]
           a - b - c - d
        """

        node_iter = start
        part_struct: StructureType = [start]

        while True:
            f_ch = children_in_front(node_iter, sectioned_list)

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
        # to_be_cataloged = eventually_connect(first_node) & set(sum(sectioned_list[:get_section_index(last_node)], []))
        # for part in sectioned_list[get_section_index(first_node):get_section_index(last_node)]:
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

        step_forward = children_in_front(first_node, sectioned_list)

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
        if len(parents_behind(last_node, sectioned_list)) == len(cataloged_last_nodes):
            # return finished box
            return {last_node}, struct_part + [last_node]

        # return incomplete box
        return set(cataloged_last_nodes), struct_part

    def next_box(node: Node) -> tuple[Node, StructureType]:
        """
        computes the next box after node

        see "handle_proper_bounding_box()" and "handle_improper_bounding_box()" for examples
        """

        f_ch = children_in_front(node, sectioned_list)

        last_node, improper_bounding_box = get_box_end(f_ch, sectioned_list)

        if improper_bounding_box:
            nodes_connected_to_last, struct_part = handle_improper_bounding_box()  # node, last_node)
        else:
            nodes_connected_to_last, struct_part = handle_proper_bounding_box(node, last_node)

        return nodes_connected_to_last.pop(), struct_part

    fix_box_edge_cases(struct_node)
    sectioned_list = get_sectioned_list(struct_node)
    tail = struct_node.get_tail()
    head = struct_node.get_head()

    return iterate_to(head, tail)[1] + [tail]


def structure_image(struct_node: Node, text_size=100):
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

    structure = box_convert(struct_node)

    font = ImageFont.truetype('arial.ttf', text_size)
    _, _, x_margin, text_height = font.getbbox("ooo")
    y_margin = text_height // 4
    x_margin = x_margin // 2

    img = compute_part(structure)
    img.show()
