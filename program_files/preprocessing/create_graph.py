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
                self.add_comp(str(nd.label), "ellipse", False, self.dot)
                # keep the bus reference for drawing edges later
                self.busses.append(nd)
            elif isinstance(nd, Bus) and "infrastructure" in nd.label:
                pass
            elif isinstance(nd, HeatPipeline):
                if "dh-network" not in str(self.dot):
                    self.dot.node("dh-network", "dh-network", shape="hexagon")
            else:
                self.add_comp(
                    str(nd.label),
                    switch_dict.get(str(type(nd)), "Invalid component")[0],
                    switch_dict.get(str(type(nd)), "Invalid component")[1],
                    self.dot,
                )
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
        subgraph.node(
            linebreaks(label),
            shape=shape,
            fontsize="10",
            fixedsize="shape",
            width="1.1",
            height="0.7",
            style="dashed" if dashed else "",
        )

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
        if isinstance(b, HeatPipeline):
            self.dot.edge(a_label, "dh-network")
        elif isinstance(a, HeatPipeline):
            self.dot.edge("dh-network", b_label)
        elif isinstance(a, HeatPipeline) and isinstance(b, HeatPipeline):
            pass
        else:
            self.dot.edge(a_label, b_label)

    def render(self, filepath, show):
        """Call the render method of the DiGraph instance"""
        self.dot.render(filepath + "/graph.gv", view=show)
