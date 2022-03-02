import bpy
import tqdm

no_mat_ls=[]
one_dot_obj_ls=[]
multi_dot_obj_ls=[]
for obj in tqdm.tqdm(bpy.data.objects.values()):
    try:
        mat_name_ls=obj.data.materials.keys()
    except:
        pass
    # if len(mat_name_ls)==0:
    #     no_mat_ls.append(obj.name)
    # if len(mat_name_ls)==1:
    for mat_name in mat_name_ls:
        if '.' in mat_name :
            one_dot_obj_ls.append(obj.name)
    # else:
    #     for mat_name in mat_name_ls:
    #         if '.' in mat_name:
    #             multi_dot_obj_ls.append(obj.name)


# for _ in no_mat_ls:
#     bpy.data.objects[_].data.materials.clear()
#     obj.data.materials.append(bpy.data.materials['colorfulHue'])   
    
# for _ in one_dot_obj_ls:
#     print(_)
#     try:
#         mat=bpy.data.materials[(bpy.data.objects[_].data.materials.keys()[0].split('.')[0])]
#         bpy.data.objects[_].data.materials.clear()
#         bpy.data.objects[_].data.materials.append(mat)
#     except:
#         pass
    

# print('no mat:{}'.format(no_mat_ls))
print('have .001:{}'.format(set(one_dot_obj_ls)))
# print('have muliti .001:{}'.format(multi_dot_obj_ls))
