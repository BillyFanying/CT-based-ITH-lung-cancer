import os, math
import numpy as np
import nibabel as nib
import json
import pandas as pd
from nibabel.testing import data_path
import matplotlib.pyplot as plt
from skimage import measure, draw
import SimpleITK as sitk

Errorlis = []
Ecnt = 0


class spacing_not_equal(Exception):  ##继承异常的类
    def __init__(self):
        print("nii文件spaing的 x和y 不一致，需重新编写代码")


#  2.手动抛出用户自定义类型异常
def if_spacing_equal(x, y):
    flag = (x == y)
    if not flag:  # 如果nii文件的spacing 的x和y不想当，抛出错误
        raise spacing_not_equal()  # 抛出异常很简单，使用raise即可,但是没有处理，即捕捉  ##直接打印出来
    else:
        pass


def expansion_mm(nii_path, expan_num):
    img = nib.load(nii_path)
    img_data = img.get_fdata()
    [img_x, img_y, img_num] = img_data.shape

    img_minus = np.zeros((img_x, img_y, img_num))  # 仅外扩部分的矩阵
    img_expan = np.zeros((img_x, img_y, img_num))  # 复制一份img_data用于保存原图像+外扩部分
    count_nii = 0
    while count_nii < img_num:
        #         nii_matrix[:, :, count_nii] = np.transpose(img_arr[:, :, count_nii])  # 转置
        img_expan[:, :, count_nii] = img_data[:, :, count_nii]
        count_nii = count_nii + 1

    for num in range(img_num):
        img_tmp = img_data[:, :, num].reshape((img_x, img_y))  # 三维矩阵变为二维
        if (img_tmp.max()):
            contours = measure.find_contours(img_tmp, 0.5)  # 找出轮廓，返回轮廓列表集合，可用for循环取出每一条轮廓。
            #             for contour in contours:
            for contour_x, contour_y in contours[0]:
                # skimage.draw.circle(r, c, radius, shape=None) r，c：圆的中心坐标。半径：圆的半径。
                rr, cc = draw.ellipse(contour_x, contour_y, expan_num, expan_num)  # 外扩,  rr，cc：像素坐标。
                img_expan[rr, cc, num] = 1

    return img_expan
    # return img_minus


def expansion(nii_path, mm_num):  # 输入为路径和毫米##具体外扩

    img = nib.load(nii_path)
    img_data = img.get_fdata()
    [img_x, img_y, img_num] = img_data.shape
    # nii为0和1，找轮廓，轮廓上的点画圆，  xyz都有spacing两个像素点实际物理距离，0.1mm还是0.2mm
    # 判断spacing
    file = sitk.ReadImage(nii_path)
    spacing = file.GetSpacing()  # 读取该数据的spacing
    [x_spacing, y_spacing, z_spacing] = spacing
    if_spacing_equal(x_spacing, y_spacing)  # spacing 的x和y应该一致，如果不一致，不能用画圆的方法外扩了，需要重新编写外扩部分赋值的代码
    expan_num = math.ceil(mm_num / x_spacing)  # 向上取整外扩的像素数目，如果：外扩5mm除spacing
    # 画圆 赋值
    img_minus = np.zeros((img_x, img_y, img_num))  # 仅外扩部分的矩阵
    img_expan = np.zeros((img_x, img_y, img_num))  # 复制一份img_data用于保存原图像+外扩部分

    count_nii = 0
    while count_nii < img_num:  # 赋值 img_num 为一共多少张nii
        img_expan[:, :, count_nii] = img_data[:, :, count_nii]
        count_nii = count_nii + 1
    for num in range(img_num):  ###循环每一张nii图像 ##找出轮廓，轮廓上的每个点画圆
        img_tmp = img_data[:, :, num].reshape((img_x, img_y))  # 三维矩阵变为二维
        # print(img_tmp)
        if (img_tmp.max()):
            contours = measure.find_contours(img_tmp, 0.5)  # 找出轮廓，返回轮廓列表集合，可用for循环取出每一条轮廓。##500多个点数据点返回

            for contour_x, contour_y in contours[0]:
                # print("8")
                # skimage.draw.circle(r, c, radius, shape=None) r，c：圆的中心坐标。半径：圆的半径。
                rr, cc = draw.ellipse(contour_x, contour_y, expan_num, expan_num)  # 外扩,  rr，cc：像素坐标。
                img_expan[rr, cc, num] = 1  ##赋值为1
                # print("7")

            img_minus[:, :, num] = img_expan[:, :, num] - img_data[:, :, num]  # 矩阵相减，仅仅留下外扩部分

    print("成功外扩")
    return img_expan  # 返回原图+扩充部分的矩阵


##nii有三个部分：header aff和data
def save_new_nii(nii_path, new_nii_path, mm_num):
    # image_data = img.get_fdata()
    # expan_data = expansion(nii_path,mm_num = mm_num)#返回外扩三维矩阵
    expan_data = expansion_mm(nii_path, expan_num=5)  # 返回外扩三维矩阵
    print("成功加载expand_data")
    img = nib.load(nii_path)  # 读进来
    header = img.header  # 头文件
    affine = img.affine  #
    expan_img = nib.Nifti1Image(expan_data, affine=affine, header=header)  # 新建对象： nii文件，
    print("成功加载expend_img")
    nib.save(expan_img, new_nii_path)
    print("成功加载nib_save")

    img1 = sitk.ReadImage(new_nii_path)
    sitk.WriteImage(img1, new_nii_path.replace('nii.gz', 'nrrd'))


