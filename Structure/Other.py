from typing import Iterable

from . import Node

# typehint for structure
StructurePartType = Iterable['structure_type'] | Node
StructureType = tuple[StructurePartType] | list[StructurePartType]