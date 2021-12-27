import bpy

def generate_materials(mat_name, color_hsva, strength):
    '''[summary]

    Parameters
    ----------
    mat_name : [str]
            材质的名称
    color_hsv : [tuple]
        材质 rgba，
    strength : [float]
        光的强度
    '''
    bpy.data.materials.new(mat_name)
    bpy.data.materials[mat_name].use_nodes = True
    bpy.data.materials[mat_name].node_tree.nodes.new(
        type=('ShaderNodeEmission'))
    bpy.data.materials[mat_name].node_tree.nodes["Emission"].inputs[
        0].default_value = color_hsva
    bpy.data.materials[mat_name].node_tree.nodes["Emission"].inputs[
        1].default_value = strength
    bpy.data.materials[mat_name].node_tree.links.new(
        bpy.data.materials[mat_name].node_tree.nodes['Material Output'].
        inputs['Surface'],
        bpy.data.materials[mat_name].node_tree.nodes['Emission'].outputs[0])

