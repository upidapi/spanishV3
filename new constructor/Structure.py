from __future__ import annotations


class Node:
    """
    WARNING!
    Do not store references to "head" nor "tail". (and maby "point")
    They have the possibility of being removed. Instead, use
    instance.get_head() for the head or instance.get_tail()
    for the latter.
    """

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
        self.data = data
        self.children = set()
        self.parents = set()

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

    # child / parent managing
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

    @staticmethod
    def sandwich(a, b, c):
        a.get_tail().adopt(b.get_head())
        b.get_tail().adopt(c.get_head())

    # data retrieve
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

    # data fixers
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

    # display functions
    def print(self, ide=None):
        def push_forward(thing):
            for x in layers:
                try:
                    x.remove(thing)
                except ValueError:
                    pass

        layers = [[self.get_head()]]
        some_name = layers[-1].copy()
        while 0 < len(some_name):
            for part in some_name:
                some_name.pop(0)
                if any(part in x for x in layers[:-1]):
                    continue
                if part.data == "tail":
                    continue
                layers.append([])
                for sub_part in part.children:
                    push_forward(sub_part)
                    layers[-1].append(sub_part)
                    some_name.append(sub_part)

        if ide is None:
            print(layers)
        else:
            print(ide, layers)
        return layers

    def sectioned_list(self):
        def push_children(parent):
            for child in parent.children:
                for x in layers:
                    try:
                        x.remove(child)
                    except ValueError:
                        pass
                    else:
                        things.remove(child)

        things = []
        layers = []
        queue = [self.get_head()]

        while len(queue) > 0:
            next_queue = set()
            layers.append(queue)
            things += queue

            for thing in queue:
                if things.count(thing) == 1:
                    push_children(thing)
                    next_queue |= thing.children

            queue = list(next_queue)

        return layers

    def order_list(self):
        things_left: list[list[Node]] = self.sectioned_list()
        path: list[Node] = [self.get_head()]
        ordered: list[list[Node]] = [[] for _ in range(len(things_left))]
        ordered[0] = path.copy()

        while len(path) > 0:
            cur = path[-1]
            pos = len(path) - 1

            # prio: child => super_sibling => sibling => parent
            if pos + 1 < len(things_left):
                # child
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

            # siblings
            t = list(cur.siblings & set(things_left[pos]))
            if t:
                things_left[pos].remove(t[0])
                ordered[pos].append(t[0])
                path[-1] = t[0]
                continue

            # parent
            path.pop(-1)

        return ordered

    def display(self):
        def get_step_up():
            j = i - 1
            while j > 0:
                for thing in or_lay[j]:
                    temp = get_next_step(j + 1, thing)
                    if temp:
                        return j, temp

                j -= 1
            return False

        def get_next_step(j, thing):
            j += 1
            while j < len(layers):
                for child in thing.children:
                    try:
                        k = layers[j].index(child)
                        new_val = layers[j][k]
                        layers[j].pop(k)
                        or_lay[j].append(new_val)
                        return j, new_val

                    except ValueError:
                        pass

                j += 1
            return False

        # organize
        layers = self.sectioned_list()
        or_lay = [[] for _ in range(len(layers))]

        layers[0] = []
        current = self.get_head()
        or_lay[0] = [current]

        i = 0
        while True:
            # if len(or_lay) + 1 > i:
            #     or_lay.append([])
            x = get_next_step(i, current)
            if x:
                i, current = x
            else:
                x = get_step_up()
                if x:
                    i, current = x
                else:
                    break
        print(or_lay)

    def __repr__(self):
        return self.data


# todo rename "thing" to "node"
# todo add typehints
