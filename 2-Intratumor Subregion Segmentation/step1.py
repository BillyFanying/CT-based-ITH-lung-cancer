import SimpleITK as sitk
import os
import pandas as pd
import numpy as np


def get_img_data(path):  # Returns image data
    img = sitk.ReadImage(path)
    data = sitk.GetArrayFromImage(img)
    return data


def scale255_3Ddata(data_3D):  # Scale 3D array pixel range to [0, 255].
    data255 = np.zeros(data_3D.shape)
    min_data = data_3D.min()
    max_data = data_3D.max()
    data255 = (data_3D - min_data) / (max_data - min_data)
    data255 = np.trunc(data255 * 255)
    return data255.astype(int)  # float to int conversion


def to_nrrd(file_path, nii_nrrd_name, nrrd_name):  # file_path is DICOM folder, nrrd_name is DICOM NRRD filename
    global img
    path_nrrd = os.path.join(file_path, nii_nrrd_name)
    print('path_nrrd: ', path_nrrd, '\n')

    for filename in os.listdir(file_path):
        if filename.endswith(('nii', 'nii.gz')):
            nii_path = os.path.join(file_path, filename)
            print('nii_path: ', nii_path)
            img = sitk.ReadImage(nii_path)
            sitk.WriteImage(img, path_nrrd)

    nii_array = sitk.GetArrayFromImage(img)

    series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(file_path)
    nb_series = len(series_IDs)
    print('Number of sequences in this folder', nb_series, '\n')
    series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(file_path)

    # Create a new ImageSeriesReader object
    series_reader = sitk.ImageSeriesReader()
    series_reader.SetFileNames(series_file_names)
    image3D = series_reader.Execute()
    sitk.WriteImage(image3D, os.path.join(file_path, 'dcmyuanshi.nrrd'))
    img_nrrd = sitk.GetArrayFromImage(image3D)
    slice_num = img_nrrd.shape[0]
    print(img_nrrd.shape)
    voi_data = np.zeros(img_nrrd.shape)
    for num in range(slice_num):
        if nii_array[num].max() == 1:
            index = np.argwhere(nii_array[num] == 1)
            for (i, j) in index:
                voi_data[num][i, j] = img_nrrd[num][i, j]
    voi_guiyi_data = scale255_3Ddata(data_3D=voi_data)
    img_voi_nrrd = sitk.GetImageFromArray(voi_guiyi_data)
    img_voi_nrrd.CopyInformation(image3D)
    sitk.WriteImage(img_voi_nrrd, os.path.join(file_path, nrrd_name))


if __name__ == '__main__':
    df_xlsx = pd.read_excel('I:/EGFR19 vs 21/EGFR_Primary/segmentation/T2W.xlsx')
    pathlist = df_xlsx['path']

    rest_num = len(pathlist)
    for dir_path in pathlist:
        print('Folder currently being processed: ', dir_path)
        rest_num = rest_num - 1
        print('Remaining count: ', rest_num)
        to_nrrd(dir_path, nii_nrrd_name='nii_sitk1.nrrd', nrrd_name='voi_sitk1.nrrd')
