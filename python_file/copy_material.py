from typing import Container
import bpy
import yaml
import numpy as np
import utils
import os

basecolor=((0,1),(0.2,0.8),(0.5,1))

def decimals_random(section):
    # section 元祖:(0.3,0.542),最多三位小数
    try :
        return np.random.randint(section[0]*1000,section[1]*1000)/1000
    except:
        raise Exception("{} 最多三位小数".format(section))

def policy_HSV_RANDOM(HSV_args=((0,1),1,1)):
    # HSV_args:((0,1),1,1)
    if isinstance(HSV_args[0],tuple):
        H=decimals_random(HSV_args[0])
    else:
        H=HSV_args[0]
    if isinstance(HSV_args[1],tuple):
        S=decimals_random(HSV_args[1])
    else:
        S=HSV_args[1]
    if isinstance(HSV_args[2],tuple):
        V=decimals_random(HSV_args[2])
    else:
        V=HSV_args[2]
    return utils.hsva2rgb(H*360,S,V,1)

def utils_change_texture(material_name,texture_name_prefix,policy="RANDOM"):
    
    color_tex_ls=[]
    for tex in bpy.data.images.keys():
        if tex.split('.')[0].split('_')[0]==texture_name_prefix and tex.split('.')[0].split('_')[-1]=='color':
            color_tex_ls.append(tex)
    print('color_tex_ls:',color_tex_ls)
    if policy=='RANDOM':
        color_tex_name=color_tex_ls[np.random.randint(0,len(color_tex_ls))]
        num=color_tex_name.split('.')[0].split('_')[-2]
        color_tex=bpy.data.images[color_tex_name]
        for tex in bpy.data.images.keys():
            if tex.split('.')[0].split('_')==[texture_name_prefix,num,'normal']:
                normal_tex=bpy.data.images[tex]    
            if tex.split('.')[0].split('_')==[texture_name_prefix,num,'roughness']:
                roughness_tex=bpy.data.images[tex]
    used_text_dict={}
    # 记录数据             
    for nodes in bpy.data.materials[material_name].node_tree.nodes.keys():
        if nodes.startswith('Image Texture'):
            texture_ori=bpy.data.materials[material_name].node_tree.nodes[nodes].image
            tx_kinds=texture_ori.name.split('.')[0].split('_')[-1]
            if tx_kinds.lower()=='color':
                bpy.data.materials[material_name].node_tree.nodes[nodes].image=color_tex
                used_text_dict['color_tex']=color_tex.name
            if tx_kinds.lower()=='roughness':
                bpy.data.materials[material_name].node_tree.nodes[nodes].image=roughness_tex
                used_text_dict['roughness_tex']=roughness_tex.name
            if tx_kinds.lower()=='normal':
                bpy.data.materials[material_name].node_tree.nodes[nodes].image=normal_tex
                used_text_dict['normal_tex']=normal_tex.name
                
    return used_text_dict

def utils_change_colorramp(material_name,ColorRamp=None):
    colorRamp_value_ls=[]
    for count in range(len(bpy.data.materials[material_name].node_tree.nodes["ColorRamp"].color_ramp.elements.values())):
        value=policy_HSV_RANDOM(ColorRamp)
        bpy.data.materials[material_name].node_tree.nodes["ColorRamp"].color_ramp.elements[count].color=value
        colorRamp_value_ls.append(value)
    return {'colorRamp_value_ls':colorRamp_value_ls}

def utils_change_layerWeight(material_name,LayerWeight_value):
    bpy.data.materials[material_name].node_tree.nodes['Layer Weight'].inputs[0].default_value=LayerWeight_value
    return {'LayerWeight_value':LayerWeight_value}
    