if __name__ == '__main__':

    df_xlsx = pd.read_excel('I:/EGFR19 vs 21/EGFR_Primary/segmentation/T2W.xlsx')
    pathlist = df_xlsx['path']
    Ccnt = 0
    cnt = 0
    count = 1
    # pathlist = ['E:\BAI_GUANG_CHAO_MR171211039_head\T1_C']
    for path_patient in pathlist:
        cnt += 1
        print("正在处理第：", cnt, "个样本")
        print("路径为:", path_patient)

        PathDicom = path_patient
        subdirnii = os.listdir(PathDicom)
        for niinum in subdirnii:
            # if filename.endswith(('nii', 'nii.gz')):
            if niinum.__contains__('nii.gz') or niinum.__contains__('.nii'):
                nii_path = os.path.join(PathDicom, niinum)
                print(nii_path)
                new_nii_path = os.path.dirname(nii_path) + r'\nii5.nii.gz'
                print(count, new_nii_path)
                count = count + 1

                try:
                    save_new_nii(nii_path, new_nii_path, mm_num=5)  # mm_num：外扩多少mm，***必须大于0***

                    Ccnt += 1
                except IndexError:
                    Errorlis.append(path_patient)
                    Ecnt += 1

                    print("第", Ecnt, "个错误样例")
                    pass
                continue

    print(Errorlis)

pass


def expansion_mm(img_data, expan_num):
    [img_x, img_y, img_num] = img_data.shape

    img_minus = np.zeros((img_x, img_y, img_num))  # 仅外扩部分的矩阵
    img_expan = np.zeros((img_x, img_y, img_num))  # 复制一份img_data用于保存原图像+外扩部分
    count_nii = 0
    while count_nii < img_num:
        #         nii_matrix[:, :, count_nii] = np.transpose(img_arr[:, :, count_nii])  # 转置
        img_expan[:, :, count_nii] = img_data[:, :, count_nii]
        count_nii = count_nii + 1

    for num in range(img_num):
        img_tmp = img_data[:, :, num].reshape((img_x, img_y))  # 三维矩阵变为二维
        if (img_tmp.max()):
            contours = measure.find_contours(img_tmp, 0.5)  # 找出轮廓，返回轮廓列表集合，可用for循环取出每一条轮廓。
            #             for contour in contours:
            for contour_x, contour_y in contours[0]:
                # skimage.draw.circle(r, c, radius, shape=None) r，c：圆的中心坐标。半径：圆的半径。
                rr, cc = draw.ellipse(contour_x, contour_y, expan_num, expan_num)  # 外扩,  rr，cc：像素坐标。
                img_expan[rr, cc, num] = 1

            img_minus[:, :, num] = img_expan[:, :, num] - img_data[:, :, num]  # 矩阵相减，仅仅留下外扩部分

    return img_minus  # 返回仅扩充部分的矩阵


def expansion1(nii_path, mm_num):  # 输入为路径和毫米##具体外扩

    img = nib.load(nii_path)
    # print(img)
    img_data = img.get_fdata()
    # print(img_data)
    [img_x, img_y, img_num] = img_data.shape
    # print("1")

    # nii为0和1，找轮廓，轮廓上的点画圆，  xyz都有spacing两个像素点实际物理距离，0.1mm还是0.2mm
    # 判断spacing
    file = sitk.ReadImage(nii_path)

    spacing = file.GetSpacing()  # 读取该数据的spacing
    [x_spacing, y_spacing, z_spacing] = spacing
    if_spacing_equal(x_spacing, y_spacing)  # spacing 的x和y应该一致，如果不一致，不能用画圆的方法外扩了，需要重新编写外扩部分赋值的代码
    expan_num = math.ceil(mm_num / x_spacing)  # 向上取整外扩的像素数目，如果：外扩5mm除spacing

    img_minus = np.zeros((img_x, img_y, img_num))  # 仅外扩部分的矩阵
    img_expan = np.zeros((img_x, img_y, img_num))  # 复制一份img_data用于保存原图像+外扩部分

    count_nii = 0
    while count_nii < img_num:  # 赋值 img_num 为一共多少张nii

        img_expan[:, :, count_nii] = img_data[:, :, count_nii]
        count_nii = count_nii + 1

    for num in range(img_num):  ###循环每一张nii图像 ##找出轮廓，轮廓上的每个点画圆
        img_tmp = img_data[:, :, num].reshape((img_x, img_y))  # 三维矩阵变为二维

        if (img_tmp.max()):
            contours = measure.find_contours(img_tmp, 0.5)  # 找出轮廓，返回轮廓列表集合，可用for循环取出每一条轮廓。##500多个点数据点返回

            for contour_x, contour_y in contours[0]:
                rr, cc = draw.ellipse(contour_x, contour_y, expan_num, expan_num)  # 外扩,  rr，cc：像素坐标。
                img_expan[rr, cc, num] = 1  ##赋值为1
                # print("7")

            img_minus[:, :, num] = img_expan[:, :, num] - img_data[:, :, num]  # 矩阵相减，仅仅留下外扩部分

    print("成功外扩")
    return img_expan  # 返回原图+扩充部分的矩阵
