# -*- coding: utf-8 -*-

"""Module to render an oemof energy model network in a graph.
SPDX-FileCopyrightText: Pierre-Francois Duc <pierre-francois.duc@rl-institut.de>
SPDX-FileCopyrightText: Uwe Krien <krien@uni-bremen.de>
SPDX-FileCopyrightText: Patrik Schönfeldt
SPDX-License-Identifier: MIT
"""

import logging
import os
import graphviz
from oemof.solph import Bus
from oemof.solph.components import Sink, Source, Converter, GenericStorage
from dhnx.optimization.oemof_heatpipe import HeatPipeline


def linebreaks(text: str):
    """
    Adds linebreaks a given string.

    Function which adds a line break to strings every ten
    characters. Up to four strings are added.

    :param text: string to which line breaks will be added
    :type text: str

    Christian Klemm - christian.klemm@fh-muenster.de
    """
    text_length = len(text)
    if text_length > 10:
        text = str(text[0:9] + "-\n" + text[9:])
    if text_length > 20:
        text = str(text[0:21] + "-\n" + text[21:])
    if text_length > 30:
        text = str(text[0:33] + "-\n" + text[33:])
    if text_length > 40:
        text = str(text[0:45] + "-\n" + text[45:])
    return text


class ESGraphRenderer:
    def __init__(
        self, energy_system=None, filepath=None, legend=False, view=False
    ) -> None:
        """
            Render an oemof energy system using graphviz.
            
            developed by the oemof group adopted for SESMG
            original repository: https://github.com/oemof/oemof-visio
        
            :param energy_system: The oemof energy system
            :type energy_system: oemof.solph.network.EnergySystem
            :param filepath: path where the created files will be saved
            :type filepath: str
            :param legend: specify, whether a legend will be added to \
                the graph or not
            :type legend: bool
        """
        self.busses = []

        os.environ["PATH"] += os.pathsep + "C:\\Program Files (x86)\\Graphviz2.38\\bin"
        self.dot = graphviz.Digraph(format="png")
        self._nodes_added = set()
        self._edges_added = set()
        self._edge_pairs_added = set()

        if legend is True:
            with self.dot.subgraph(name="cluster_1") as self.c:
                # color of the legend box
                self.c.attr(color="black")
                # title of the legend box
                self.c.attr(label="Legends")
                self.add_comp("Bus", "ellipse", False, self.c)
                self.add_comp("Sink", "invtrapezium", False, self.c)
                self.add_comp("Source", "trapezium", False, self.c)
                self.add_comp("Transformer", "rectangle", False, self.c)
                self.add_comp("Storage", "rectangle", True, self.c)

        switch_dict = {
            "<class 'oemof.solph.components._sink.Sink'>": ["invtrapezium",
                                                            False],
            "<class 'oemof.solph.components._source.Source'>": ["trapezium",
                                                                False],
            "<class 'oemof.solph.components._converter.Converter'>": [
                "rectangle", False],
            "<class 'oemof.solph.components._generic_storage.GenericStorage'>": [
                "rectangle", True],
            "<class 'oemof.solph.components._link.Link'>": [
                "rectangle", False],
        }
        # draw a node for each of the energy_system's component.
        # the shape depends on the component's type.
        for nd in energy_system.nodes:
            # make sur the label is a string and not a tuple
            if isinstance(nd, Bus) and not "infrastructure" in nd.label:
                _lbl = str(nd.label).lower()
                if _lbl in {'dh-network', 'dh-network-exergy', 'dh-network-anergy'}:
                    continue
                else:
                    self.add_comp(str(nd.label), 'ellipse', False, self.dot)
                self.busses.append(nd)
            elif isinstance(nd, Bus) and "infrastructure" in nd.label:
                pass
            elif isinstance(nd, HeatPipeline):
                continue
            else:
                self.add_comp(
                    str(nd.label),
                    switch_dict.get(str(type(nd)), "Invalid component")[0],
                    switch_dict.get(str(type(nd)), "Invalid component")[1],
                    self.dot,
                )
        # Searching Pipelines with label containing 'exergy' or 'anergy'
        exergy_present = any(
            isinstance(nd, HeatPipeline) and 'exergy' in str(nd.label).lower()
            for nd in energy_system.nodes
        )
        anergy_present = any(
            isinstance(nd, HeatPipeline) and 'anergy' in str(nd.label).lower()
            for nd in energy_system.nodes
        )
        heatpipe_present = any(
            isinstance(nd, HeatPipeline)
            for nd in energy_system.nodes
        )
        
        if exergy_present and anergy_present:
            net_labels = ['dh-network-exergy', 'dh-network-anergy']

        elif exergy_present:
            net_labels = ['dh-network-exergy']
        elif anergy_present:
            net_labels = ['dh-network-anergy']
        elif heatpipe_present:
            # Generic case for heat pipelines
            net_labels = ['dh-network']
        else:
            net_labels = []
        # Create heat-network node(s) as needed
        for net in net_labels:
            if net not in self._nodes_added:
                self.dot.node(net, linebreaks(net), shape='hexagon')
                self._nodes_added.add(net)

        # draw the edges between the nodes based on each bus inputs/outputs
        for bus in self.busses:
            for component in bus.inputs:
                # draw an arrow from the component to the bus
                self.connect(component, bus)
            for component in bus.outputs:
                # draw an arrow from the bus to the component
                self.connect(bus, component)

        self.render(filepath, view)

    def add_comp(self, label, shape, dashed, subgraph):
        label_str = str(label)
        if label_str in self._nodes_added:
            return
        subgraph.node(
            linebreaks(label),
            shape=shape,
            fontsize="10",
            fixedsize="shape",
            width="1.1",
            height="0.7",
            style="dashed" if dashed else "",
        )
        self._nodes_added.add(label_str)

    def connect(self, a, b):
        """Draw an arrow from node a to node b

        Parameters
        ----------
        a: `oemof.solph.network.Node`
            An oemof node (usually a Bus or a Component)

        b: `oemof.solph.network.Node`
            An oemof node (usually a Bus or a Component)
        """
        a_label = linebreaks(str(a.label))
        b_label = linebreaks(str(b.label))
        
        # If one is a Heatpipeline, we connect it to the network
        if isinstance(a, HeatPipeline) or isinstance(b, HeatPipeline):
            
            if not hasattr(self, '_edges_added'):
                self._edges_added = set()
            if not hasattr(self, '_edge_pairs_added'):
                self._edge_pairs_added = set()
            if not hasattr(self, '_nodes_added'):
                self._nodes_added = set()

            pipeline = b if isinstance(b, HeatPipeline) else a
            plc_label = str(pipeline.label).lower()
            if 'exergy' in plc_label:
                net = 'dh-network-exergy'
            elif 'anergy' in plc_label:
                net = 'dh-network-anergy'
            else:
                net = 'dh-network'
            
            if isinstance(b, HeatPipeline):
                # BUS → NET
                pair_key = frozenset({a_label, net})
                if pair_key not in self._edge_pairs_added:
                    self._edge_pairs_added.add(pair_key)
                    if (a_label, net) not in self._edges_added:
                        self.dot.edge(a_label, net)
                        self._edges_added.add((a_label, net))
            else:
                # NET → BUS
                pair_key = frozenset({net, b_label})
                if pair_key not in self._edge_pairs_added:
                    self._edge_pairs_added.add(pair_key)
                    if (net, b_label) not in self._edges_added:
                        self.dot.edge(net, b_label)
                        self._edges_added.add((net, b_label))
            return
        
        # If both are not Heatpipelines, we connect them normally
        elif not (isinstance(a, HeatPipeline) and isinstance(b, HeatPipeline)):
            if (a_label, b_label) not in self._edges_added:
                self.dot.edge(a_label, b_label)
                self._edges_added.add((a_label, b_label))

    def render(self, filepath, show):
        """Call the render method of the DiGraph instance"""
        self.dot.render(filepath + "/graph.gv", view=show)
