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


def to_nrrd(nii_data, dcm_data, outpath):  # nii_data is NIfTI mask array, dcm_data is DICOM image array, outpath is path to save the output NRRD
    nii_array = nii_data
    img_nrrd = dcm_data
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

    img_voi_nrrd.CopyInformation(sitk.ReadImage(os.path.join(os.path.dirname(outpath), 'dcmyuanshi.nrrd')))
    sitk.WriteImage(img_voi_nrrd, outpath)


if __name__ == '__main__':
    df_xlsx = pd.read_excel('I:/EGFR19 vs 21/EGFR_Primary/segmentation/T2W.xlsx')
    pathlist = df_xlsx['path']
    rest_num = len(pathlist)
    for dir_path in pathlist:
        dcm_path = os.path.join(dir_path, 'dcmyuanshi.nrrd')
        nii_path = os.path.join(dir_path, 'nii5.nrrd')
        outpath = os.path.join(dir_path, 'dcm5.nrrd')
        print('dcm_path: ', dcm_path)
        print('Folder currently being processed: ', dir_path)
        dcm_data = get_img_data(path=dcm_path)
        nii_data = get_img_data(path=nii_path)
        rest_num = rest_num - 1
        print('Remaining count: ', rest_num)
        to_nrrd(nii_data=nii_data, dcm_data=dcm_data, outpath=outpath)
