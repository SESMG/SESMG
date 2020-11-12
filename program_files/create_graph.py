from graphviz import Digraph
import os


def create_graph(filepath, nodes_data, legend=False):
    """Visualizes the energy system as graph.

    Creates, using the library Graphviz, a graph containing all
    components and connections from "nodes_data" and returns this as a
    PNG file.

    ----

    Keyword arguments:

        filepath : obj:'str'
          -- path, where the PNG-result shall be saved

        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file.

        legend : obj:'bool'
          -- specifies, whether a legend will be added to the graph or
             not

    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.04.2020
    """
    
    def linebreaks(text):
        """Adds linebreaks a given string.

         Function which adds a line break to strings every ten
         characters. Up to four strings are added.

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
    
    # Defines the location of Graphviz as path necessary for windows
    os.environ["PATH"] += \
        os.pathsep + 'C:\\Program Files (x86)\\Graphviz2.38\\bin'
    # Creates the Directed-Graph
    dot = Digraph(format='png')
    # Creates a Legend if Legend = True
    if legend:
        component = ['Bus', 'Source', 'Sink', 'Transformer\nLinks', 'Storage']
        shape = {'Bus': ['ellipse'], 'Source': ['trapezium'],
                 'Sink': ['invtrapezium'], 'Transformer\nLinks': ['box'],
                 'Storage': ['box']}
        for i in component:
            dot.node(i, shape=shape[i][0], fontsize="10", fixedsize='shape',
                     width='1.1', height='0.6',
                     style='dashed' if i == 'Storage' else '')
    components = ["buses", "sources", "demand", "transformers", "storages",
                  "links"]
    shapes = {'sources': ['trapezium'], 'demand': ['invtrapezium'],
              'transformers': ['box'], 'storages': ['box'],
              'links': ['box']}
    bus = {'buses': ['label'], 'sources': ['output'], 'demand': ['input'],
           'transformers': ['input'], 'storages': ['bus'], 'links': ['bus_1']}
    for i in components:
        for j, b in nodes_data[i].iterrows():
            if b['active']:
                # sets component label
                label = b['label']
                if i == 'buses':
                    if b['shortage']:
                        label = b['label'] + '_shortage'
                    elif b['excess']:
                        label = b['label'] + '_excess'
                label = linebreaks(label)
                if i != 'buses':
                    dot.node(label, shape=shapes[i][0], fontsize="10",
                             fixedsize='shape', width='1.1', height='0.6',
                             style='dashed' if i == 'storages' else '')
                else:
                    if b['shortage']:
                        dot.node(label, shape='trapezium', fontsize="10",
                                 fixedsize='shape', width='1.1', height='0.6')
                    if b['excess']:
                        dot.node(label, shape='invtrapezium', fontsize="10",
                                 fixedsize='shape', width='1.1', height='0.6')
                # creates bus nodes
                dot.node(b[bus[i][0]], shape='ellipse', fontsize="10")
                if i == 'links':
                    dot.node(b['bus_2'], shape='ellipse')
                # creates edges
                if i == 'demand' or i == 'storages' or i == 'links' \
                        or (i == 'buses' and b['excess']):
                    dot.edge(b[bus[i][0]], label)
                if i == 'sources' or i == 'storages' \
                        or (i == 'buses' and b['shortage']):
                    dot.edge(label, b[bus[i][0]])
                if i == 'links':
                    dot.edge(label, b['bus_2'])
                    if b['(un)directed'] == 'undirected':
                        dot.edge(b['bus_2'], label)
                        dot.edge(label, b['bus_1'])
                elif i == 'transformers':
                    dot.node(b['output'], shape='ellipse', fontsize="10")
                    dot.edge(b[bus[i][0]], label)
                    dot.edge(label, b['output'])
                    if b['output2'] != "None":
                        dot.node(b['output2'], shape='ellipse', fontsize="10")
                        dot.edge(label, b['output2'])
                    if b['transformer type'] == "HeatPump":
                        # adds "_low_temp_source" to the label
                        low_temp_source = label + '_low_temp_source'
                        # Linebreaks, so that the labels fit the boxes
                        low_temp_source = linebreaks(low_temp_source)
                        # Adds a second input and a heat source (node and edge)
                        # for heat pumps
                        dot.node(label + '_low_temp_bus',
                                 shape='ellipse',
                                 fontsize="10")
                        dot.edge(label + '_low_temp_bus', label)
                        dot.node(low_temp_source, shape='trapezium',
                                 fontsize="10",
                                 fixedsize='shape', width='1.1', height='0.6')
                        dot.edge(low_temp_source,
                                 label + '_low_temp_bus')
    dot.render(filepath + '/graph.gv', view=True)
