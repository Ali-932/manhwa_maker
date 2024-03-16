def print_level_image_crop_calculator(manhwa_crop_list, column_height):
    '''
    This function takes a list of crop lists after being cut in the manhwa level. this function cut the cropped images based on the length of the column,
    so whenver an images is over the length of the column it crop it and insert the cropped part into the list.
    :param manhwa_crop_list:
    :param column_height:
    :return:
    '''
    side_length = 0
    for image in manhwa_crop_list:
        for i, cut_pixels in enumerate(image):
            side_length += cut_pixels[1] - cut_pixels[0]
            if side_length > column_height:
                cut_pixels = (
                    cut_pixels[0],
                    cut_pixels[0] + column_height - (side_length - (cut_pixels[1] - cut_pixels[0]))
                )
                old_cut_pixels = image[i]
                image[i] = cut_pixels

                side_length = 0
                image.insert(i + 1, (image[i][1], old_cut_pixels[1]))
    return manhwa_crop_list
