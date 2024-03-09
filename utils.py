from PIL import Image
import numpy as np

def skip_image_same_color(height, image_array, y_look_up_start, steps=10 ):
    diff = np.abs(np.diff(image_array, axis=1))
    diff_sum = np.sum(diff, axis=1)
    non_color_lines = np.where(diff_sum != 0)[0]
    number_of_same_color_lines = 0
    for y in range(y_look_up_start, height, steps):
        if y in non_color_lines:
            number_of_same_color_lines += 1
            if number_of_same_color_lines > 3:
                return y
    return y_look_up_start


def get_image_axies(image: Image, y_look_up_start=0):
    steps = 10
    image_array = np.array(image)
    y_coordinate_start = skip_image_same_color(image.height, image_array, y_look_up_start)
    if y_coordinate_start == y_look_up_start:
        return image.height
    for y in range(y_coordinate_start, image.height, steps):
        first_pixel_color = image_array[y, 0]
        if np.all(image_array[y] == first_pixel_color):
            return y
    return image.height

def image_crop_calculator(image: Image, y_coordinate_start=0):
    y_coordinate_start = get_image_axies(image, y_coordinate_start)
    if y_coordinate_start < image.height:
        image_crop_calculator(image, y_coordinate_start)
