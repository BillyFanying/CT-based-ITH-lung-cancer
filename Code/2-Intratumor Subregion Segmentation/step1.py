import SimpleITK as sitk
import os
import pandas as pd
import numpy as np


def get_img_data(path):  # 返回图像数据
    img = sitk.ReadImage(path)
    data = sitk.GetArrayFromImage(img)
    return data


def scale255_3Ddata(data_3D):  # 将三维数组 像素值范围缩放到【0，255】。如果数组最大值本来就是255，那么不再做处理。
    data255 = np.zeros(data_3D.shape)
    min_data = data_3D.min()
    max_data = data_3D.max()
    data255 = (data_3D - min_data) / (max_data - min_data)
    data255 = np.trunc(data255 * 255)
    return data255.astype(int)  # float转int型


def to_nrrd(file_path, nii_nrrd_name, nrrd_name):  # file_path是dcm文件夹，nrrd_name是dcm的nrrd的文件名
    #     print('正在处理的文件夹为：',file_path)
    # 获取该文件下的所有序列ID，每个序列对应一个ID， 返回的series_IDs为一个列表
    global img
    path_nrrd = os.path.join(file_path, nii_nrrd_name)
    print('path_nrrd: ', path_nrrd, '\n')

    for filename in os.listdir(file_path):
        # print(filename)
        if filename.endswith(('nii', 'nii.gz')):  # 排除'kmeans2.nii.gz'
            nii_path = os.path.join(file_path, filename)
            print('nii_path: ', nii_path)
            img = sitk.ReadImage(nii_path)
            sitk.WriteImage(img, path_nrrd)

    nii_array = sitk.GetArrayFromImage(img)

    series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(file_path)
    # 查看该文件夹下的序列数量
    nb_series = len(series_IDs)
    print('该文件夹下的序列数量', nb_series, '\n')
    # 通过ID获取该ID对应的序列所有切片的完整路径， series_IDs[1]代表的是第二个序列的ID
    series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(file_path)

    # 新建一个ImageSeriesReader对象
    series_reader = sitk.ImageSeriesReader()
    # 通过之前获取到的序列的切片路径来读取该序列
    series_reader.SetFileNames(series_file_names)
    # 获取该序列对应的3D图像
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
    # print(pathlist)
    for dir_path in pathlist:
        print('现在处理的文件夹: ', dir_path)
        rest_num = rest_num - 1
        print('剩余人数： ', rest_num)
        # print(dir_path)
        to_nrrd(dir_path, nii_nrrd_name='nii_sitk1.nrrd', nrrd_name='voi_sitk1.nrrd')