def utils_change_PrincipledBSDF(material_name,BaseColor=None,Specular=None,Roughness=None,
                                Scale=None,Distortion=None,SubsurfaceColor=None,
                                Emission=None,EmissionStrength=None):
    container={}
    if BaseColor:
        basecolor=policy_HSV_RANDOM(BaseColor)
        bpy.data.materials[material_name].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=basecolor
        container['BaseColor']=basecolor
    if Specular:
        bpy.data.materials[material_name].node_tree.nodes['Principled BSDF'].inputs['Specular'].default_value=Specular
        container['Specular']=Specular
    if Roughness:
        bpy.data.materials[material_name].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=Roughness
        container['Roughness']=Roughness
    if SubsurfaceColor:
        subsurfacecolor=policy_HSV_RANDOM(SubsurfaceColor)
        bpy.data.materials[material_name].node_tree.nodes['Principled BSDF'].inputs['Subsurface Color'].default_value=subsurfacecolor
        container['SubsurfaceColor']=subsurfacecolor
    if Emission:
        emission=policy_HSV_RANDOM(Emission)
        bpy.data.materials[material_name].node_tree.nodes['Principled BSDF'].inputs['Emission'].default_value=emission
        container['Emission']=emission
    if EmissionStrength:
        bpy.data.materials[material_name].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=EmissionStrength
        container['EmissionStrength']=EmissionStrength
    return container
    
def utils_change_noiseTexture(material_name,Scale=None,Distortion=None,Roughness=None):
    container={}
    if Scale:
        bpy.data.materials[material_name].node_tree.nodes['Noise Texture'].inputs['Scale'].default_value=Scale
        container['Scale']=Scale
    if Distortion:
        bpy.data.materials[material_name].node_tree.nodes['Noise Texture'].inputs['Distortion'].default_value=Distortion
        container['Distortion']=Distortion
    if Roughness:
        bpy.data.materials[material_name].node_tree.nodes['Noise Texture'].inputs['Roughness'].default_value=Roughness
        container['Roughness']=Roughness
    return container

def utils_change_glassBSDF(material_name,Color=None,Specular=None,Roughness=None):
    container={}
    if Color:
        color=policy_HSV_RANDOM(Color)
        bpy.data.materials[material_name].node_tree.nodes['Glass BSDF'].inputs['Color'].default_value=color
        container['Color']=color
    return container
        
def utils_change_fresnel(material_name,IOR=None):
    container={}
    if IOR:
        bpy.data.materials[material_name].node_tree.nodes['Fresnel'].inputs['IOR'].default_value=IOR
        container['IOR']=IOR
    return container

def utils_change_MixShader(material_name,Fac=None,Roughness=None):
    container={}
    if Fac:
        bpy.data.materials[material_name].node_tree.nodes['Mix Shader'].inputs['Fac'].default_value=Fac
        container['Fac']=Fac
    return container
    
def utils_change_CheckerTexture(material_name,color_2_CheckerTexture):
    container={}
    if color_2_CheckerTexture:
        value=policy_HSV_RANDOM(color_2_CheckerTexture)
        bpy.data.materials[material_name].node_tree.nodes['Checker Texture'].inputs['Color2'].default_value=value
        container['Color2']=value
    return container

def utils_change_emission(material_name,Color=None,Strength=None):
    container={}
    if Color:
        color=policy_HSV_RANDOM(Color)
        bpy.data.materials[material_name].node_tree.nodes['Emission'].inputs['Color'].default_value=color
        container['Color']=color
    if Strength:
        bpy.data.materials[material_name].node_tree.nodes['Emission'].inputs['Strength'].default_value=Strength
        container['Strength']=Strength
    return container

def utils_change_GlossyBSDF(material_name,Roughness):
    container={}
    if Roughness:
        bpy.data.materials[material_name].node_tree.nodes['Glossy BSDF'].inputs['Roughness'].default_value=Roughness
        container['Roughness']=Roughness
    return  container

def utils_change_MusgraveTexture(material_name,scale):
    container={}    
    if scale:
        bpy.data.materials[material_name].node_tree.nodes['Musgrave Texture'].inputs['Scale'].default_value=scale
        container['Scale']=scale
    return container

