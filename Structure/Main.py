from __future__ import annotations

from typing import Iterable


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
        """
        runs all "data fixers" on self
        """

        self.make_head_tail()
        self.point_simplify()
    # </editor-fold>


# typehint for structure
StructurePartType = Iterable['structure_type'] | Node
StructureType = tuple[StructurePartType] | list[StructurePartType]
