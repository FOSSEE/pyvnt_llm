from pyvnt import *

# Create the root node: fvSolution
fv_solution_root = Node_C("fvSolution", None, None)

# Create the 'solvers' node
solvers_node = Node_C("solvers", fv_solution_root, None)

# Define properties for p solver
p_solver = Key_C('solver', Enm_P('solver', items={'PCG', 'PBiCG', 'PBiCGStab', 'smoothSolver', 'diagonal'}, default='PBiCGStab'))
p_preconditioner = Key_C('preconditioner', Enm_P('preconditioner', items={'DIC', 'DILU', 'FDIC'}, default='DILU'))
p_tolerance = Key_C('tolerance', Flt_P('tolerance', minimum=0, maximum=1, default=1e-06))
p_relTol = Key_C('relTol', Flt_P('relTol', minimum=0, maximum=1, default=0.01))

# Create the 'p' node
p_node = Node_C("p", solvers_node, None, p_solver, p_preconditioner, p_tolerance, p_relTol)

# Define properties for pFinal solver
pFinal_relTol = Key_C('relTol', Flt_P('relTol', minimum=0, maximum=1, default=0))

# Create the 'pFinal' node
pFinal_node = Node_C("pFinal", solvers_node, None, pFinal_relTol)

# Define properties for pcorr.* solver
pcorr_solver = Key_C('solver', Enm_P('solver', items={'PCG', 'PBiCG', 'PBiCGStab', 'smoothSolver', 'diagonal'}, default='PCG'))
pcorr_preconditioner = Key_C('preconditioner', Enm_P('preconditioner', items={'DIC', 'DILU', 'FDIC'}, default='DIC'))
pcorr_tolerance = Key_C('tolerance', Flt_P('tolerance', minimum=0, maximum=1, default=1e-02))
pcorr_relTol = Key_C('relTol', Flt_P('relTol', minimum=0, maximum=1, default=0))

# Create the 'pcorr.*' node
pcorr_node = Node_C("pcorr.*", solvers_node, None, pcorr_solver, pcorr_preconditioner, pcorr_tolerance, pcorr_relTol)

# Define properties for rho.* solver
rho_solver = Key_C('solver', Enm_P('solver', items={'PCG', 'PBiCG', 'PBiCGStab', 'smoothSolver', 'diagonal'}, default='diagonal'))
rho_tolerance = Key_C('tolerance', Flt_P('tolerance', minimum=0, maximum=1, default=1e-05))
rho_relTol = Key_C('relTol', Flt_P('relTol', minimum=0, maximum=1, default=0))

# Create the 'rho.*' node
rho_node = Node_C("rho.*", solvers_node, None, rho_solver, rho_tolerance, rho_relTol)

# Define properties for (U|h|e|R|k|epsilon|omega) solver
uh_solver = Key_C('solver', Enm_P('solver', items={'PCG', 'PBiCG', 'PBiCGStab', 'smoothSolver', 'diagonal'}, default='smoothSolver'))
uh_smoother = Key_C('smoother', Enm_P('smoother', items={'symGaussSeidel', 'gaussSeidel'}, default='symGaussSeidel'))
uh_tolerance = Key_C('tolerance', Flt_P('tolerance', minimum=0, maximum=1, default=1e-05))
uh_relTol = Key_C('relTol', Flt_P('relTol', minimum=0, maximum=1, default=0.1))

# Create the '(U|h|e|R|k|epsilon|omega)' node
uh_node = Node_C("(U|h|e|R|k|epsilon|omega)", solvers_node, None, uh_solver, uh_smoother, uh_tolerance, uh_relTol)

# Define properties for (U|h|e|R|k|epsilon|omega)Final solver
uhFinal_relTol = Key_C('relTol', Flt_P('relTol', minimum=0, maximum=1, default=0))

# Create the '(U|h|e|R|k|epsilon|omega)Final' node
uhFinal_node = Node_C("(U|h|e|R|k|epsilon|omega)Final", solvers_node, None, uhFinal_relTol)

# Define properties for cellMotionUx.* solver
cellMotionUx_solver = Key_C('solver', Enm_P('solver', items={'PCG', 'PBiCG', 'PBiCGStab', 'smoothSolver', 'diagonal'}, default='PCG'))
cellMotionUx_preconditioner = Key_C('preconditioner', Enm_P('preconditioner', items={'DIC', 'DILU', 'FDIC'}, default='DIC'))
cellMotionUx_tolerance = Key_C('tolerance', Flt_P('tolerance', minimum=0, maximum=1, default=1e-08))
cellMotionUx_relTol = Key_C('relTol', Flt_P('relTol', minimum=0, maximum=1, default=0))

# Create the 'cellMotionUx.*' node
cellMotionUx_node = Node_C("cellMotionUx.*", solvers_node, None, cellMotionUx_solver, cellMotionUx_preconditioner, cellMotionUx_tolerance, cellMotionUx_relTol)

# Create the PIMPLE node
pimple_node = Node_C("PIMPLE", fv_solution_root, None)

# Define properties for PIMPLE
momentumPredictor = Key_C('momentumPredictor', Enm_P('momentumPredictor', items={'yes', 'no'}, default='yes'))
correctPhi = Key_C('correctPhi', Enm_P('correctPhi', items={'yes', 'no'}, default='yes'))
nOuterCorrectors = Key_C('nOuterCorrectors', Int_P('nOuterCorrectors', minimum=0, maximum=100, default=1))
nCorrectors = Key_C('nCorrectors', Int_P('nCorrectors', minimum=0, maximum=100, default=2))
transonic = Key_C('transonic', Enm_P('transonic', items={'yes', 'no'}, default='yes'))
nNonOrthogonalCorrectors = Key_C('nNonOrthogonalCorrectors', Int_P('nNonOrthogonalCorrectors', minimum=0, maximum=100, default=0))
rhoMin = Key_C('rhoMin', Flt_P('rhoMin', minimum=0, maximum=100, default=0.1))
rhoMax = Key_C('rhoMax', Flt_P('rhoMax', minimum=0, maximum=100, default=100.0))

# Add properties to the PIMPLE node
pimple_node.add_data(momentumPredictor)
pimple_node.add_data(correctPhi)
pimple_node.add_data(nOuterCorrectors)
pimple_node.add_data(nCorrectors)
pimple_node.add_data(transonic)
pimple_node.add_data(nNonOrthogonalCorrectors)
pimple_node.add_data(rhoMin)
pimple_node.add_data(rhoMax)

# Create the relaxationFactors node
relaxationFactors_node = Node_C("relaxationFactors", fv_solution_root, None)

# Create the equations node under relaxationFactors
equations_node = Node_C("equations", relaxationFactors_node, None)

# Define properties for equations
equations_all = Key_C('.*', Flt_P('.*', minimum=0, maximum=1, default=1))

# Add properties to the equations node
equations_node.add_data(equations_all)

# Display the tree
show_tree(fv_solution_root)