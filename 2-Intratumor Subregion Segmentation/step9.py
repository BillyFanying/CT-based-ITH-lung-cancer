import matplotlib.pyplot as plt
import sklearn
from sklearn.cluster import KMeans
from sklearn import metrics
import pandas as pd
import numpy as np
import os
import SimpleITK as sitk
import sklearn
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split


def df2list(df):  # Extract values of dataframe and return as list
    data_list = []
    for row in df.values:  # For each row
        for row_num in row:
            data_list.append(row_num)
    return data_list


def del_path_label(df):  # Delete path, label
    del df['path']
    del df['label']
    return df


def get_img_data(path):  # Returns image data
    img = sitk.ReadImage(path)
    data = sitk.GetArrayFromImage(img)
    return data


def get_excel_valus(path):
    return del_path_label(pd.DataFrame(pd.read_excel(path))).values  # Delete path, label


def load_train_test_data(path):  # Stratified sampling, requires label column
    df = pd.DataFrame(pd.read_excel(path))
    train_set, test_set = train_test_split(df, test_size=1 / 3, stratify=df['label'], random_state=1)

    return (del_path_label(train_set), del_path_label(test_set))


path_dcm = 'I:/EGFR19 vs 21/EGFR_Primary/segmentation/T2W_dcm_superpixel_kmeans20.xlsx'  # Replace with your own file path
path_entropy = 'I:/EGFR19 vs 21/EGFR_Primary/segmentation/T2W_entropy_superpixel_kmeans20.xlsx'  # Replace with your own file path

dcm_train_set, dcm_test_set = load_train_test_data(path=path_dcm)
entropy_train_set, entropy_test_set = load_train_test_data(path=path_entropy)

dcm_train_list = df2list(dcm_train_set)
entropy_train_list = df2list(entropy_train_set)

vector = np.array([dcm_train_list, entropy_train_list])
vector = vector.transpose()
scaler = MinMaxScaler()
scaler.fit(vector)
vector = scaler.transform(vector)  # Data standardization

km = KMeans(n_clusters=2, random_state=0)  # Number of clusters n_clusters
km.fit(vector)  # Train model
km.predict(vector)
lab = km.labels_
aa = set(lab)
clu = km.cluster_centers_
ine = km.inertia_
dcm_superpixels = get_excel_valus(path=path_dcm)
entropy_superpixels = get_excel_valus(path=path_entropy)

df_xlsx = pd.read_excel('I:/EGFR19 vs 21/EGFR_Primary/segmentation/T2W.xlsx')
pathlist = df_xlsx['path']

rest_num = len(pathlist)
count = 0  # Patient index

kmeans_num = 20  # Number of clusters at patient-level for KMeans
for dir_path in pathlist:
    print('Folder currently being processed: ', dir_path)
    rest_num = rest_num - 1
    print('Remaining count: ', rest_num, '\n')

    nii_path = os.path.join(dir_path, 'kmeans20.nrrd')
    roi_kmeans_path = os.path.join(dir_path, '180p_guiyi_roi_kmeans20_cluster2_seed1_1_3_random0.nrrd')
    nii_data = get_img_data(path=nii_path)

    patient_vector = np.array([dcm_superpixels[count], entropy_superpixels[count]]).transpose()
    patient_vector = scaler.transform(patient_vector)
    new_label = km.predict(patient_vector) + 1  # +1 to avoid cluster value of 0, new_label is the new label for subregions 1 to 20

    nii_kmeans = np.zeros(nii_data.shape)  # Store clustering results
    for num in range(kmeans_num):
        index = np.argwhere(nii_data == num + 1)
        for (img_num, x_index, y_index) in index:
            nii_kmeans[img_num][x_index, y_index] = new_label[num]  # Reassign labels to different subregions

    img_roi_kmeans = sitk.GetImageFromArray(nii_kmeans)
    img_nii = sitk.ReadImage(nii_path)
    img_roi_kmeans.CopyInformation(img_nii)
    sitk.WriteImage(img_roi_kmeans, roi_kmeans_path)

    count = count + 1
