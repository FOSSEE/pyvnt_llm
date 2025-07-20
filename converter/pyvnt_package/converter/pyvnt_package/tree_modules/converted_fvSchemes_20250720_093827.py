from pyvnt import *

# Create the root node
root = Node_C('fvSchemes', None, None)

# FoamFile node
foamFile_node = Node_C('FoamFile', root, None)

# FoamFile Key_Cs
format_prop = Str_P('format', default='ascii')
class_prop = Str_P('class', default='dictionary')
location_prop = Str_P('location', default='system')
object_prop = Str_P('object', default='fvSchemes')

foamFile_key = Key_C('FoamFile_data', format_prop, class_prop, location_prop, object_prop)

foamFile_node.data.append(foamFile_key)


# ddtSchemes node
ddtSchemes_node = Node_C('ddtSchemes', root, None)

# ddtSchemes Key_Cs
ddt_default_prop = Enm_P('default', items={'Euler', ' CrankNicolson', 'backward'}, default='Euler')

ddtSchemes_key = Key_C('ddtSchemes_data', ddt_default_prop)
ddtSchemes_node.data.append(ddtSchemes_key)


# gradSchemes node
gradSchemes_node = Node_C('gradSchemes', root, None)

# gradSchemes Key_Cs
grad_default_prop = Str_P('default', default='Gauss linear')

gradSchemes_key = Key_C('gradSchemes_data', grad_default_prop)
gradSchemes_node.data.append(gradSchemes_key)

# divSchemes node
divSchemes_node = Node_C('divSchemes', root, None)

# divSchemes Key_Cs
div_default_prop = Str_P('default', default='none')
div_phiU_prop = Str_P('div(phi,U)', default='Gauss limitedLinearV 1')
div_phiK_prop = Str_P('div(phi,k)', default='Gauss limitedLinear 1')
div_phiEpsilon_prop = Str_P('div(phi,epsilon)', default='Gauss limitedLinear 1')
div_phiOmega_prop = Str_P('div(phi,omega)', default='Gauss limitedLinear 1')
div_phiR_prop = Str_P('div(phi,R)', default='Gauss limitedLinear 1')
div_R_prop = Str_P('div(R)', default='Gauss linear')
div_phiNuTilda_prop = Str_P('div(phi,nuTilda)', default='Gauss limitedLinear 1')
div_nuEff_prop = Str_P('div((nuEff*dev2(T(grad(U)))))', default='Gauss linear')

divSchemes_key = Key_C('divSchemes_data', div_default_prop, div_phiU_prop, div_phiK_prop, div_phiEpsilon_prop, div_phiOmega_prop, div_phiR_prop, div_R_prop, div_phiNuTilda_prop, div_nuEff_prop)
divSchemes_node.data.append(divSchemes_key)


# laplacianSchemes node
laplacianSchemes_node = Node_C('laplacianSchemes', root, None)

# laplacianSchemes Key_Cs
laplacian_default_prop = Str_P('default', default='Gauss linear corrected')

laplacianSchemes_key = Key_C('laplacianSchemes_data', laplacian_default_prop)
laplacianSchemes_node.data.append(laplacianSchemes_key)


# interpolationSchemes node
interpolationSchemes_node = Node_C('interpolationSchemes', root, None)

# interpolationSchemes Key_Cs
interpolation_default_prop = Str_P('default', default='linear')

interpolationSchemes_key = Key_C('interpolationSchemes_data', interpolation_default_prop)
interpolationSchemes_node.data.append(interpolationSchemes_key)


# snGradSchemes node
snGradSchemes_node = Node_C('snGradSchemes', root, None)

# snGradSchemes Key_Cs
snGrad_default_prop = Str_P('default', default='corrected')

snGradSchemes_key = Key_C('snGradSchemes_data', snGrad_default_prop)
snGradSchemes_node.data.append(snGradSchemes_key)

show_tree(root)