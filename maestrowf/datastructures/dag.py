###############################################################################
# Copyright (c) 2017, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory
# Written by Francesco Di Natale, dinatale3@llnl.gov.
#
# LLNL-CODE-734340
# All rights reserved.
# This file is part of MaestroWF, Version: 1.0.0.
#
# For details, see https://github.com/LLNL/maestrowf.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################

"""Module that contains the implemenation of a Directed-Acyclic Graph."""

from collections import deque, OrderedDict
import logging

from ..abstracts import Graph

logger = logging.getLogger(__name__)


class DAG(Graph):
    """
    A directed acyclic graph (DAG) data structure.

    The implementation of this DAG uses an adjacency map with a map to
    index the values (or objects) at each node.
    """

    def __init__(self):
        """Initialize the DAG data structure internals."""
        self.adjacency_table = OrderedDict()
        self.values = OrderedDict()

    def add_node(self, name, obj):
        """
        Add node 'name' to the DAG.

        :param name: String identifier of the node.
        :param obj: An object representing the value of the node.
        """
        logging.debug("Adding %s...", name)
        if name in self.values:
            logger.warning("Node %s already exists. Returning.",
                           name)
            return

        logger.debug("Node %s added. Value is of type %s.", name, type(obj))
        self.values[name] = obj
        self.adjacency_table[name] = []

    def add_edge(self, src, dest):
        """
        Add an edge to the DAG if edge (src, dest) is a valid edge.

        :param src: Source vertex name.
        :param dest: Destination vertex name.
        """
        # Disallow loops to the same node.
        if src == dest:
            msg = "Cannot add self referring cycle edge ({}, {})" \
                  .format(src, dest)
            logger.error(msg)

            return

        # Disallow adding edges to the graph before nodes are added.
        error = "Attempted to create edge ({src}, {dest}), but node {node}" \
                " does not exist."
        if src not in self.adjacency_table:
            error = error.format(src=src, dest=dest, node=src)
            logger.error(error)
            raise ValueError(error)

        if dest not in self.adjacency_table:
            logger.error(error, src, dest, dest)
            return

        # If the edge would create a loop, don't add the edge.
        if src in self.adjacency_table[dest]:
            error = error.format(src=src, dest=dest, node=dest)
            logger.error(error)
            raise ValueError(error)

        # If dest is not already and edge from src, add it.
        if dest not in self.adjacency_table[src]:
            self.adjacency_table[src].append(dest)
            logging.info("Edge (%s, %s) added.", src, dest)
            return

        # Otherwise, we already have the edge.
        logging.info("Edge (%s, %s) already in DAG.", src, dest)

    def remove_edge(self, src, dest):
        """
        Remove edge (src, dest) from the DAG.

        :param src: Source vertex name.
        :param dest: Destination vertex name.
        """
        if src not in self.adjacency_table:
            logger.warning("Attempted to remove an edge (%s, %s), but %s"
                           " does not exist.", src, dest, src)
            return

        if dest not in self.adjacency_table:
            logger.warning("Attempted to remove an edge from (%s, %s), but %s"
                           " does not exist.", src, dest, dest)
            return

        logging.debug("Removing edge (%s, %s).", src, dest)
        self.adjacency_table[src].remove(dest)

    def dfs_subtree(self, src, par=None):
        """
        Create a subtree of the DAG starting at src in DFS order.

        :param src: Source node name to begin search.
        :param par: Name of parent node to the specified source node.
        :returns: A list representing the path taken by DFS.
        :returns: A dictionary containing a mapping from node to parent node.
        """
        path = [src]
        parent = {src: par}
        for node in self.adjacency_table[src]:
            parent[node] = src
            subpath, children = self.dfs_subtree(node, src)
            path = path + subpath
            parent.update(children)

        return path, parent

    def bfs_subtree(self, src):
        """
        Create a subtree of the DAG starting at src in BFS order.

        :param src: Source node name to begin search.
        :returns: A list representing the path taken by BFS.
        :returns: A dictionary containing a mapping from node to parent node.
        """
        queue = deque([src])
        path = [src]
        parent = {src: None}

        while queue:
            root = queue.popleft()
            for node in self.adjacency_table[root]:
                if node in path:
                    continue

                queue.append(node)
                parent[node] = root
                path.append(node)

        return path, parent
