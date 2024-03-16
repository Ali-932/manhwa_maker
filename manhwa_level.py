import numpy as np


def get_y_coordinate_start(y_look_up_start, diff_sum, steps=5, max_color_lines=3):
    '''
    This function returns the y-coordinate where the image starts
    it uses the diff_sum to find the y-coordinate where the image starts
    :param y_look_up_start:
    :param diff_sum:
    :param steps:
    :param max_color_lines: how many colored lines are allowed before the image starts
    :return:
    '''
    non_color_lines = np.where(diff_sum != 0)[0]
    number_of_same_color_lines = 0
    start_index = np.searchsorted(non_color_lines, y_look_up_start)
    for y in non_color_lines[start_index::steps]:
        number_of_same_color_lines += 1
        if number_of_same_color_lines > max_color_lines:
            return max(y_look_up_start, y)
    return y_look_up_start


def get_y_coordinate_end(height, image_array, y_coordinate_start, steps=5, offset=10):
    '''
    This function returns the y-coordinate where the image ends
    it has an offset for color to avoid gradient color and some borders not detected
    it also checks for the percentage of the same color in the image, with a threshold of 99.5%
    :param height:
    :param image_array:
    :param y_coordinate_start:
    :param steps:
    :return:
    '''
    for y in range(y_coordinate_start, height, steps):
        first_pixel_color = image_array[y, 0]
        upper_bounds = []
        lower_bounds = []

        for color in first_pixel_color:
            upper = min(255, color + offset)
            lower = max(0, color - offset)
            upper_bounds.append(upper)
            lower_bounds.append(lower)

        # Convert lists to arrays for comparison
        upper_bounds = np.array(upper_bounds)
        lower_bounds = np.array(lower_bounds)

        condition = np.logical_and(
            image_array[y] >= lower_bounds,
            image_array[y] <= upper_bounds
        )
        channel_wise_condition = np.all(condition, axis=-1)

        true_percentage = np.mean(channel_wise_condition) * 100

        if true_percentage > 99.5:
            return y
    return height


def get_image_axies(image, diff_sum, y_look_up_start=0):
    '''
    This function returns the y-coordinate where the image starts and ends
    :param image:
    :param diff_sum:
    :param y_look_up_start:
    :return:
    '''
    y_coordinate_start = get_y_coordinate_start(y_look_up_start, diff_sum)
    if y_coordinate_start == y_look_up_start:
        return image.shape[0], y_coordinate_start
    y_coordinate_end = get_y_coordinate_end(image.shape[0], image, y_coordinate_start)
    return y_coordinate_end, y_coordinate_start


def manhwa_level_image_crop_calculator(image, diff_sum, y_coordinate_end=0, image_crop_list=None):
    '''
    This function calculates the cropping coordinates for an image at the manhwa level.
    It uses a recursive approach to find the start and end y-coordinates for each crop,
    and appends these coordinates to the image_crop_list.

    Args:
        image (np.array): The input image to be cropped.
        diff_sum (np.array): The sum of absolute differences between adjacent pixels in the image.
        y_coordinate_end (int, optional): The y-coordinate where the last crop ended. Defaults to 0.
        image_crop_list (list, optional): A list to store the cropping coordinates. Defaults to None.

    Returns:
        list: A list of tuples, where each tuple contains the start and end y-coordinates for a crop.
    '''
    if image_crop_list is None:
        image_crop_list = []
    y_coordinate_end, y_coordinate_start = get_image_axies(image, diff_sum, y_look_up_start=y_coordinate_end)
    image_crop_list.append(tuple((max(0, y_coordinate_start), y_coordinate_end)))
    if y_coordinate_end < image.shape[0]:
        return manhwa_level_image_crop_calculator(image, diff_sum, y_coordinate_end, image_crop_list)
    else:
        return image_crop_list
