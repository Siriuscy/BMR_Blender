import bpy
from mathutils import *
import math


bpy.ops.object.metaball_add(type='BALL', 
                            enter_editmode=False, 
                            align='WORLD', 
                            location=(0, 0, 0), 
                            scale=(1, 1, 1))
bpy.context.object.name = 'ball_metaball'

bpy.ops.curve.primitive_bezier_circle_add(enter_editmode=False,
                                          align='WORLD', 
                                          location=(0, 0, 0),
                                          scale=(1, 1, 1))
bpy.context.object.name = 'circle_bezier'
bpy.data.objects["ball_metaball"].constraints['Follow Path'].target=bpy.data.objects["circle_bezier"]
bpy.ops.constraint.followpath_path_animate(constraint="Follow Path",
                                           owner='OBJECT')
