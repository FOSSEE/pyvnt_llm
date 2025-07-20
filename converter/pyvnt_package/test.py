from converter import read
from pyvnt import show_tree

tree_node = read('/opt/openfoam11/tutorials/solidDisplacement/beamEndLoad/system/fvSolution')

show_tree(tree_node)