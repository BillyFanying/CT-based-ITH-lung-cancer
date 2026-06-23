from numpy import *
from pylab import *
from PIL import Image
import matplotlib.pyplot as plt
import scipy.misc
import numpy as np
import SimpleITK as sitk
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import pandas as pd
import os


def get_img_data(path):  # Returns image data
    img = sitk.ReadImage(path)
    data = sitk.GetArrayFromImage(img)
    return data


def get_roi_data(data, nii_data, label=1):  # Returns all data pixel values corresponding to the ROI
    pixel_list = []
    index = np.argwhere(nii_data == label)
    for (img_num, x_index, y_index) in index:
        pixel_list.append(data[img_num][x_index, y_index])
    return pixel_list


if __name__ == '__main__':
    df_xlsx = pd.read_excel('I:/EGFR19 vs 21/EGFR_Primary/segmentation/T2W.xlsx')
    pathlist = df_xlsx['path']

    rest_num = len(pathlist)
    for dir_path in pathlist:
        print('Folder currently being processed: ', dir_path)
        rest_num = rest_num - 1
        print('Remaining count: ', rest_num, '\n')
        dcm_path = os.path.join(dir_path, 'dcm5.nrrd')
        nii_path = os.path.join(dir_path, 'nii_sitk1.nrrd')

        roi_entropy_path = os.path.join(dir_path, 'entropy.nrrd')
        roi_kmeans_path = os.path.join(dir_path, 'kmeans20.nrrd')
        n_clusters = 20

        dcm_data = get_img_data(path=dcm_path)
        nii_data = get_img_data(path=nii_path)
        roi_entropy_data = get_img_data(path=roi_entropy_path)

        dcm_list = get_roi_data(data=dcm_data, nii_data=nii_data)
        entropy_list = get_roi_data(data=roi_entropy_data, nii_data=nii_data)

        vector = np.array([dcm_list, entropy_list])
        vector = vector.transpose()
        scaler = MinMaxScaler()
        scaler.fit(vector)
        vector = scaler.transform(vector)  # Data standardization

        km = KMeans(n_clusters=n_clusters, random_state=0)
        km.fit(vector)

        nii_kmeans = np.zeros(nii_data.shape)  # Stores patient-level clustering results
        index = np.argwhere(nii_data == 1)
        for (num, x_index, y_index) in index:
            pixel = np.array([dcm_data[num][x_index, y_index], roi_entropy_data[num][x_index, y_index]])
            pixel = pixel.reshape(1, -1)
            pixel = scaler.transform(pixel)  # Standardization

            cluster_num = km.predict(pixel)[0]  # Predict K-Means result
            nii_kmeans[num][x_index, y_index] = cluster_num + 1  # Add 1 to avoid cluster_num = 0

        img_roi_kmeans = sitk.GetImageFromArray(nii_kmeans)
        img_nii = sitk.ReadImage(nii_path)
        img_roi_kmeans.CopyInformation(img_nii)
        sitk.WriteImage(img_roi_kmeans, roi_kmeans_path)
