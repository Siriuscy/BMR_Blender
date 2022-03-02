from typing import Collection
import bpy
from mathutils import *
import numpy as np
import yaml
import string

def metaball_geneator(metadata,particles_conf_path):
    metaball_matada_dict={}
    conf=yaml.load(open(particles_conf_path,"r"),Loader=yaml.FullLoader)
    metaball_matada_dict['conf']=conf
    col_ls=bpy.data.collections.keys()
    if 'curves_metaballs' not in col_ls:
        bpy.data.collections.new('curves_metaballs')
        bpy.context.scene.collection.children.link(bpy.data.collections['curves_metaballs'])

    def create_one_metaball(curve_name,metaball_name,ball_index,
                            curve_location=(0, 0, 8.17),
                            ball_scale=(1, 1, 1),
                            curve_scale=(10, 10, 10),
                            one_round_frames=40,
                            frame_start=1,
                            frame_length=100,):
        # 材质设置
        if conf["mat_setting"]['type']=="RANDOM":
            for count in range(3):
                bpy.data.materials[conf["mat_setting"]['name']].node_tree.nodes["ColorRamp"].color_ramp.elements[count].color=(np.random.rand(),np.random.rand(),np.random.rand(),1)
        elif conf["mat_setting"]['type']=="VALUES":
            mat_value_ls= conf["mat_setting"]["VALUES"]
            for count in range(3):
                # 防止预制的材质不够
                try:
                    bpy.data.materials[conf["mat_setting"]['name']].node_tree.nodes["ColorRamp"].color_ramp.elements[count].color=mat_value_ls[ball_index][count]
                except:
                    bpy.data.materials[conf["mat_setting"]['name']].node_tree.nodes["ColorRamp"].color_ramp.elements[count].color=mat_value_ls[0][count]
        # elif conf["mat_setting"]['type']=="SENTA":        
        #     import senta_particles   
        #     from importlib import reload
        #     reload(senta_particles)
        #     senta_particles.senta_particles(text="我今天非常伤心",conf=conf)
        mat=bpy.data.materials[conf["mat_setting"]['name']].copy()
        
        import copy_material
        import utils
        from importlib import reload
        reload(copy_material)
        reload(utils)
        # value=utils.hsva2rgb(0.125*np.random.randint(9)*360,0.8,1,1)
        # mat=copy_material.v10_flat_mat(value)[0]
        
        bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children["curves_metaballs"]        
        bpy.ops.curve.primitive_bezier_circle_add(enter_editmode=False,
                                                align='WORLD', 
                                                location=curve_location,
                                                scale=curve_scale)
        bpy.context.object.name = curve_name
        # curve sacle transform
        bpy.context.object.scale=curve_scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        bpy.context.object.rotation_mode = 'QUATERNION'
        bpy.data.objects[curve_name].rotation_quaternion = tuple(np.random.random_integers(low=-100,high=101,size=(4)))
        bpy.data.objects[curve_name].keyframe_insert("rotation_quaternion", frame=frame_start) 
        bpy.data.objects[curve_name].rotation_quaternion = tuple(np.random.random_integers(low=-100,high=101,size=(4)))
        bpy.data.objects[curve_name].keyframe_insert("rotation_quaternion", frame=frame_start+frame_length) 
        bpy.data.objects[curve_name].data.bevel_object= bpy.data.objects['circle_loft']
        bpy.data.objects[curve_name].data.bevel_mode="OBJECT"
        bpy.context.object.data.materials.append(mat)
        

        bpy.ops.object.metaball_add(type=conf["metaball_type"],
                                    enter_editmode=False, 
                                    align='WORLD', 
                                    location=(0, 0, 0), 
                                    scale=(1,1,1))
        bpy.context.object.name = metaball_name
        # 选择材质/分辨率
        bpy.context.object.data.materials.append(mat)
        bpy.context.object.data.render_resolution = conf["render_resolution"]
        bpy.context.object.data.resolution = 0.05
        
        # 融球大小
        bpy.context.object.scale=ball_scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        bpy.ops.object.constraint_add(type='FOLLOW_PATH')
        bpy.data.objects[curve_name].data.path_duration=one_round_frames
        bpy.data.objects[metaball_name].constraints['Follow Path'].target=bpy.data.objects[curve_name]
        bpy.ops.constraint.followpath_path_animate(constraint="Follow Path",
                                                owner='OBJECT',
                                                frame_start=frame_start,
                                                length=frame_length)
        
        # 新建一个子对象作为发射器，并进行相关设置
        bpy.ops.mesh.primitive_uv_sphere_add(enter_editmode=False, 
                                             align='WORLD',
                                             location=(0, 0, 0),
                                             scale=(1, 1, 1))    
        
        bpy.context.object.parent=bpy.data.objects[metaball_name]
        bpy.context.object.scale=tuple([_*conf["emitter_scale"] for _ in ball_scale])
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.particle_system_add()
        setting=bpy.context.object.particle_systems[0].settings
        setting.count=conf["count"]
        setting.lifetime=conf["lifetime"]
        setting.lifetime_random=conf['lifetime_random']
        setting.damping=conf["damping"]
        setting.particle_size=conf["particle_size"]
        setting.size_random=conf["size_random"]
        setting.normal_factor=conf["normal_factor"]
        setting.brownian_factor=3
        setting.object_factor=conf["init_speed"]
        setting.use_rotations=True
        setting.rotation_factor_random=1
        setting.use_dynamic_rotation=True
        setting.physics_type="FLUID"

        setting.effector_weights.gravity=0
        setting.render_type="OBJECT"
        
        # 粒子对象的设置
        
        setting.instance_object=bpy.data.objects[metaball_name]
        bpy.context.object.show_instancer_for_render = False
        
        
    def clean_collection():
        for obj in bpy.data.collections["curves_metaballs"].objects.values():
            bpy.data.objects.remove(obj,do_unlink=True)
    clean_collection()
    
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children["curves_metaballs"]
    bpy.ops.curve.primitive_nurbs_circle_add(radius=conf["loft_radius"],
                                                enter_editmode=False,
                                                align='WORLD',
                                                location=(0, 0, 0),
                                                scale=(1, 1, 1))
    bpy.context.object.name ='circle_loft'
    
    random_num=np.abs(np.round(np.random.normal(loc=conf['metaball_num_mean'],scale=conf['metaball_num_scale']),0))
    ball_data_dict={}
    if random_num !=0:
        for count in range(int(random_num)):
            ball_scale=tuple([np.abs(np.round(np.random.normal(loc=conf['ball_scale_mean'],scale=conf['ball_scale_scale']),2))]*3)
            curve_scale=tuple([np.abs(np.round(np.random.normal(loc=conf['curve_scale_mean'],scale=conf['curve_scale_scale']),2))]*3)
            one_round_frames=np.random.randint(low=conf['one_ronund_frame_low'],high=conf['one_ronund_frame_high'])
            ball_data_dict[count]={'ball_scale':ball_scale,'curve_scale':curve_scale,'one_round_frames':one_round_frames}
            create_one_metaball(curve_name=string.ascii_uppercase[count],metaball_name=string.ascii_lowercase[count],
                                ball_scale=ball_scale,
                                curve_scale=curve_scale,
                                one_round_frames=one_round_frames,
                                ball_index=count,)
    metaball_matada_dict['metadata']=ball_data_dict
    metadata['metaball_metadata']=metaball_matada_dict
    bpy.ops.ptcache.bake_all(bake=True)

    return metadata

if __name__ == '__main__':
    metaball_geneator(particles_conf_path='../particles_conf.yml')
    # bpy.ops.ptcache.free_bake_all("EXEC_DEFAULT")
    bpy.ops.ptcache.bake_all(bake=True)
    bpy.context.scene.frame_set(90)
    # bpy.ops.screen.animation_play()
    # print("start")
    # while True:
    #     if bpy.context.scene.frame_current >40:
    #         bpy.ops.screen.animation_play()
    #         break
    # bpy.context.scene.frame_set(40)