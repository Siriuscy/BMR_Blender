import bpy
import os
import numpy as np
import yaml
import string
import json
import bmesh
import random

def find_multi_mat_obj(multi_mat_obj_filePath):
    '''[summary]
    找到所有的单个mesh多材质的物体，并保存在json文件中。

    Parameters
    ----------
    multi_mat_obj_filePath : [type]
        json文件地址

    Returns
    -------
    [type] dict
        [如果是单mesh多材质则返回]
    '''
    obj_ls=bpy.data.objects.values()
    container={}
    for obj in obj_ls:
        print("{} is judging if has multiple material...".format(obj.name))
        if obj.type=='MESH':
            # get mesh data
            if not obj.visible_get():
                obj.hide_set(False) 
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                mesh = bmesh.from_edit_mesh(obj.data)
                obj.hide_set(True)
                # bpy.ops.object.mode_set(mode='OBJECT')   
            else:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                mesh = bmesh.from_edit_mesh(obj.data)
                # bpy.ops.object.mode_set(mode='OBJECT')   
                
            # if multi mat
            mat_ls=[]
            for face in mesh.faces:
                mat_ls.append(face.material_index)
                
            if len(set(mat_ls))>=2:
                print("{} is multi mat".format(obj.name))
                
                mat_keys=obj.data.materials.keys()
                indexes = [[face.index, face.material_index] for face in mesh.faces]
                container_dic={}
                for face_index,mat_index in indexes:
                    mat=mat_keys[mat_index] 
                    if mat in container_dic.keys():
                        container_dic[mat].append(face_index)
                    else:
                        container_dic[mat]=[face_index]
                container[obj.name]=(container_dic)
            else:
                print("{} is single mat".format(obj.name))
            bpy.ops.object.mode_set(mode='OBJECT')   
        else:
            print("{} is not a mesh".format(obj.name))    
        
            
        
    open(multi_mat_obj_filePath,'w').close()                        
    json.dump(container,open(multi_mat_obj_filePath,'w'),indent=4)
    
    return container


def main(multi_mat_obj_filePath,read_multi_mat_file,file_name='codes',generate_len=20,):
    if read_multi_mat_file:
        multi_obj_ls=json.load(open(multi_mat_obj_filePath,'r'))
        print("Reading data from ",multi_mat_obj_filePath)
    else:
        print("Generating data about multi_mat_obj...")
        multi_obj_ls=find_multi_mat_obj(multi_mat_obj_filePath)
        
        
    if multi_obj_ls !=[]:
        multi_obj_name_ls=multi_obj_ls.keys()
        print("Find one mesh multiple materials : {}".format(list(multi_obj_name_ls)))
    else:
        print('no one mesh multiple materials found')
        multi_obj_name_ls=[]
        
    file_path="../"+file_name+'.yml'
    if os.path.exists(file_path):
        codes_ls=yaml.load(open(file_path,"r"),Loader=yaml.FullLoader)
        if not codes_ls:
            codes_ls=[]
        print("Reading generated codes from "+file_path)
    else:   
        codes_ls=[]
        open(file_path,"w").close()
        print("No generated codes exists,create codes file..."+"-"*20)
    print("-"*20+'\n'+'Generate codes ...')
    
    container_dict={}
    expection_collection_ls=yaml.load(open('../conf.yml','r'),Loader=yaml.FullLoader)['exception_collection']
    must_selected_at_lesat_one=yaml.load(open('../conf.yml','r'),Loader=yaml.FullLoader)['must_selected_at_lesat_one']
    all_must_selected=yaml.load(open('../conf.yml','r'),Loader=yaml.FullLoader)['all_must_selected']
    
    col_ls=bpy.data.collections.keys()
    for col in col_ls:
        if col not in expection_collection_ls:
            con=[]
            obj_ls=bpy.data.collections[col].all_objects.values()
            for _ in obj_ls:
                if not _.parent:
                    con.append(_.name)
            container_dict[col]=con  
    print(container_dict)

    
    while True:
        if len(codes_ls)>=generate_len:
            print("ALL DONE\n"+"-"*50)
            break
        one_code=""
        one_result=[]
        def process(num,container_dict,_):
                # 因为会有空的元素
                if num==len(container_dict[_]):
                    num='#'
                else:
                    # 判断是否有子对象，有则全部提取出
                    obj_name=container_dict[_][num]
                    obj=bpy.data.objects[obj_name]
                    # print("{} is processing to get a material...".format(obj_name))
                    dict={}
                    
                    one_obj_dict={}
                    one_obj_code=""
                    obj_ls=list(obj.children)+[obj]
                    
                    for obj in obj_ls :
                        if obj.type in ['MESH',"CURVE"]:
                            if obj.name in multi_obj_name_ls:
                                # 单mesh多材质
                                # print("{} is multi-mat...".format(obj.name))
                                materials=obj.data.materials.keys()
                                face_index_num=len(multi_obj_ls[obj.name].values())
                                print(obj.name)
                                index=random.sample(range(len(materials)),face_index_num)
                                one_obj_dict[obj.name]=index
                                for _ in index:
                                    one_obj_code+=(string.ascii_lowercase+string.ascii_uppercase)[_]
                            else:
                                materials=obj.data.materials.keys()
                                index=np.random.randint(0,len(materials))
                                one_obj_dict[obj.name]=materials[index]
                                one_obj_code+=(string.ascii_lowercase+string.ascii_uppercase)[index]
                    num=str(num)+one_obj_code
                    dict[obj.name]=one_obj_dict   
                    one_result.append(dict)
                return num     
                    # print("{} is done...".format(obj_name))                    
        
        keys_ls=sorted(container_dict.keys())
        for col_name in keys_ls:
            # 设置必选的collection，但是材质可选
            if col_name in must_selected_at_lesat_one:
                num=np.random.randint(0,len(container_dict[col_name]))
                num=process(num,container_dict,_=col_name)
            elif col_name in all_must_selected:
                for num in list(range(0,len(container_dict[col_name]))):
                    num=process(num,container_dict,_=col_name)
            else:
                num=np.random.randint(0,len(container_dict[col_name])+1)
                num=process(num,container_dict,_=col_name)
            
            
            one_code+=str(num)
        if one_code not in codes_ls and set(list(one_code))!=set(['#']):
            codes_ls.append([one_code,one_result])
    
    yaml.dump(codes_ls,open(file_path,"w"),default_flow_style=False)


if __name__ == '__main__':
    main(multi_mat_obj_filePath='../multi_mat_obj.json',
         file_name='codes',
         read_multi_mat_file=False,
         generate_len=1)

