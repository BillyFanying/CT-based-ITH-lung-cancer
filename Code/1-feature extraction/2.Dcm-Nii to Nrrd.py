import SimpleITK as sitk
import numpy as np
import nrrd
import os
import json


def get_file_name(path):
    with open("E:\\Mouse\\Mouse.json", 'r') as load_f:   #C:\Users\Administrator\Desktop\Aliyun\EGFR_data
        pathlist = json.load(load_f)
        print(pathlist)

    return (pathlist)


def to_nrrd(pathlist):
    for file_path in pathlist:
        # dicom文件所在的文件夹目录
        Modality = file_path.split(os.path.sep)[-1]
        print('正在处理的序列是' + str(Modality))
        PathDicom = file_path
        print('正在处理的文件夹为：' + str(file_path))
        # 要保存的dcm_nrrd的路径
        path_dcm_nrrd = os.path.join(PathDicom, '%s_dcm.nrrd' % Modality)

        # 获取该文件下的所有序列ID，每个序列对应一个ID， 返回的series_IDs为一个列表
        series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(file_path)
        # 查看该文件夹下的序列数量
        nb_series = len(series_IDs)
        print('该文件夹下的序列数量', nb_series)

        ###输出dcm名字
        series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(file_path)
        for series_file_names_num in series_file_names:
            print(series_file_names_num)

        # 新建一个ImageSeriesReader对象
        series_reader = sitk.ImageSeriesReader()
        # 通过之前获取到的序列的切片路径来读取该序列
        series_reader.SetFileNames(series_file_names)
        # 获取该序列对应的3D图像
        image3D = series_reader.Execute()

        # 查看该3D图像的尺寸
        print('3D图像的尺寸', image3D.GetSize(), '\n')  # GetSize()方法可用于获取SimpleITK对象的三个维度大小#3D图像的尺寸 (640, 512, 20) x,y,z

        # img = sitk.GetArrayFromImage(image3D)# GetArrayFromImage()可用于将SimpleITK对象转换为ndarray像素矩阵 SimpleITK读取的图像数据的坐标顺序坐标顺序是z, y, x，即从多少张切片到单张切片的宽和高；
        sitk.WriteImage(image3D, path_dcm_nrrd)  # 一句话dcm转nrrd

        # 获取nii路径
        subdir1 = os.listdir(PathDicom)
        for subdir1_num in subdir1:
             if subdir1_num.endswith('gz') or subdir1_num.endswith('nii'):#if subdir1_num.endswith('ex2.nii.gz') :#
                nii_path = os.path.join(PathDicom, subdir1_num)
                print(nii_path)
                nii = sitk.ReadImage(nii_path)
                # nii 要保存的 nrrd 文件路径
                path_nii_nrrd = os.path.join(PathDicom, '%s_nii.nrrd' % Modality)
                sitk.WriteImage(nii, path_nii_nrrd)  # nii 转化为nrrd    sitk.WriteImage(new_image, save_filename)


if __name__ == '__main__':
    path = r'E://Mouse'
    pathlist = get_file_name(path)
    to_nrrd(pathlist)
