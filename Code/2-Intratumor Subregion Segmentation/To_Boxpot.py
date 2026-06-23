
import matplotlib.pyplot as plt
import scipy.misc
import numpy as np
import SimpleITK as sitk
import pandas as pd
import os


def get_img_data(path):  # 返回图像数据
    img = sitk.ReadImage(path)
    data = sitk.GetArrayFromImage(img)
    return data

def get_pixels_mean(img, nii, subregion_mum=2):
    pixel_list = []
    index = np.argwhere(nii_data == subregion_mum)
    for (num, x_index, y_index) in index:
        pixel_list.append(img[num][x_index, y_index])

    return np.mean(pixel_list)


#df_xlsx = pd.read_excel('F:/XiongZui/T1_pathlist_187p.xlsx')
df_xlsx = pd.read_excel('I:/EGFR19 vs 21/EGFR_Primary/segmentation/T1CE.xlsx')
pathlist = df_xlsx['path']
subregion_num =2

dcm_list = []
entropy_list = []
for dir_path in pathlist:
    print('现在处理的文件夹: ', dir_path)

    dcm_path = os.path.join(dir_path, 'dcm5.nrrd')
    #     nii_path = os.path.join(dir_path,'nii_sitk.nrrd')
    roi_entropy_path = os.path.join(dir_path, 'entropy.nrrd')
    roi_kmeans_path = os.path.join(dir_path, '180p_guiyi_roi_kmeans20_cluster2_seed1_1_3_random0.nrrd')  #

    dcm_data = get_img_data(path=dcm_path)
    nii_data = get_img_data(path=roi_kmeans_path)
    roi_entropy_data = get_img_data(path=roi_entropy_path)

    dcm_list.append(get_pixels_mean(img=dcm_data, nii=nii_data, subregion_mum=subregion_num))
    entropy_list.append(get_pixels_mean(img=roi_entropy_data, nii=nii_data, subregion_mum=subregion_num))
subregion_list = []



for num in range(len(dcm_list)):
    subregion_list.append('subregion 2')

dict = {}
dict['label'] = pathlist[0]
dict['path'] = pathlist[1]
dict['subregion'] = subregion_list
dict['dcm_list'] = dcm_list
dict['entropy_list'] = entropy_list


res_arr = np.array(dict)


print(dict)


df = pd.DataFrame()
df.to_excel('I:/EGFR19 vs 21/EGFR_Primary/segmentation/testsub2.xlsx')

print('-----------')
print(pd.DataFrame.from_dict(dict, orient='index'))
df = df._append(pd.DataFrame.from_dict(dict, orient='index').transpose(), sort=True)



df.to_excel('I:/EGFR19 vs 21/EGFR_Primary/segmentation/testsub2.xlsx')
df.head()

