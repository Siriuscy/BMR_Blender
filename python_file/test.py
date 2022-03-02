import bpy
import numpy as np
    
for _ in bpy.data.objects.values():
    try:
        _.data.materials.clear()
        
        _.data.materials.append(bpy.data.materials['toon'].copy())
    except:
        pass