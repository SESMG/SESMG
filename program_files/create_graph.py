import pydot
import os
from graphviz import Digraph


def create_graph(filepath, nodes_data, legend=False):
    """Visualizes the energy system as graph.

    Creates, using the library Graphviz, a graph containing all components
    and connections from "nodes_data" and returns this as a PNG file.

    ----

    Keyword arguments:

        filepath : obj:'str'
          -- path, where the PNG-result shall be saved

        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file.

        legend : obj:'bool'
          -- specifies, whether a legend will be added to the graph or not

    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.04.2020
    """


    def linebreaks(text):
        """Adds linebreaks a given string.

         Function which adds a line break to strings every ten characters.
         Up to four strings are added.

         ----

        Keyword arguments:

            text : obj:'str'
              -- string to which line breaks will be added

        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 14.04.2020

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

    # Defines the location of Graphviz as path
    os.environ["PATH"] += os.pathsep + 'C:\\Program Files (x86)\\Graphviz2.38\\bin'

    filepath = filepath
    nd = nodes_data

    # Creates the Directed-Graph
    dot = Digraph(format='png')

    # #Creates a Legend if Legend = True
    if legend:
        dot.node('Bus', shape='ellipse', fontsize="10", fixedsize='shape', width='1.1', height='0.6')
        dot.node('Source', shape='trapezium', fontsize="10", fixedsize='shape', width='1.1', height='0.6')
        dot.node('Sink', shape='invtrapezium', fontsize="10", fixedsize='shape', width='1.1', height='0.6')
        dot.node('Transformer\n Links', shape='box', fontsize="10", fixedsize='shape', width='1.1', height='0.6')
        dot.node('Storage', shape='box', fontsize="10", fixedsize='shape', width='1.1', height='0.6', style='dashed')

    # Implements shortage-sources and excess-sinks and their connected buses in the graph
    for i, b in nd['buses'].iterrows():
        if b['active']:

            # Implements shortage sources
            if b['shortage']:

                # adds "_shortage" to the label
                shortage = b['label'] + '_shortage'
                # Linebreaks, so that the labels fit the boxes
                shortage = linebreaks(shortage)

                # Adds nodes to the graph
                dot.node(shortage, shape='trapezium', fontsize="10", fixedsize='shape', width='1.1', height='0.6')
                dot.node(b['label'], shape='ellipse', fontsize="10")

                # Adds edge to the graph
                dot.edge(shortage, b['label'])

            # Implements excess sinks
            if b['excess']:

                # adds "_shortage" to the label
                excess = b['label'] + '_excess'
                # Linebreaks, so that the labels fit the boxes
                excess = linebreaks(excess)

                # Adds nodes to the graph
                dot.node(excess, shape='invtrapezium', fontsize="10", fixedsize='shape', width='1.1', height='0.6')
                dot.node(b['label'], shape='ellipse', fontsize="10")

                # Adds edge to the graph
                dot.edge(b['label'], excess)

    # Implements sources and their connected buses in the graph
    for i, so in nd['sources'].iterrows():
        if so['active']:

            # Linebreaks, so that the labels fit the boxes
            so['label'] = linebreaks(so['label'])

            # Adds nodes to the graph
            dot.node(so['label'], shape='trapezium', fontsize="10", fixedsize='shape', width='1.1', height='0.6')
            dot.node(so['output'], shape='ellipse', fontsize="10")

            # Adds edge to the graph
            dot.edge(so['label'], so['output'])

    # Implements sinks and their connected buses in the graph
    for i, de in nd['demand'].iterrows():
        if de['active']:

            # Linebreaks, so that the labels fit the boxes
            de['label'] = linebreaks(de['label'])

            dot.node(de['label'], shape='invtrapezium', fontsize="10", fixedsize='shape', width='1.1', height='0.6')
            dot.node(de['input'], shape='ellipse', fontsize="10")
            dot.edge(de['input'], de['label'])

    # Implements transformers and their connected buses in the graph
    for i, t in nd['transformers'].iterrows():
        if t['active']:

            # Linebreaks, so that the labels fit the boxes
            t['label'] = linebreaks(t['label'])

            # Adds nodes to the graph
            dot.node(t['label'], shape='box', fontsize="10", fixedsize='shape', width='1.1', height='0.6')
            dot.node(t['input'], shape='ellipse', fontsize="10")
            dot.node(t['output'], shape='ellipse', fontsize="10")

            # Adds edges to the graph
            dot.edge(t['input'], t['label'])
            dot.edge(t['label'], t['output'])

            # Adds a second output (node and edge), if the transformer has two outputs
            if t['output2'] != "None":
                dot.node(t['output2'], shape='ellipse', fontsize="10")
                dot.edge(t['label'], t['output2'])
                



            if t['transformer type'] == "HeatPump":

                # adds "_low_temp_source" to the label
                low_temp_source = t['label']+'_low_temp_source'
                # Linebreaks, so that the labels fit the boxes
                low_temp_source = linebreaks(low_temp_source)

                # Adds a second input and a heat source (node and edge) for heat pumps
                dot.node(t['label'] + '_low_temp_bus', shape='ellipse', fontsize="10")
                dot.edge(t['label'] + '_low_temp_bus', t['label'])
                dot.node(low_temp_source, shape='trapezium', fontsize="10",
                         fixedsize='shape', width='1.1', height='0.6')
                dot.edge(low_temp_source, t['label'] + '_low_temp_bus')

    # Implements storages and their connected buses in the graph
    for i, s in nd['storages'].iterrows():
        if s['active']:

            # Linebreaks, so that the labels fit the boxes
            s['label'] = linebreaks(s['label'])

            # Adds nodes to the graph
            dot.node(s['label'], shape='box', style='dashed', fontsize="10", fixedsize='shape', width='1.1', height='0.6')
            dot.node(s['bus'], shape='ellipse', fontsize="10")

            # Adds edges to the graph
            dot.edge(s['bus'], s['label'])
            dot.edge(s['label'], s['bus'])

    # Implements links and their connected buses in the graph
    for i, p in nd['links'].iterrows():
        if p['active']:

            # Linebreaks, so that the labels fit the boxes
            p['label'] = linebreaks(p['label'])

            # Adds nodes to the graph
            dot.node(p['label'], shape='box', fontsize="10", fixedsize='shape', width='1.1', height='0.6')
            dot.node(p['bus_1'], shape='ellipse', fontsize="10")
            dot.node(p['bus_2'], shape='ellipse')

            # Adds edges to the graph
            dot.edge(p['bus_1'], p['label'])
            dot.edge(p['label'], p['bus_2'])

            # Adds a second edge direction, if the link is an undirected link
            if p['(un)directed'] == 'undirected':
                dot.edge(p['bus_2'], p['label'])
                dot.edge(p['label'], p['bus_1'])

    dot.render(filepath+'/graph.gv', view=True)