def utils_change_default_value(material_name,value):
    container={}
    bpy.data.materials[material_name].node_tree.nodes['Value'].outputs['Value'].default_value=value
    container['value']=value
    return container

def background():
    container={}
    data=utils_change_colorramp(material_name="background",ColorRamp=((0.5,1),(0.2,0.8),0.65))
    container['utils_change_colorramp']=data
    mat=bpy.data.materials['background'].copy()
    return mat,container

def crystal():
    '''
    - LayerWeight:Blend section:(0.35,0.95)
    - ColorRamp:3个节点 H、S、V 颜色可调节
    '''
    container={}
    data1=utils_change_colorramp(material_name="crystal",ColorRamp=((0,1),(0,1),(0,1)))
    container['utils_change_colorramp']=data1
    data2=utils_change_layerWeight(material_name="crystal",LayerWeight_value=decimals_random((0.35,0.95)))
    container['utils_change_layerWeight']=data2
    mat=bpy.data.materials['crystal'].copy()
    return mat , container

def glassBubble():
    '''ColorRamp
    - 调节2个节点参数 H 的范围为0～1，S 参数固定为1、V 参数固定为1
    MixShader
    - Fac 参数为 0.9～1'''
    container={}
    data1=utils_change_colorramp(material_name='glassBubble',ColorRamp=((0,1),1,1))
    container['utils_change_colorramp']=data1
    data2=utils_change_MixShader(material_name="glassBubble",Fac=decimals_random((0.9,1)))
    container['utils_change_MixShader']=data2
    mat=bpy.data.materials['glassBubble'].copy()
    return mat,container

def glossyValue():
    '''
    - BaseColor:调节颜色 H 为 0～1，S 默认为 0.68，V 默认为 1'''
    container={}
    data1=utils_change_PrincipledBSDF(material_name="glossyValue",BaseColor=basecolor)
    container['utils_change_PrincipledBSDF']=data1
    mat=bpy.data.materials['glossyValue'].copy()
    return mat,container

def paint():
    '''- BaseColor 调节 H、S、V
    - Specular 调节参数范围 0～1
    - Roughness 调节参数范围 0～1'''
    container={}
    data1=utils_change_PrincipledBSDF(material_name="paint",BaseColor=basecolor,Specular=decimals_random((0,1)),Roughness=decimals_random((0,1)))
    container['utils_change_PrincipledBSDF']=data1
    mat=bpy.data.materials['paint'].copy()
    return mat,container

def metalRoughness():
    '''- BaseColor 中 S 参数固定为0.65，调节 H、V'''
    container={}
    data=utils_change_PrincipledBSDF(material_name='metalRoughness',BaseColor=basecolor)
    container['utils_change_PrincipledBSDF']=data
    mat=bpy.data.materials['metalRoughness'].copy()
    return mat,container

def glassHue():
    # - Color: 调节 H 参数范围为0～1，S 参数范围为0～1，V 参数固定为1
    container={}
    data=utils_change_glassBSDF(material_name='glassHue',Color=((0,1),(0.2,0.8),1))
    container['utils_change_glassBSDF']=data
    mat=bpy.data.materials['glassHue'].copy()
    return mat,container

def glassColorful():
    '''- Scale 参数调节为 0～1
    - Distortion 参数调节为 0～1'''
    container={}
    data=utils_change_noiseTexture(material_name='glassColorful',Scale=decimals_random((0,1)),Distortion=decimals_random((0,1)))
    container['utils_change_noiseTexture']=data
    mat=bpy.data.materials['glassColorful'].copy()
    return mat,container

