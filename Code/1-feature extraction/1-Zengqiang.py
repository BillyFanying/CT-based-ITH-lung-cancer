import os
import numpy as np
import pydicom
import cv2
import random
from pathlib import Path
import matplotlib.pyplot as plt
from scipy import ndimage


def create_medical_augmentation(input_dir, output_dir, preserve_original=True):
    """
    创建医学图像友好的数据增强

    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        preserve_original: 是否保留原始图像
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)

    # 更温和的增强方法
    def rotate_image(image, angle_range=(-5, 5)):
        """轻微旋转"""
        angle = random.uniform(angle_range[0], angle_range[1])
        return ndimage.rotate(image, angle, reshape=False, mode='reflect')

    def adjust_brightness(image, factor_range=(0.95, 1.05)):
        """轻微亮度调整"""
        factor = random.uniform(factor_range[0], factor_range[1])
        return np.clip(image * factor, image.min(), image.max())

    def adjust_contrast(image, factor_range=(0.95, 1.05)):
        """轻微对比度调整"""
        factor = random.uniform(factor_range[0], factor_range[1])
        mean = np.mean(image)
        return np.clip(mean + factor * (image - mean), image.min(), image.max())

    def add_gaussian_noise(image, sigma_range=(0.5, 2)):
        """添加轻微高斯噪声"""
        sigma = random.uniform(sigma_range[0], sigma_range[1])
        noise = np.random.normal(0, sigma, image.shape)
        noisy_image = image + noise
        return np.clip(noisy_image, image.min(), image.max())

    def translate_image(image, shift_range=(-2, 2)):
        """轻微平移"""
        dx = random.randint(shift_range[0], shift_range[1])
        dy = random.randint(shift_range[0], shift_range[1])

        M = np.float32([[1, 0, dx], [0, 1, dy]])
        rows, cols = image.shape
        return cv2.warpAffine(image, M, (cols, rows), borderMode=cv2.BORDER_REFLECT)

    def zoom_image(image, zoom_range=(0.98, 1.02)):
        """轻微缩放"""
        zoom_factor = random.uniform(zoom_range[0], zoom_range[1])
        h, w = image.shape
        new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)

        # 调整大小
        zoomed = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # 裁剪或填充到原始尺寸
        if zoom_factor > 1:
            # 从中心裁剪
            start_h = (new_h - h) // 2
            start_w = (new_w - w) // 2
            return zoomed[start_h:start_h + h, start_w:start_w + w]
        else:
            # 填充
            pad_h = (h - new_h) // 2
            pad_w = (w - new_w) // 2
            padded = np.zeros_like(image)
            padded[pad_h:pad_h + new_h, pad_w:pad_w + new_w] = zoomed
            return padded

    def elastic_transform(image, alpha=10, sigma=4):
        """弹性变换（轻微）"""
        random_state = np.random.RandomState(None)
        shape = image.shape

        dx = random_state.rand(*shape) * 2 - 1
        dy = random_state.rand(*shape) * 2 - 1

        dx = cv2.GaussianBlur(dx, (sigma, sigma), 0) * alpha
        dy = cv2.GaussianBlur(dy, (sigma, sigma), 0) * alpha

        x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
        indices = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1))

        distorted = ndimage.map_coordinates(image, indices, order=1, mode='reflect')
        return distorted.reshape(image.shape)

    # 定义增强组合
    augmentation_methods = {
        'original': lambda img: img,
        'rotation': rotate_image,
        'brightness': adjust_brightness,
        'contrast': adjust_contrast,
        'gaussian_noise': add_gaussian_noise,
        'translation': translate_image,
        'zoom': zoom_image,
        'elastic': lambda img: elastic_transform(img, alpha=5, sigma=3)  # 轻微弹性变换
    }

    # 处理所有DICOM文件
    processed_count = 0

    # 支持的文件扩展名
    valid_extensions = ['.dcm', '.DCM', '.ima', '.IMA']

    for root, dirs, files in os.walk(input_dir):
        # 在输入目录结构中查找DICOM文件
        dicom_files = []
        for ext in valid_extensions:
            dicom_files.extend(Path(root).glob(f'*{ext}'))

        if not dicom_files:
            continue

        # 创建对应的输出目录结构
        relative_path = Path(root).relative_to(input_path)
        patient_study_path = relative_path

        print(f"处理目录: {relative_path}")

        for file_path in dicom_files:
            try:
                # 读取DICOM文件
                dicom = pydicom.dcmread(str(file_path))

                # 检查是否包含像素数据
                if not hasattr(dicom, 'pixel_array'):
                    continue

                # 获取像素数据
                image = dicom.pixel_array.astype(np.float32)

                # 归一化到0-255范围（保持原始对比度）
                if image.max() > image.min():
                    image = (image - image.min()) / (image.max() - image.min()) * 255
                else:
                    image = np.zeros_like(image)

                # 转换为8位（用于显示和处理）
                image_8bit = image.astype(np.uint8)

                # 应用每种增强方法
                for aug_name, aug_func in augmentation_methods.items():
                    if aug_name == 'original' and not preserve_original:
                        continue

                    # 创建输出目录
                    aug_output_dir = output_path / patient_study_path / aug_name
                    aug_output_dir.mkdir(parents=True, exist_ok=True)

                    # 应用增强
                    if aug_name == 'original':
                        aug_image = image_8bit
                    else:
                        aug_image = aug_func(image_8bit.copy())

                    # 确保数据类型正确
                    if aug_image.dtype != np.uint8:
                        aug_image = aug_image.astype(np.uint8)

                    # 创建新的DICOM文件
                    new_dicom = dicom.copy()

                    # 更新像素数据
                    if aug_image.dtype != new_dicom.pixel_array.dtype:
                        # 如果需要，转换回原始数据类型
                        aug_image = aug_image.astype(new_dicom.pixel_array.dtype)

                    # 更新DICOM元数据
                    new_dicom.PixelData = aug_image.tobytes()
                    new_dicom.Rows, new_dicom.Columns = aug_image.shape

                    # 添加增强信息到DICOM标签（修复了MultiValue与list加法问题，提升了鲁棒性）
                    if aug_name != 'original':
                        # 修复核心：先将MultiValue转换为普通list，处理空值情况，再拼接
                        original_image_type = list(dicom.ImageType) if dicom.ImageType else []
                        new_dicom.ImageType = original_image_type + ['DERIVED', 'SECONDARY']

                        if hasattr(new_dicom, 'SeriesDescription'):
                            new_dicom.SeriesDescription = f"{dicom.SeriesDescription} - {aug_name}"
                        else:
                            new_dicom.SeriesDescription = aug_name

                    # 生成输出文件名
                    if aug_name == 'original':
                        output_filename = file_path.name
                    else:
                        output_filename = f"{file_path.stem}_{aug_name}.dcm"

                    # 保存文件
                    output_file = aug_output_dir / output_filename
                    new_dicom.save_as(str(output_file))

                    processed_count += 1

                    # 每处理100个文件打印进度
                    if processed_count % 100 == 0:
                        print(f"已处理 {processed_count} 个文件...")

            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {e}")
                continue

    print(f"\n数据增强完成！")
    print(f"总共处理了 {processed_count} 个增强文件")
    print(f"增强后的数据保存在: {output_dir}")

    # 显示示例图像
    show_example_images(output_dir)


def show_example_images(output_dir, num_examples=3):
    """显示增强前后的示例图像"""
    output_path = Path(output_dir)

    # 查找原始和增强的文件夹
    aug_folders = []
    for item in output_path.rglob('*'):
        if item.is_dir():
            if any(aug in item.name for aug in ['original', 'rotation', 'brightness', 'noise']):
                aug_folders.append(item)

    if not aug_folders:
        print("未找到增强文件夹")
        return

    # 从每个文件夹获取示例图像
    example_images = {}
    for folder in aug_folders[:5]:  # 最多显示5种增强
        dicom_files = list(folder.glob('*.dcm'))
        if dicom_files:
            try:
                dicom = pydicom.dcmread(str(dicom_files[0]))
                image = dicom.pixel_array
                # 归一化显示
                if image.max() > image.min():
                    image = (image - image.min()) / (image.max() - image.min())
                example_images[folder.name] = image
            except:
                pass

    # 显示图像
    if example_images:
        fig, axes = plt.subplots(1, len(example_images), figsize=(15, 4))
        if len(example_images) == 1:
            axes = [axes]

        for (name, image), ax in zip(example_images.items(), axes):
            ax.imshow(image, cmap='gray', vmin=0, vmax=1)
            ax.set_title(name)
            ax.axis('off')

        plt.tight_layout()
        plt.show()


def verify_augmentation_quality(input_dir, output_dir):
    """验证增强质量"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # 计算原始和增强图像的相似度
    original_images = []
    augmented_images = []

    # 收集图像
    for orig_file in input_path.rglob('*.dcm'):
        try:
            orig_dicom = pydicom.dcmread(str(orig_file))
            orig_image = orig_dicom.pixel_array
            original_images.append(orig_image)
        except:
            pass

    for aug_file in output_path.rglob('*_*.dcm'):
        try:
            aug_dicom = pydicom.dcmread(str(aug_file))
            aug_image = aug_dicom.pixel_array
            augmented_images.append(aug_image)
        except:
            pass

    if original_images and augmented_images:
        # 计算平均相似度
        from skimage.metrics import structural_similarity as ssim

        sample_pairs = min(10, len(original_images), len(augmented_images))
        ssim_scores = []

        for i in range(sample_pairs):
            orig = original_images[i].astype(np.float32)
            aug = augmented_images[i].astype(np.float32)

            # 归一化
            orig = (orig - orig.min()) / (orig.max() - orig.min() + 1e-8)
            aug = (aug - aug.min()) / (aug.max() - aug.min() + 1e-8)

            # 计算SSIM
            score = ssim(orig, aug, data_range=1.0)
            ssim_scores.append(score)

        avg_ssim = np.mean(ssim_scores)
        print(f"增强质量评估:")
        print(f"样本数量: {sample_pairs}")
        print(f"平均结构相似性(SSIM): {avg_ssim:.4f}")
        print(f"增强强度: {'轻微' if avg_ssim > 0.95 else '适中' if avg_ssim > 0.85 else '强烈'}")

        return avg_ssim
    return None


if __name__ == "__main__":
    # 设置路径
    input_folder = "E:/Mouse/MT/test"  # 替换为您的数据路径
    output_folder = "E:/Mouse/MT/zengqiang"

    # 执行增强
    create_medical_augmentation(input_folder, output_folder)

    # 验证增强质量
    verify_augmentation_quality(input_folder, output_folder)