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


def get_mean(kmeans_roi_data, dcm_roi_data, subregion=1):
    pixel_list = []
    index = np.argwhere(kmeans_roi_data == subregion)
    for (img_num, x_index, y_index) in index:
        pixel_list.append(dcm_roi_data[img_num][x_index, y_index])
    return np.mean(pixel_list)  # 需判断index是否为0，为0则均值设为0


if __name__ == '__main__':

    df_xlsx = pd.read_excel('I:/EGFR19 vs 21/EGFR_Primary/segmentation/T2W.xlsx')
    pathlist = df_xlsx['path']

    df = pd.DataFrame()
    path_excel = r'I:/EGFR19 vs 21/EGFR_Primary/segmentation/T2W_entropy_superpixel_kmeans20.xlsx'

    rest_num = len(pathlist)
    for dir_path in pathlist:
        print('现在处理的文件夹: ', dir_path)
        rest_num = rest_num - 1
        print('剩余人数： ', rest_num, '\n')
        # dcm_path = os.path.join(dir_path, 'roi_entropy_sitk.nrrd')
        dcm_path = os.path.join(dir_path, 'entropy.nrrd')
        #         nii_path = os.path.join(dir_path,'nii_sitk.nrrd')
        #         roi_entropy_path = os.path.join(dir_path,'roi_entropy_sitk.nrrd')
        # roi_kmeans_path = os.path.join(dir_path, 'roi_kmeans20.nrrd')  # 修改这里 和 下一行
        roi_kmeans_path = os.path.join(dir_path, 'kmeans20.nrrd')  # 修改这里 和 下一行
        cluster_num = 20

        dcm_data = get_img_data(path=dcm_path)
        #         nii_data = get_img_data(path = nii_path)
        roi_kmeans_data = get_img_data(path=roi_kmeans_path)
        #         roi_entropy_data = get_img_data(path = roi_entropy_path)

        name_list = []
        for num in range(cluster_num):
            name_list.append('entropy_subregion_' + str(num + 1).rjust(2, '0'))  # subregion 的变量名列表
        dict = {}
        dict['path'] = dir_path

        for subregion_num in range(cluster_num):
            dict[name_list[subregion_num]] = get_mean(kmeans_roi_data=roi_kmeans_data, dcm_roi_data=dcm_data,
                                                      subregion=subregion_num + 1)  # 别忘了加1，range是从0开始的。
        df = df._append(pd.DataFrame.from_dict(dict, orient='index').transpose(), sort=True)
        df.to_excel(path_excel)
