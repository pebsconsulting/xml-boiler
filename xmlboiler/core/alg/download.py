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
import itertools
from dataclasses import dataclass, field
from typing import Any

from xmlboiler.core.options import RecursiveRetrievalPriorityOrderElement


# https://softwareengineering.stackexchange.com/questions/358931/breadth-first-traversal-with-some-edges-preferred/358937#358937

from xmlboiler.core.rdf_format import asset_parser


def _enumerate_xml_namespaces(state):
    stack = [state.xml.documentElement]
    while stack:
        v = stack.pop()
        for w in v.childNodes:
            yield w.namespaceURI
            stack.append(w)

@dataclass(order=True)
class PrioritizedNS:
    priority: int
    ns: Any=field(compare=False)


# Return a pair (priority, namespace)
def _enumerate_child_namespaces(state, asset):
    priority = 0
    yield from [PrioritizedNS(priority, ns) for ns in _enumerate_xml_namespaces(state)]
    for order_part in state.opts.recursiveOptions:
        priority += 1
        if order_part == RecursiveRetrievalPriorityOrderElement.SOURCES:
            for t in asset.transformers:
                for s in t.source_namespaces:
                    yield PrioritizedNS(priority, s)
        elif order_part == RecursiveRetrievalPriorityOrderElement.TARGETS:
            for t in asset.transformers:
                for s in t.target_namespaces:
                    yield PrioritizedNS(priority, s)
        elif order_part == RecursiveRetrievalPriorityOrderElement.WORKFLOW_TARGETS:
            # TODO: It may happen atmost once, may optimize not to run it again
            yield from [PrioritizedNS(priority, ns) for ns in state.opts.targetNamespaces]


def _enumerate_child_namespaces_without_priority(state, asset):
    return [x.ns for x in _enumerate_child_namespaces(state, asset)]


class DepthFirstDownloader(object):
    def __init__(self, parse_content, subclasses, state):
        self.parse_content = parse_content
        self.subclasses = subclasses
        self.state = state

    # Recursive algorithm for simplicity.
    # Every yield produces a list of assets (not individual assets),
    # because in our_depth_first_based_download() we need to discard multiple assets.
    def depth_first_download(self, ns, downloaders):
        if ns in self.state.assets:
            return
        self.state.assets.add(ns)
        parser = asset_parser.AssetParser(self.parse_content, self.subclasses)
        assets = []
        for graph in [downloader(ns) for downloader in downloaders]:
            asset_info = parser.parse(graph)
            self.state.add_asset(asset_info)
            assets.append(asset_info)
        yield assets
        for ns2 in _enumerate_child_namespaces_without_priority(self.state, ns):
            # if ns2 not in self.state.assets: # checked above
            self.depth_first_download(ns2, downloaders)  # recursion

    # Every yield produces a list of assets (not individual assets),
    # because in our_depth_first_based_download() we need to discard multiple assets.
    def _our_depth_first_based_download(self):
        for downloaders in self.state.opts.downloaders:
            for assets in self.state.opts.initial_assets:
                yield assets
            for asset in self.state.opts.initial_assets:
                try:
                    iter = self.depth_first_download(asset, downloaders)
                    next(iter)  # do not repeat the above
                    yield from iter
                except StopIteration:
                    pass

    # Merge list of lists (in fact, iterators) into one list
    def our_depth_first_based_download(self):
        return itertools.chain.from_iterable(self._our_depth_first_based_download())