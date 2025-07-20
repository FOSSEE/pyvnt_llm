from pyvnt import *

# Create the root node: fvSolution
root = Node_C('fvSolution', None, None)

# Create the 'solvers' node
solvers_node = Node_C('solvers', root, None)

# Create Key_C objects for 'p' solver
p_solver = Key_C('solver', Enm_P('val1', items={'GAMG', 'PCG', 'PBiCGStab', 'smoothSolver'}, default='GAMG'))
p_tolerance = Key_C('tolerance', Flt_P('val1', minimum=0, maximum=1, default=1e-06))
p_relTol = Key_C('relTol', Flt_P('val1', minimum=0, maximum=1, default=0.1))
p_smoother = Key_C('smoother', Enm_P('val1', items={'GaussSeidel', 'symGaussSeidel'}, default='GaussSeidel'))

# Create the 'p' node and add the Key_C objects
p_node = Node_C('p', solvers_node, None, p_solver, p_tolerance, p_relTol, p_smoother)

# Create Key_C objects for 'pFinal' solver
pFinal_tolerance = Key_C('tolerance', Flt_P('val1', minimum=0, maximum=1, default=1e-06))
pFinal_relTol = Key_C('relTol', Flt_P('val1', minimum=0, maximum=1, default=0))

# Create the 'pFinal' node and add the Key_C objects
pFinal_node = Node_C('pFinal', solvers_node, None, pFinal_tolerance, pFinal_relTol)

# Create Key_C objects for the generic solver
generic_solver = Key_C('solver', Enm_P('val1', items={'GAMG', 'PCG', 'PBiCGStab', 'smoothSolver'}, default='smoothSolver'))
generic_smoother = Key_C('smoother', Enm_P('val1', items={'GaussSeidel', 'symGaussSeidel'}, default='GaussSeidel'))
generic_tolerance = Key_C('tolerance', Flt_P('val1', minimum=0, maximum=1, default=1e-05))
generic_relTol = Key_C('relTol', Flt_P('val1', minimum=0, maximum=1, default=0))

# Create the generic solver node and add the Key_C objects
generic_node = Node_C('"(U|k|epsilon|omega|R|nuTilda).*"', solvers_node, None, generic_solver, generic_smoother, generic_tolerance, generic_relTol)

# Create the 'PIMPLE' node
PIMPLE_node = Node_C('PIMPLE', root, None)

# Create Key_C objects for PIMPLE
nCorrectors = Key_C('nCorrectors', Int_P('int_prop_1', minimum=0, maximum=10, default=2))
nNonOrthogonalCorrectors = Key_C('nNonOrthogonalCorrectors', Int_P('int_prop_2', minimum=0, maximum=10, default=0))
pRefCell = Key_C('pRefCell', Int_P('int_prop_3', minimum=0, maximum=10000, default=0))
pRefValue = Key_C('pRefValue', Flt_P('float_prop_1', minimum=-1e10, maximum=1e10, default=0))

# Add Key_C objects to the PIMPLE node
PIMPLE_node.add_data(nCorrectors)
PIMPLE_node.add_data(nNonOrthogonalCorrectors)
PIMPLE_node.add_data(pRefCell)
PIMPLE_node.add_data(pRefValue)

# Display the tree structure
show_tree(root)