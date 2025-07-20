from pyvnt import *

# Create the root node
root = Node_C('fvSchemes', None, None)

# FoamFile node
foamFile_data = [
    Str_P('format', default='ascii'),
    Str_P('class', default='dictionary'),
    Str_P('location', default='"system"'),
    Str_P('object', default='fvSchemes')
]
foamFile = Node_C('FoamFile', root, None, *[Key_C('FoamFile', *foamFile_data)])

# ddtSchemes node
ddtSchemes_data = [
    Str_P('default', default='steadyState')
]
ddtSchemes = Node_C('ddtSchemes', root, None, Key_C('ddtSchemes', *ddtSchemes_data))

# gradSchemes node
gradSchemes_data = [
    Str_P('default', default='Gauss linear')
]
gradSchemes = Node_C('gradSchemes', root, None, Key_C('gradSchemes', *gradSchemes_data))

# divSchemes node
divSchemes_data = [
    Str_P('default', default='none'),
    Str_P('div(phi,U)', default='bounded Gauss linearUpwind grad(U)'),
    Str_P('div(phi,k)', default='bounded Gauss limitedLinear 1'),
    Str_P('div(phi,epsilon)', default='bounded Gauss limitedLinear 1'),
    Str_P('div(phi,omega)', default='bounded Gauss limitedLinear 1'),
    Str_P('div(phi,v2)', default='bounded Gauss limitedLinear 1'),
    Str_P('div((nuEff*dev2(T(grad(U)))))', default='Gauss linear'),
    Str_P('div(nonlinearStress)', default='Gauss linear')
]
divSchemes = Node_C('divSchemes', root, None, Key_C('divSchemes', *divSchemes_data))

# laplacianSchemes node
laplacianSchemes_data = [
    Str_P('default', default='Gauss linear corrected')
]
laplacianSchemes = Node_C('laplacianSchemes', root, None, Key_C('laplacianSchemes', *laplacianSchemes_data))

# interpolationSchemes node
interpolationSchemes_data = [
    Str_P('default', default='linear')
]
interpolationSchemes = Node_C('interpolationSchemes', root, None, Key_C('interpolationSchemes', *interpolationSchemes_data))

# snGradSchemes node
snGradSchemes_data = [
    Str_P('default', default='corrected')
]
snGradSchemes = Node_C('snGradSchemes', root, None, Key_C('snGradSchemes', *snGradSchemes_data))

# wallDist node
wallDist_data = [
    Str_P('method', default='meshWave')
]
wallDist = Node_C('wallDist', root, None, Key_C('wallDist', *wallDist_data))

# Display the tree
show_tree(root)