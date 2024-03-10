import numpy as np
import cv2


# import cProfile
# cProfile.run('image_crop_calculator(image)')

def get_y_coordinate_start(height, image_array, y_look_up_start, steps=5):
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


def get_y_coordinate_end(height, image_array, y_coordinate_start, steps=5):
    for y in range(y_coordinate_start, height, steps):
        first_pixel_color = image_array[y, 0]
        if np.all(image_array[y] == first_pixel_color):
            return y
    return height


def get_image_axies(image, y_look_up_start=0):
    y_coordinate_start = get_y_coordinate_start(image.shape[0], image, y_look_up_start)
    if y_coordinate_start == y_look_up_start:
        return image.shape[0], y_coordinate_start
    y_coordinate_end = get_y_coordinate_end(image.shape[0], image, y_coordinate_start)
    return y_coordinate_end, y_coordinate_start


def manhwa_level_image_crop_calculator(image, y_coordinate_end=0, image_crop_list=None):
    if image_crop_list is None:
        image_crop_list = []
    y_coordinate_end, y_coordinate_start = get_image_axies(image, y_coordinate_end)
    image_crop_list.append(tuple((y_coordinate_start, y_coordinate_end)))
    print(y_coordinate_start, y_coordinate_end)
    print(y_coordinate_end < image.shape[0])
    if y_coordinate_end < image.shape[0]:
        return manhwa_level_image_crop_calculator(image, y_coordinate_end, image_crop_list)
    else:
        return image_crop_list


def print_level_image_crop_calculator(manhwa_crop_list, image_side_pixel_count=2300):
    side_length = 0
    for image in manhwa_crop_list:
        for i, cut_pixels in enumerate(image):
            side_length += cut_pixels[1] - cut_pixels[0]
            if side_length > image_side_pixel_count:
                cut_pixels = (
                    cut_pixels[0], cut_pixels[0] + image_side_pixel_count - (side_length - (cut_pixels[1] - cut_pixels[0]))
                )
                old_cut_pixels = image[i]
                image[i] = cut_pixels

                side_length = 0
                image.insert(i + 1, (image[i][1], old_cut_pixels[1]))
    return manhwa_crop_list


def filter_blank_images(manhwa_crop_list, image):
    for i, cut_pixels in enumerate(manhwa_crop_list):
        check_flag = get_y_coordinate_start(image.shape[0], image, cut_pixels[0])
        if check_flag == cut_pixels[0]:
            manhwa_crop_list.remove(cut_pixels)
    return manhwa_crop_list


def crop_image(image_paths: list):
    manhwa_crop_dict = {}
    all_crop_lists = []  # To collect all crop lists before passing to print_level_image_crop_calculator

    for image_path in image_paths:
        image = cv2.imread(image_path)
        crop_list = manhwa_level_image_crop_calculator(image)
        crop_list = filter_blank_images(crop_list, image)

        # Save both the image and the filtered crop list in the dictionary
        manhwa_crop_dict[image_path] = {"image": image, "crop_list": crop_list}

        # Add the filtered crop list to the aggregate list
        all_crop_lists.append(crop_list)

    # Now, process all crop lists together with print_level_image_crop_calculator
    final_crop_list = print_level_image_crop_calculator(all_crop_lists)
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


def place_images_on_canvas(cropped_images):
    full_image = np.ones((int(2480), int(3508 / 2), 3), dtype=np.uint8) * 255
    start_x, start_y = 950, 60
    current_x, current_y = start_x, start_y
    images_placed = []
    for index, img in enumerate(cropped_images):
        h, w = img.shape[:2]
        full_image[current_y:current_y + h, current_x:current_x + w] = img
        current_y += h
        if current_y == 2360:
            if current_x == 950:
                current_x, current_y = 130, start_y
                current_x = 130
            elif current_x == 130:
                images_placed.append(full_image)
                cv2.imwrite(f'full_image{index}.png', full_image)
                current_x, current_y = start_x, start_y
                full_image = np.ones((int(2480), int(3508 / 2), 3), dtype=np.uint8) * 255
    return images_placed


def make_full_image(image_paths: list):
    image_componenets_lists = crop_image(image_paths)
    images_placed = place_images_on_canvas(image_componenets_lists)
    for i, image in enumerate(images_placed):
        cv2.imwrite(f'full_image{i}.png', image)


def manage_images(image_paths):
    # start_time = time.time()
    images = []
    images_placed = make_full_image(image_paths)
    # print(f"Time taken: {time.time() - start_time:.2f} seconds")
    for image_path in image_paths:
        images.extend(images_placed)

    for i, image in enumerate(images):
        cv2.imwrite(f'image{i}.png', image)
    #     print('Image saved as full_image.png')
