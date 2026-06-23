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


class spacing_not_equal(Exception):  # Inherit Exception class
    def __init__(self):
        print("Nifti file spacing x and y do not match, code adjustment required")


# Manually raise custom exception
def if_spacing_equal(x, y):
    flag = (x == y)
    if not flag:
        raise spacing_not_equal()
    else:
        pass


def expansion_mm(nii_path, expan_num):
    img = nib.load(nii_path)
    img_data = img.get_fdata()
    [img_x, img_y, img_num] = img_data.shape

    img_minus = np.zeros((img_x, img_y, img_num))  # Matrix for dilated region only
    img_expan = np.zeros((img_x, img_y, img_num))  # Copy image data to hold original + dilated regions
    count_nii = 0
    while count_nii < img_num:
        img_expan[:, :, count_nii] = img_data[:, :, count_nii]
        count_nii = count_nii + 1

    for num in range(img_num):
        img_tmp = img_data[:, :, num].reshape((img_x, img_y))
        if (img_tmp.max()):
            contours = measure.find_contours(img_tmp, 0.5)  # Find contours
            for contour_x, contour_y in contours[0]:
                rr, cc = draw.ellipse(contour_x, contour_y, expan_num, expan_num)  # Dilated region pixel coordinates
                img_expan[rr, cc, num] = 1

    return img_expan


def expansion(nii_path, mm_num):  # Specific dilation implementation
    img = nib.load(nii_path)
    img_data = img.get_fdata()
    [img_x, img_y, img_num] = img_data.shape
    file = sitk.ReadImage(nii_path)
    spacing = file.GetSpacing()  # Get voxel spacing
    [x_spacing, y_spacing, z_spacing] = spacing
    if_spacing_equal(x_spacing, y_spacing)
    expan_num = math.ceil(mm_num / x_spacing)  # Ceil pixel count for physical millimeter distance
    img_minus = np.zeros((img_x, img_y, img_num))
    img_expan = np.zeros((img_x, img_y, img_num))

    count_nii = 0
    while count_nii < img_num:
        img_expan[:, :, count_nii] = img_data[:, :, count_nii]
        count_nii = count_nii + 1
    for num in range(img_num):
        img_tmp = img_data[:, :, num].reshape((img_x, img_y))
        if (img_tmp.max()):
            contours = measure.find_contours(img_tmp, 0.5)

            for contour_x, contour_y in contours[0]:
                rr, cc = draw.ellipse(contour_x, contour_y, expan_num, expan_num)
                img_expan[rr, cc, num] = 1

            img_minus[:, :, num] = img_expan[:, :, num] - img_data[:, :, num]

    print("Successfully dilated")
    return img_expan  # Returns original + dilated matrix


# NIfTI consists of header, affine, and data
def save_new_nii(nii_path, new_nii_path, mm_num):
    expan_data = expansion_mm(nii_path, expan_num=5)  # Returns dilated 3D matrix
    print("expand_data successfully loaded")
    img = nib.load(nii_path)
    header = img.header
    affine = img.affine
    expan_img = nib.Nifti1Image(expan_data, affine=affine, header=header)
    print("expend_img successfully loaded")
    nib.save(expan_img, new_nii_path)
    print("nib_save successfully executed")

    img1 = sitk.ReadImage(new_nii_path)
    sitk.WriteImage(img1, new_nii_path.replace('nii.gz', 'nrrd'))


if __name__ == '__main__':
    df_xlsx = pd.read_excel('I:/EGFR19 vs 21/EGFR_Primary/segmentation/T2W.xlsx')
    pathlist = df_xlsx['path']
    Ccnt = 0
    cnt = 0
    count = 1
    for path_patient in pathlist:
        cnt += 1
        print("Processing sample: ", cnt)
        print("Path:", path_patient)

        PathDicom = path_patient
        subdirnii = os.listdir(PathDicom)
        for niinum in subdirnii:
            if niinum.__contains__('nii.gz') or niinum.__contains__('.nii'):
                nii_path = os.path.join(PathDicom, niinum)
                print(nii_path)
                new_nii_path = os.path.dirname(nii_path) + r'\nii5.nii.gz'
                print(count, new_nii_path)
                count = count + 1

                try:
                    save_new_nii(nii_path, new_nii_path, mm_num=5)  # mm_num: dilation distance, must be > 0

                    Ccnt += 1
                except IndexError:
                    Errorlis.append(path_patient)
                    Ecnt += 1

                    print("Error sample number: ", Ecnt)
                    pass
                continue

    print(Errorlis)

pass


def expansion_mm(img_data, expan_num):
    [img_x, img_y, img_num] = img_data.shape

    img_minus = np.zeros((img_x, img_y, img_num))
    img_expan = np.zeros((img_x, img_y, img_num))
    count_nii = 0
    while count_nii < img_num:
        img_expan[:, :, count_nii] = img_data[:, :, count_nii]
        count_nii = count_nii + 1

    for num in range(img_num):
        img_tmp = img_data[:, :, num].reshape((img_x, img_y))
        if (img_tmp.max()):
            contours = measure.find_contours(img_tmp, 0.5)
            for contour_x, contour_y in contours[0]:
                rr, cc = draw.ellipse(contour_x, contour_y, expan_num, expan_num)
                img_expan[rr, cc, num] = 1

            img_minus[:, :, num] = img_expan[:, :, num] - img_data[:, :, num]

    return img_minus  # Returns dilated region only


def expansion1(nii_path, mm_num):
    img = nib.load(nii_path)
    img_data = img.get_fdata()
    [img_x, img_y, img_num] = img_data.shape
    file = sitk.ReadImage(nii_path)

    spacing = file.GetSpacing()
    [x_spacing, y_spacing, z_spacing] = spacing
    if_spacing_equal(x_spacing, y_spacing)
    expan_num = math.ceil(mm_num / x_spacing)

    img_minus = np.zeros((img_x, img_y, img_num))
    img_expan = np.zeros((img_x, img_y, img_num))

    count_nii = 0
    while count_nii < img_num:
        img_expan[:, :, count_nii] = img_data[:, :, count_nii]
        count_nii = count_nii + 1

    for num in range(img_num):
        img_tmp = img_data[:, :, num].reshape((img_x, img_y))

        if (img_tmp.max()):
            contours = measure.find_contours(img_tmp, 0.5)

            for contour_x, contour_y in contours[0]:
                rr, cc = draw.ellipse(contour_x, contour_y, expan_num, expan_num)
                img_expan[rr, cc, num] = 1

            img_minus[:, :, num] = img_expan[:, :, num] - img_data[:, :, num]

    print("Successfully dilated")
    return img_expan
