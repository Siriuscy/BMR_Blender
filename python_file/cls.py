import bpy
import yaml

class Bobj():
    def __init__(self,obj_name,conf_path='../conf.yml'):
        self.name=bpy.data.objects[obj_name].name
        self.mat_ls=bpy.data.materials[obj_name].materials.values()
        self.conf=yaml.load(open(conf_path,'r'),Loader=yaml.FullLoader)

        self.mat=bpy.data.objects[obj_name].data.materials
        
    def mat_clear(self):
        self.mat.clear()
        return 'mat clear'
    
    def append_mat(self,new_mat):
        self.mat.append(new_mat)


    
    