import PIL.Image as im
import os
import math
import datetime
import tqdm

# python /Users/chenyu/Desktop/BMR_blender/version_material/joint_images.py

date=datetime.date.today().strftime("%m_%d").__str__()
pic_all_dir='./results'
joint_pic_dir='./joint_results'
pic_path_ls=os.listdir(pic_all_dir)
try:
    pic_path_ls.remove('.DS_Store')
except:
    pass

bg=im.new(mode='RGB',size=(1300*5,1300*math.ceil((len(pic_path_ls)//5))),color=(0,0,0))
with tqdm.tqdm(total=len(pic_path_ls)) as pbar:
    for count,pic_path in enumerate(pic_path_ls):
        pic=im.open(os.path.join(pic_all_dir,pic_path)).resize((1280,1280),im.ANTIALIAS)
        bg.paste(pic,(1300*(count%5),1300*(count//5)))
        
        pbar.update(1)
    
print("saving...")

num=0
save_path=os.path.join(joint_pic_dir,date+'_'+str(num)+'.jpg')
while os.path.exists(save_path):
    num+=1
    save_path=os.path.join(joint_pic_dir,date+'_'+str(num)+'.jpg')
    
bg.save(save_path)
    

    