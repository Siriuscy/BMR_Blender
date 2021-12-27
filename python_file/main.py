import bpy
import os
import numpy as np
import yaml
import json
import bmesh
from mathutils import Euler,Vector
from math import pi
import tqdm

def main(done_codes_path,
         codes_path,
         conf_path,
         pic_save_path,
         multi_mat_file_path,
         render_setting):
    
    exception_col_set=set(yaml.load(open(conf_path,'r'),Loader=yaml.FullLoader)['exception_collection'])
    video_setting=yaml.load(open(conf_path,'r'),Loader=yaml.FullLoader)['video_setting']
    static_collection_ls=yaml.load(open(conf_path,'r'),Loader=yaml.FullLoader)['static_collection']
    done_codes_ls=yaml.load(open(done_codes_path,"r"),Loader=yaml.FullLoader)
    multi_mat_file_dict=json.load(open(multi_mat_file_path,"r"))
    
    print("Have Done Codes:",done_codes_ls)
    if not done_codes_ls:
        done_codes_ls=[]

    print("reading done codes...\n"+"-"*50)

    all_codes=yaml.load(open(codes_path,"r"),Loader=yaml.FullLoader)
    
    # 1.把所有的非保护对象隐藏掉。
    for one_code in tqdm.tqdm(all_codes):
        for _ in bpy.data.objects.values():
            col_set=set([_.name for _ in _.users_collection])
            if not col_set & exception_col_set:
                _.hide_render=True
                
        code=one_code[0]
        obj_ls=one_code[1]
        
    # 2.查询是否已经生成。
        if code in done_codes_ls:
            print('{} have done'.format(code))
        else:
            print("Start to generate {}".format(code))
    
    # 3.将选中的object显示出来。        
            for one_dic in obj_ls:
            # like {'brain_01': {'brain_01': 'glass_01', 'bull': 'metal_01'}}
                parent_obj=bpy.data.objects[list(one_dic.keys())[0]]
                def set_render_true(parent_obj):
                    parent_obj.hide_render=False
                    for child_obj in parent_obj.children:
                        child_obj.hide_render=False
                        if child_obj.children !=():
                            set_render_true(child_obj)
                set_render_true(parent_obj)
    
    # 4.将选中的object赋予相应的材质。          
                # assign materials:
                for obj_mat in one_dic.values():
                    obj_name=list(obj_mat.keys())[0]
                    mat_name=list(obj_mat.values())[0]
                    print("{} is assigning material.".format(obj_name))
                    if isinstance(mat_name,str):                    
                        bpy.data.objects[obj_name].data.materials[0]=bpy.data.materials[mat_name]
                    else:
                        # 多材质的情况
                        print("{} has multiple materials.".format(obj_name))
                        bpy.context.view_layer.objects.active = bpy.data.objects[obj_name]
                        bpy.ops.object.mode_set(mode='EDIT')
                        bm= bmesh.from_edit_mesh(bpy.data.objects[obj_name].data)
                        face_index_ls=list(multi_mat_file_dict[obj_name].values())
                        for one_mat_ls in face_index_ls:
                            mat_index=mat_name[0]
                            mat_name.remove(mat_index)
                            for face in one_mat_ls:
                                if hasattr(bm.faces, "ensure_lookup_table"): 
                                    bm.faces.ensure_lookup_table()
                                bm.faces[face].material_index=mat_index
                        bpy.ops.object.mode_set(mode='OBJECT')
                        
            print("Material assignment done...\n"+"-"*50+"\n")       
    # 5.选择渲染方式：PICTURE/VIDEO。  
            if render_setting=="PICTURE":          
                print("Start to render one picture...")
                bpy.context.scene.render.filepath=os.path.join(pic_save_path,code+'.png')
                bpy.ops.render.render(write_still=True)
    # 5.1 渲染方式是video时，设置单帧输出或者视频输出
            elif render_setting=="VIDEO":
                
                time_scale=video_setting['time_scale']
                rotation=video_setting['rotation']
                output_setting=video_setting['output_setting']
                
                fps=bpy.context.scene.render.fps
                bpy.context.scene.frame_end = fps*time_scale

                for one_dic in obj_ls:
                    # like {'brain_01': {'brain_01': 'glass_01', 'bull': 'metal_01'}}
                    parent_obj=bpy.data.objects[list(one_dic.keys())[0]]                      
                    parent_col_ls=set([_.name for _ in parent_obj.users_collection])
                    if parent_obj.parent==None and set(parent_col_ls).intersection(set(static_collection_ls))==set():
                        print("{} is setting a animation.".format(parent_obj.name))
                        # 只对父级object且不在static collection中的object进行旋转。
                        
                        parent_obj.keyframe_insert("rotation_euler", frame=1) 
                        parent_obj.rotation_euler[2]+=pi * rotation / 180
                        parent_obj.keyframe_insert("rotation_euler", frame=fps*time_scale)
                        
    # 5.2 设置输出                
                if output_setting in ['AVI_JPEG','AVI_RAW',"FFMPEG"]:
                    print("Rendering VIDEO...")
                    bpy.context.scene.render.image_settings.file_format=output_setting
                    if output_setting=="FFMPEG":
                        bpy.context.scene.render.ffmpeg.format='MPEG4'
                        bpy.context.scene.render.ffmpeg.codec="H264"
                        bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
                        bpy.context.scene.render.use_stamp_note = True
                        bpy.context.scene.render.stamp_note_text = "BMR-LAB CHINA TONGJI UNIVERSITY."

                    bpy.context.scene.render.filepath=os.path.join(pic_save_path,code)
                    bpy.ops.render.render(animation=True,write_still=True)
                else:
                    print("Rendering ARRAY IMAGES...")
                    bpy.context.scene.render.image_settings.file_format=output_setting
                    new_path=os.path.join(pic_save_path,code)
                    if os.path.exists(new_path):
                        print("{} have been existed.".format(new_path))
                    else:
                        os.mkdir(new_path)
                    bpy.context.scene.render.filepath=os.path.join(new_path,'frames')
                    bpy.ops.render.render(animation=True)
                        
            done_codes_ls.append(str(code))
            yaml.dump(done_codes_ls,open(done_codes_path,"w"),default_flow_style=False)
            
            print("{} done".format(code))
            
if __name__ == '__main__':
    main(done_codes_path='../done_codes.yml',
         codes_path='../codes.yml',
         conf_path='../conf.yml',
         pic_save_path='../results',
         multi_mat_file_path='../multi_mat_obj.json',
         render_setting="VIDEO")
    