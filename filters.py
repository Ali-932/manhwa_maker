import cv2
import numpy as np


def filter_blank_images(manhwa_crop_list, image, std_dev_threshold=10):
    """
    This function filters out blank images from a list of cropped images. An image is considered blank if the standard
    deviation of its pixel values is less than a specified threshold.

    Args:
        manhwa_crop_list (list): A list of tuples, where each tuple contains the start and end y-coordinates for a crop.
        image (np.array): The original image from which the crops were taken.
        std_dev_threshold (int, optional): The standard deviation threshold below which an image is considered blank. Defaults to 10.

    Returns:
        list: A list of tuples, where each tuple contains the start and end y-coordinates for a non-blank crop.
    """

    # Load the image
    filtered_crops = []

    for cut_pixels in manhwa_crop_list:
        cropped_image = image[cut_pixels[0]:cut_pixels[1], :]
        std_dev = np.std(cropped_image)
        is_blank = std_dev < std_dev_threshold
        if not is_blank:
            filtered_crops.append(cut_pixels)

    return filtered_crops


def filter_small_images(crop_list, min_height=35):
    '''
    This function filters out small images from a list of cropped images.
     An image is considered small if its height is less than a specified threshold.
    :param crop_list:
    :param min_height:
    :return:
    '''
    filtered_crops = []
    for cut_pixels in crop_list:
        if (cut_pixels[1] - cut_pixels[0]) >= min_height:
            filtered_crops.append(cut_pixels)
    return filtered_crops


def appropriate_size_filter(image, target_width=804):
    '''
    This function resizes an image to a target width if its width is greater than the target width.
    :param image:
    :param target_width:
    :return:
    '''
    (h, w) = image.shape[:2]
    if w < target_width:
        return image

    ratio = target_width / float(w)

    # Calculate the new height based on the aspect ratio
    target_height = int(h * ratio)

    # Resize the image to the target dimensions
    resized_image = cv2.resize(image, (target_width, target_height))
    return resized_image


def remove_border_if_exists_filter(image, offset=5):
    """
    This function checks if an image has a border and removes it if it exists.
    It first converts the image to grayscale and then to binary.
    It then finds the contours of the binary image and identifies the leftmost and rightmost contours.
    If these contours are at the edges of the image, it means the image has a border.
    In this case, the function returns the original image.
    If the contours are not at the edges, it means the image does not have a border.
    In this case, the function crops the image to remove the border and returns the cropped image.

    Args:
        image (np.array): The input image.
        offset (int, optional): The offset to use when cropping the image. Defaults to 5.

    Returns:
        np.array: The image with the border removed if it exists, otherwise the original image.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Get the leftmost and rightmost contours
    leftmost_contour = min(contours, key=lambda c: c[:, 0, 0].min())
    rightmost_contour = max(contours, key=lambda c: c[:, 0, 0].max())

    lx, ly, lw, lh = cv2.boundingRect(leftmost_contour)
    rx, ry, rw, rh = cv2.boundingRect(rightmost_contour)

    if lx == 0 and lx + lw == image.shape[1]:  # Check for left border
        return image
    elif rx == 0 and rx + rw == image.shape[1]:  # Check for right border
        return image
    else:
        cropped_image = image[:, max(lx + offset, 0):min(rx + rw - offset, image.shape[1])]
        return cropped_image
