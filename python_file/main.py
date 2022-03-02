import bpy
import os
import numpy as np
import yaml
import string
import json
import bmesh
import random
from importlib import reload
import sys
import tqdm

def main(num,initialize=True,calculate_multi_mat_obj=True,save_mode='PICTURE'):
    
# STEP 0: 导入数据
    conf=yaml.load(open('../conf.yml','r',encoding='utf-8'),Loader=yaml.FullLoader)

# STEP 1: 初始化
    '''
    1.将所有的动画非static_collection的origin设置为(0,0,0),为动画做准备
    2.删除所有动画
    3.重置所有的贴图文件
    '''
    if initialize==True and num==0:
        initial.initial()
    
# STEP 2: 计算并保存多材质数据 
    # 返回多材质点位数据，第一次需要计算
    
    if calculate_multi_mat_obj==True and num==0:
        multi_obj_ls=utils.find_multi_mat_obj(multi_mat_obj_filePath=conf['multi_mat_obj_filePath'])
    else:
        multi_obj_ls=json.load(open(conf['multi_mat_obj_filePath'],'r'))
        
    if multi_obj_ls !=[]:
        multi_obj_name_ls=multi_obj_ls.keys()
    else:
        multi_obj_name_ls=[]

        
# STEP 3: 选择元素
    one_code,one_result=utils.choose_element(conf)
    if one_code !='REPEATED':
        

# STEP 4: 给元素赋予材质，记录数据
        metadata=utils.assign_material(one_result,multi_obj_name_ls,multi_obj_ls,one_code)

# STEP 5:独显展示所有元素:
        utils.show_models(one_result)

# STEP 6:添加粒子: 
        metadata_withParticles=particles.metaball_geneator(metadata,particles_conf_path=particles_conf_path)
    
# STEP 7:设置旋转动画:
        # utils.set_annimation(conf=conf,chosed_element=one_result,)
    
# STEP 7:渲染保存:
        # utils.render(conf,code=one_code)

# STEP 8:清除多余材质:
        utils.cleanup()
    
# STEP 9:记录元数据:
        utils.save_metadata(conf,metadata_withParticles)
    
 
if __name__ == '__main__':
    conf_path='../conf.yml'
    particles_conf_path='../particles_conf.yml'
    conf=yaml.load(open(conf_path,"r"),Loader=yaml.FullLoader)
    if conf["dir_path"] not in sys.path:
        sys.path.append(conf["dir_path"])
        
    import particles
    import utils
    import copy_material
    import initial
    reload(initial)
    reload(particles)
    reload(utils)
    reload(copy_material)
    
    for _ in tqdm.tqdm(range(2)):
        main(initialize=False,calculate_multi_mat_obj=False,num=_)
    # todo :initial 材质加载还有问题

    
    
    

