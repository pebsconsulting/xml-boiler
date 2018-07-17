#  Copyright (c) 2018 Victor Porton,
#  XML Boiler - http://freesoft.portonvictor.org
#
#  This file is part of XML Boiler.
#
#  XML Boiler is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.

# the second algorithm from https://en.wikiversity.org/wiki/Automatic_transformation_of_XML_namespaces/Transformations/Automatic_transformation

from .next_script_base import ScriptsIteratorBase


class ScriptsIterator(ScriptsIteratorBase):
    def __next__(self):
        next_outer = self._next_outer_script()
        if next_outer is not None:
            return next_outer

        element = self.all_childs_in_taget_hash()[0]  # TODO: may be not quick enough

        source = element.namespaceURI
        available_chains = self._available_chains([source], self.state.opts.targetNamespaces)

        first_edges = []
        edges = available_chains.first_edges_for_shortest_path(self, frozenset([source]), self.state.opts.targetNamespaces)
        first_edges.extend(edges)
        if not first_edges:
            raise StopIteration

        first_edges = self._checked_scripts(first_edges)

        maximal_priority_edges = self._choose_by_preservance_priority(first_edges)
        if not maximal_priority_edges:
            raise StopIteration
        return maximal_priority_edges[0][0]  # TODO: Add it to the list of executed scripts