def glassRefraction():
    '''GlassBSDF
    - Roughness 调节参数范围 0～0.5
    Fresnel
    - IOR 调节参数范围 1.05～5
    '''
    container={}
    data1=utils_change_glassBSDF(material_name='glassRefraction',Roughness=decimals_random((0,0.5)))
    container['utils_change_glassBSDF']=data1
    data2=utils_change_fresnel(material_name='glassRefraction',IOR=decimals_random((1.05,5)))
    container['utils_change_fresnel']=data2
    return bpy.data.materials['glassRefraction'].copy(),container
    
def glossy():
    '''- BaseColor 调节 H、S、V
    - Specular 调节参数范围 0.25～1'''
    container={}
    data1=utils_change_PrincipledBSDF(material_name='glossy',BaseColor=basecolor,Specular=decimals_random((0.25,1)))
    container['utils_change_PrincipledBSDF']=data1
    return bpy.data.materials['glossy'].copy(),container

def metalRoughness():
    '''- BaseColor 中 S 参数固定为0.65，调节 H、V'''
    container={}
    data=utils_change_PrincipledBSDF(material_name='metalRoughness',BaseColor=basecolor)
    container['utils_change_PrincipledBSDF']=data
    return bpy.data.materials['metalRoughness'].copy(),container

def metalRefraction():
    '''- BaseColor 中 S 参数固定为0.5，调节 H、V'''
    container={}
    data=utils_change_PrincipledBSDF(material_name='metalRefraction',BaseColor=basecolor)
    container['utils_change_PrincipledBSDF']=data
    return bpy.data.materials['metalRefraction'].copy(),container

def patternChecker():
    '''Checker Texture
    - Color2 中调节 H、S、V
    Principle-BSDF
    - BaseColor 中 S 参数固定为0.5，V参数固定为1，调节 H'''
    container={}
    data1=utils_change_PrincipledBSDF(material_name='patternChecker',BaseColor=basecolor)
    container['utils_change_PrincipledBSDF']=data1
    data2=utils_change_CheckerTexture(material_name='patternChecker',color_2_CheckerTexture=((0,1),(0.5,1),(0.5,1)))
    container['utils_change_CheckerTexture']=data2
    return bpy.data.materials['patternChecker'].copy(),container

def subsurface():
    '''Principle-BSDF
    - BaseColor 中调节参数 H、S、V
    - SubsurfaceColor 中 H 调节参数 H、S、V 
    - Roughness 中参数范围为0～1'''
    container={}
    data1=utils_change_PrincipledBSDF(material_name='subsurface',SubsurfaceColor=((0,1),(0.5,1),(0.5,1)),BaseColor=basecolor,Roughness=decimals_random((0,1)))
    container['utils_change_PrincipledBSDF']=data1
    return(bpy.data.materials['subsurface'].copy()),container
    
def skin():
    '''Principle-BSDF
    - BaseColor 中 H 参数范围为0～0.1，S 参数固定为0.8，V 参数固定为1
    - SubsurfaceColor中 H 参数固定为0，S 参数范围为0.5～0.8，V 参数范围为0.3～1'''
    container={}
    data1=utils_change_PrincipledBSDF(material_name='skin',BaseColor=(()),SubsurfaceColor=(1,(0.6,0.7),1))
    container['utils_change_PrincipledBSDF']=data1
    return bpy.data.materials['skin'].copy(),container

def bones():
    '''Principle-BSDF
    - BaseColor 中 HSV'''
    container={}
    data1=utils_change_PrincipledBSDF(material_name='bones',BaseColor=basecolor)
    container['utils_change_PrincipledBSDF']=data1
    return bpy.data.materials['bones'].copy(),container

def emissionBase():
    '''Emission
    - Color 中  H 参数范围为 0～1，S 参数固定为 0～0.99，V 参数固定为1
    - Strength 参数范围为 5～50'''
    container={}
    data1=utils_change_emission(material_name='emissionBase',Color=((0,1),0.99,1),Strength=decimals_random((5,50)))
    container['utils_change_emission']=data1
    return bpy.data.materials['emissionBase'].copy(),container

