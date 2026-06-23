from numpy import *
from pylab import *
from PIL import Image
import matplotlib.pyplot as plt
import scipy.misc
import numpy as np
import SimpleITK as sitk
import os
import pandas as pd


def get_entropy_roi(img_array, nii_array, nhood=9):
    Im = img_array
    m, n = Im.shape
    Im2 = zeros(Im.shape)  # 用于保存entropy矩阵
    k = int((nhood - 1) / 2)  # 模板半径
    index = np.argwhere(nii_array == 1)  # 只对ROI 区域计算entropy，节省时间

    for (i, j) in index:
        his = zeros(256)  # 熵的公式中的p是归一化后的局部直方图，0到255.
        for p in range(i - k, i + k + 1):
            for q in range(j - k, j + k + 1):
                his[Im[p, q]] = his[Im[p, q]] + 1
        his1 = his / float(sum(his))  # 归一化
        for g in range(0, 256):
            if his1[g] != 0:
                Im2[i, j] = Im2[i, j] - his1[g] * log(his1[g])  # Entropy is defined as -sum(p.*log2(p)),

    return Im2  # 返回entropy矩阵


def get_img_data(path):  # 返回图像数据
    img = sitk.ReadImage(path)
    data = sitk.GetArrayFromImage(img)
    return data


if __name__ == '__main__':

    df_xlsx = pd.read_excel('I:/EGFR19 vs 21/EGFR_Primary/segmentation/T2W.xlsx')
    pathlist = df_xlsx['path']

    rest_num = len(pathlist)
    for dir_path in pathlist:
        print('现在处理的文件夹: ', dir_path)
        dcm_path = os.path.join(dir_path, 'dcm5.nrrd')
        nii_path = os.path.join(dir_path, 'nii_sitk1.nrrd')
        roi_entropy_path = os.path.join(dir_path, 'entropy.nrrd')

        print('dcm_path: ', dcm_path)
        print('roi_entropy_path: ', roi_entropy_path, '\n')

        dcm_data = get_img_data(path=dcm_path)
        nii_data = get_img_data(path=nii_path)
        roi_entropy_data = np.zeros(dcm_data.shape)

        slice_num = roi_entropy_data.shape[0]
        for num in range(slice_num):
            if nii_data[num].max() == 1:  # 只对ROI区域计算entropy
                roi_entropy_data[num] = get_entropy_roi(img_array=dcm_data[num], nii_array=nii_data[num],
                                                        nhood=9)  # 此处不再缩放图像

        img_roi_entropy = sitk.GetImageFromArray(roi_entropy_data)
        img_dcm = sitk.ReadImage(dcm_path)
        img_roi_entropy.CopyInformation(img_dcm)
        sitk.WriteImage(img_roi_entropy, roi_entropy_path)

        rest_num = rest_num - 1
        print('剩余人数： ', rest_num)
