import json

from . import Node

import uuid


def covert_to_json(struct_node: Node) -> str:
    node_to_id = {}
    for node in struct_node.get_all():
        node_to_id[node] = uuid.uuid4()

    def convert_object_reference(temp: set[Node]):
        return set(*[node_to_id[thing] for thing in temp])

    json_object = {}
    for node in struct_node.get_all():
        json_object[node_to_id[node]] = {
            "data": node.data,
            "parents": convert_object_reference(node.parents),
            "children": convert_object_reference(node.children)}

    return json.dumps(json_object)


def covert_to_struct(json_str: str) -> Node:
    json_object: dict = json.loads(json_str)

    id_to_node = {}
    for node_id in json_object.keys():
        id_to_node[node_id] = Node("")

    def convert_id_reference(temp: set[Node]):
        return set(*[id_to_node[thing] for thing in temp])

    for node_id, data in json_object:
        node = id_to_node[node_id]
        node.data = data["data"]
        node.parents = convert_id_reference(data["parents"])
        node.children = convert_id_reference(data["children"])

    return next(iter(id_to_node.items()))