def emissionTransparent():
    '''PrincipleBSDF
    - Emission 中颜色 H 参数范围为 0～1，S 参数固定为 1，V 参数固定为 1
    - EmissionStrength 参数范围为 5～50
    ''' 
    container={}
    data=utils_change_PrincipledBSDF(material_name='emissionTransparent',Emission=((0,1),1,1),EmissionStrength=decimals_random((5,50)))
    container['utils_change_PrincipledBSDF']=data
    return bpy.data.materials['emissionTransparent'].copy(),container

def emissionWeight():
    '''Emission
    - Emission 中颜色 H 参数范围为 0～1，S 参数固定为 0.85，V 参数固定为 1
    - Strength 参数范围为 5～50'''
    container={}
    data1=utils_change_emission(material_name='emissionWeight',Color=((0,1),0.85,1),Strength=decimals_random((5,50)))
    container['utils_change_emission']=data1
    return bpy.data.materials['emissionWeight'].copy(),container
    
# def drawingsTex():
#     '''Image texture:替换贴图，贴图命名为:drawingsmonalisa_01_color.jpeg'''
#     utils_change_texture(material_name='drawingsTex',texture_name_prefix='drawings',policy="RANDOM")
#     return bpy.data.materials['drawingsTex'].copy()

def clothTex():
    '''ImageTexture
    - 替换3张贴图，命名规范为:cloth_01_color/roughness/normal.jpg
    Value
    - 参数范围为1～5，可默认为2
    '''
    container={}
    data1=utils_change_texture(material_name='clothTex',texture_name_prefix='cloth',policy="RANDOM")
    container['utils_change_texture']=data1
    container['utils_change_default_value']=utils_change_default_value(material_name='clothTex',value=decimals_random((1,5)))
    return bpy.data.materials['clothTex'].copy(),container

def patternTex():
    '''mage texture:替换贴图，命名规范为:pattern_01_color.jpg'''
    container={}
    container['utils_change_texture']=utils_change_texture(material_name='patternTex',texture_name_prefix='pattern',policy="RANDOM")
    return bpy.data.materials['patternTex'].copy(),container

def hair():
    '''ColorRamp:2个节点 H、S、V 颜色可调节'''
    container={}
    container['utils_change_colorramp']=utils_change_colorramp(material_name='hair',ColorRamp=((0,1),(0,1),(0,1)))
    return bpy.data.materials['hair'].copy(),container
    
def colorfulHue():
    '''NoiseTexture
    - Scale:参数范围为1～2.5，可默认为 1
    PrincipledBSDF
    - SubsurfaceColor:调节颜色 H、S、V（也可只调节H，S 默认为0.6，V 默认为1）
    - Specular:参数范围为0.25～1，可默认为0.5
    - Roughness:参数范围为0.25～1，可默认为0.5
    GlossyBSDF
    - Roughness:参数范围为0～1
    NoiseTexture
    - Roughness:参数范围为0～0.25'''
    container={}
    
    container['utils_change_noiseTexture']=utils_change_noiseTexture(material_name='colorfulHue',Scale=decimals_random((1,2.5)),Roughness=decimals_random((0,0.25)))
    container['utils_change_PrincipledBSDF']=utils_change_PrincipledBSDF(material_name='colorfulHue',SubsurfaceColor=((0,1),(0.6,1),1),
                                Specular=decimals_random((0.25,1)),Roughness=decimals_random((0.25,1)))

    container['utils_change_GlossyBSDF']=utils_change_GlossyBSDF(material_name='colorfulHue',Roughness=decimals_random((0,1)))
    return bpy.data.materials['colorfulHue'].copy(),container

