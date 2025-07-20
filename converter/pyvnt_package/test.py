from converter import read
from pyvnt import show_tree

tree_node = read('/workspaces/pyvnt_llm/converter/pyvnt_package/fvSolution.txt')

show_tree(tree_node)