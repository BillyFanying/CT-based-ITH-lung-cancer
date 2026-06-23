import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn import metrics
import sklearn
import pandas as pd
import numpy as np
import os
import SimpleITK as sitk
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split


def get_subregion_pixel_nums(nii_data, sub_num=1):
    index = np.argwhere(nii_data == sub_num)
    return len(index)


def get_img_data(path):  # Returns image data
    img = sitk.ReadImage(path)
    data = sitk.GetArrayFromImage(img)
    return data


df_xlsx = pd.read_excel('I:/EGFR19 vs 21/EGFR_Primary/segmentation/T2W.xlsx')
pathlist = df_xlsx['path']
df = pd.DataFrame()

path_excel = 'I:/EGFR19 vs 21/EGFR_Primary/segmentation/T180p_T2W_kmeans20_cluster2_seed1的各个亚区像素数量.xlsx'  # Replace with your own path

rest_num = len(pathlist)
count = 0  # Patient index
kmeans_num = 20  # Number of clusters at patient-level for KMeans
for dir_path in pathlist:
    print('Folder currently being processed: ', dir_path)
    rest_num = rest_num - 1
    print('Remaining count: ', rest_num, '\n')

    roi_kmeans_path = os.path.join(dir_path, '180p_guiyi_roi_kmeans20_cluster2_seed1_1_3_random0.nrrd')
    roi_kmeans_data = get_img_data(path=roi_kmeans_path)

    dict = {}
    dict['path'] = dir_path
    dict['sub_01'] = get_subregion_pixel_nums(nii_data=roi_kmeans_data, sub_num=1)
    dict['sub_02'] = get_subregion_pixel_nums(nii_data=roi_kmeans_data, sub_num=2)

    df = df._append(pd.DataFrame.from_dict(dict, orient='index').transpose(), sort=True)
    df.to_excel(path_excel)