def colorfulValue():
    '''MusgraveTexture
    - Scale:参数范围为0～2，可默认为2
    ColorRamp
    - Pos为1的节点:调节 V 参数范围为0～1，H默认为0，S默认为0
    PrincipledBSDF
    - SubsurfaceColor:调节颜色 H、S、V（也可只调节H为0～1，S 默认为0.6，V 默认为1）
    - Specular:参数范围为0.25～1，可默认为0.5
    - Roughness:参数范围为0.25～1，可默认为0.25
    GlossyBSDF
    - Roughness:参数范围为0～1'''
    container={}
    container['utils_change_MusgraveTexture']=utils_change_MusgraveTexture(material_name='colorfulValue',scale=decimals_random((0,2)))
    container['utils_change_colorramp']=utils_change_colorramp(material_name='colorfulValue',ColorRamp=((0,1),0,0))
    container['utils_change_PrincipledBSDF']=utils_change_PrincipledBSDF(material_name='colorfulValue',SubsurfaceColor=((0,1),0.6,1),Specular=decimals_random((0.25,1)),Roughness=decimals_random((0.25,1)))
    container['utils_change_GlossyBSDF']=utils_change_GlossyBSDF(material_name='colorfulValue',Roughness=decimals_random((0,1)))
    return bpy.data.materials['colorfulValue'].copy(),container

def colorfulLight():
    '''PrincipledBSDF
    - BaseColor:调节颜色参数 H 范围为0～1，S 默认为0.6，V 默认为1
    - SubsurfaceColor:节颜色参数 H 范围为0～1，S 默认为0.275，V 默认为1
    GlossyBSDF
    - Roughness:参数范围为0～0.5'''
    container={}
    container['utils_change_PrincipledBSDF']=utils_change_PrincipledBSDF(material_name='colorfulLight',BaseColor=basecolor,SubsurfaceColor=((0,1),0.275,1))
    container['utils_change_GlossyBSDF']=utils_change_GlossyBSDF(material_name='colorfulLight',Roughness=decimals_random((0,0.5)))
    return bpy.data.materials['colorfulLight'].copy(),container

def colorfulRoughness():
    '''PrincipledBSDF
    - BaseColor:调节颜色 H、S、V（也可只调节H为0～1，S 默认为0.5，V 默认为1）'''
    container={}
    container['utils_change_PrincipledBSDF']=utils_change_PrincipledBSDF(material_name='colorfulRoughness',BaseColor=basecolor)
    return bpy.data.materials['colorfulRoughness'].copy(),container

def roughness():
    '''PrincipledBSDF
    - BaseColor:调节颜色 H、S、V'''
    container={}
    container['utils_change_PrincipledBSDF']=utils_change_PrincipledBSDF(material_name='roughness',BaseColor=basecolor)
    return bpy.data.materials['roughness'].copy(),container

def cartoon_mat():
    container={}
    bpy.data.materials['body'].node_tree.nodes["Group"].inputs[0].default_value=policy_HSV_RANDOM()
    bpy.data.materials['body'].node_tree.nodes["Group"].inputs[1].default_value=policy_HSV_RANDOM()
    bpy.data.materials['body'].node_tree.nodes["Group"].inputs[2].default_value=policy_HSV_RANDOM()
    bpy.data.materials['body'].node_tree.nodes["Group"].inputs[3].default_value=policy_HSV_RANDOM()
    bpy.data.materials['body'].node_tree.nodes["Group"].inputs[4].default_value=policy_HSV_RANDOM()
    bpy.data.materials['body'].node_tree.nodes["Group"].inputs[5].default_value=policy_HSV_RANDOM()
    return bpy.data.materials['body'].copy(),container
    
def v10_flat_mat(value):
    bpy.data.materials['flat'].node_tree.nodes["ColorRamp"].color_ramp.elements[0].color=value
    container={'v10_flat_colorRamp':value}
    return bpy.data.materials['flat'].copy(),container

def v10_paint_mat(value):
    bpy.data.materials['paint'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=value
    container={'v10_paint_colorRamp':value}
    return bpy.data.materials['paint'].copy(),container



if __name__ == '__main__':
    clothTex()