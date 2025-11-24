from graphviz import Digraph

# Create a new directed graph
dot = Digraph(comment='My NFA')

# Define states (nodes)
# 'shape=doublecircle' for final states
dot.node('q0', 'q0', shape='circle')
dot.node('q1', 'q1', shape='doublecircle')

# Define transitions (edges)
# 'label' for the input symbol
dot.edge('q0', 'q0', label='a')
dot.edge('q0', 'q1', label='b')
dot.edge('q1', 'q1', label='a, b')

# Add an invisible node and edge for the start state arrow
dot.attr('node', shape='none')
dot.node('start', '')
dot.edge('start', 'q0', label='')


# Render the graph to a file (e.g., NFA.pdf)
dot.render('NFA', view=True)