import numpy as np
import cv2

from filters import *
from manhwa_level import manhwa_level_image_crop_calculator
from print_level import print_level_image_crop_calculator


def get_image_attributes(image):
    """
    This function takes an image and returns the sum of the absolute differences between the pixels of the image.
    it's mainly used in the y_corrdinate_start function in manhwa_level.py
    :param image:
    :return:
    """
    diff = np.abs(np.diff(image, axis=1))
    diff_sum = np.sum(diff, axis=1)
    return diff_sum


def crop_and_collect_images(image_paths: list, column_height):
    """
    This function takes a list of image paths, applies several filters and cropping operations to each image,
    and then collects the cropped images into a list.

    Args:
        image_paths (list): A list of paths to the images to be processed.

    Returns:
        cropped_images (list): A list of cropped images. Each image is cropped based on the calculations
        from the manhwa_level_image_crop_calculator and print_level_image_crop_calculator functions,
        and filtered by the filter_small_images and filter_blank_images functions.

    Note:
        This function uses the OpenCV library for image processing.
        :param image_paths:
        :param column_height:
    """

    manhwa_crop_dict = {}
    all_crop_lists = []  # To collect all crop lists before passing to print_level_image_crop_calculator

    for image_path in image_paths:
        image = cv2.imread(image_path)
        image = remove_border_if_exists_filter(image)
        image = appropriate_size_filter(image)
        diff_sum = get_image_attributes(image)
        crop_list = manhwa_level_image_crop_calculator(image, diff_sum)
        crop_list = filter_small_images(crop_list)
        crop_list = filter_blank_images(crop_list, image)

        # Save both the image and the filtered crop list in the dictionary
        manhwa_crop_dict[image_path] = {"image": image, "crop_list": crop_list}

        # Add the filtered crop list to the aggregate list
        all_crop_lists.append(crop_list)

    # this is done separately to because print level image calculator needs all the images
    final_crop_list = print_level_image_crop_calculator(all_crop_lists, column_height)
    for index, (image_path, data) in enumerate(manhwa_crop_dict.items()):
        data["crop_list"] = final_crop_list[index]

    cropped_images = []
    for image_path, data in manhwa_crop_dict.items():
        image = data["image"]
        print_crop_list = data["crop_list"]
        for crop in print_crop_list:
            cropped_img = image[crop[0]:crop[1], 0:image.shape[1]]
            cropped_images.append(cropped_img)

    return cropped_images


def place_images_on_canvas(cropped_images, column_height):
    """
    This function places the cropped images on a canvas
    the canvas is A5 paper size, and split into 2 columns, each with a height length of 2360
    :param column_height:
    :param cropped_images:
    :return:
    """
    full_image = np.ones((int(2480), int(3508 / 2), 3), dtype=np.uint8) * 255
    start_x, start_y = 950, 60
    current_x, current_y = start_x, start_y
    images_placed = []
    for index, img in enumerate(cropped_images):
        h, w = img.shape[:2]
        full_image[current_y:current_y + h, current_x:current_x + w] = img
        current_y += h
        if current_y == column_height:
            if current_x == 950:
                current_x, current_y = 130, start_y
                current_x = 130
            elif current_x == 130:
                images_placed.append(full_image)
                current_x, current_y = start_x, start_y
                full_image = np.ones((int(2480), int(3508 / 2), 3), dtype=np.uint8) * 255
        if index == len(cropped_images) - 1:
            images_placed.append(full_image)
    return images_placed
