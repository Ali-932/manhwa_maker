import numpy as np
import cv2


# import cProfile
# cProfile.run('image_crop_calculator(image)')

def get_y_coordinate_start(height, image_array, y_look_up_start, diff_sum, steps=5):
    # print(f'start {diff_sum}')
    # diff = np.abs(np.diff(image_array, axis=1))
    # diff_sum = np.sum(diff, axis=1)
    # print(f'start2{diff_sum}')
    non_color_lines = np.where(diff_sum != 0)[0]
    number_of_same_color_lines = 0
    start_index = np.searchsorted(non_color_lines, y_look_up_start)
    for y in non_color_lines[start_index::steps]:
        number_of_same_color_lines += 1
        if number_of_same_color_lines > 3:
            return max(y_look_up_start, y)
    return y_look_up_start


def get_y_coordinate_end(height, image_array, y_coordinate_start, steps=5):
    offset = 10
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
    y_coordinate_start = get_y_coordinate_start(image.shape[0], image, y_look_up_start, diff_sum)
    if y_coordinate_start == y_look_up_start:
        return image.shape[0], y_coordinate_start
    y_coordinate_end = get_y_coordinate_end(image.shape[0], image, y_coordinate_start)
    return y_coordinate_end, y_coordinate_start


def manhwa_level_image_crop_calculator(image, diff_sum, y_coordinate_end=0, image_crop_list=None):
    if image_crop_list is None:
        image_crop_list = []
    y_coordinate_end, y_coordinate_start = get_image_axies(image, diff_sum, y_look_up_start=y_coordinate_end)
    image_crop_list.append(tuple((max(0, y_coordinate_start), y_coordinate_end)))
    if y_coordinate_end < image.shape[0]:
        return manhwa_level_image_crop_calculator(image,diff_sum, y_coordinate_end, image_crop_list)
    else:
        return image_crop_list


def print_level_image_crop_calculator(manhwa_crop_list, image_side_pixel_count=2300):
    side_length = 0
    for image in manhwa_crop_list:
        for i, cut_pixels in enumerate(image):
            side_length += cut_pixels[1] - cut_pixels[0]
            if side_length > image_side_pixel_count:
                cut_pixels = (
                    cut_pixels[0],
                    cut_pixels[0] + image_side_pixel_count - (side_length - (cut_pixels[1] - cut_pixels[0]))
                )
                old_cut_pixels = image[i]
                image[i] = cut_pixels

                side_length = 0
                image.insert(i + 1, (image[i][1], old_cut_pixels[1]))
    return manhwa_crop_list


def filter_blank_images(manhwa_crop_list, image):
    # Load the image
    filtered_crops = []

    for cut_pixels in manhwa_crop_list:
        # Crop the image using y-coordinates: cut_pixels[1] is the start y-coordinate,
        # cut_pixels[2] is the end y-coordinate. Adjust indices if your structure is different.
        cropped_image = image[cut_pixels[0]:cut_pixels[1], :]
        std_dev = np.std(cropped_image)
        is_blank = std_dev < 10
        # Check if cropped image is blank (same color)
        if not is_blank:
            filtered_crops.append(cut_pixels)

    return filtered_crops


def filter_small_images(crop_list, min_height=35):
    filtered_crops = []
    for cut_pixels in crop_list:
        if (cut_pixels[1] - cut_pixels[0]) >= min_height:
            filtered_crops.append(cut_pixels)
        # else:
        #     cropped_image = image[cut_pixels[0]:cut_pixels[1], :]
        #     try:
        #         cv2.imwrite(f'edxmeedc{cut_pixels[0]}{cut_pixels[1]}.png', cropped_image)
        #     except Exception as e:
        #         print(e)
    return filtered_crops


def appropriate_size_filter(image, target_width=804):
    # Get the original dimensions of the image
    (h, w) = image.shape[:2]
    if w < target_width:
        return image

    ratio = target_width / float(w)

    # Calculate the new height based on the aspect ratio
    target_height = int(h * ratio)

    # Resize the image to the target dimensions
    resized_image = cv2.resize(image, (target_width, target_height))
    return resized_image


def remove_border_if_exists_filter(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    x, y, w, h = cv2.boundingRect(contours[0])

    if x == 0 and y == 0 and w == image.shape[1] and h == image.shape[0]:
        return image
    else:
        cropped_image = image[y:y + h, x:x + w]
        return cropped_image


def get_image_attributes(image_path):
    image = cv2.imread(image_path)
    diff = np.abs(np.diff(image, axis=1))
    diff_sum = np.sum(diff, axis=1)
    return image, diff_sum


def crop_image(image_paths: list):
    manhwa_crop_dict = {}
    all_crop_lists = []  # To collect all crop lists before passing to print_level_image_crop_calculator

    for image_path in image_paths:
        image, diff_sum = get_image_attributes(image_path)
        image = cv2.imread(image_path)
        image = appropriate_size_filter(image)
        image = remove_border_if_exists_filter(image)
        crop_list = manhwa_level_image_crop_calculator(image, diff_sum)
        crop_list = filter_small_images(crop_list)
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
            # try:
            #     cv2.imwrite(f'edxmeedc{crop[0]}{crop[1]}{cropped_img.shape[1]}.png', cropped_img)
            # except Exception as e:
            #     print(e)
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
                current_x, current_y = start_x, start_y
                full_image = np.ones((int(2480), int(3508 / 2), 3), dtype=np.uint8) * 255
        if index == len(cropped_images) - 1:
            images_placed.append(full_image)
    return images_placed


def make_full_image(image_paths: list):
    image_componenets_lists = crop_image(image_paths)
    images_placed = place_images_on_canvas(image_componenets_lists)
    for i, image in enumerate(images_placed):
        cv2.imwrite(f'full_imag2e{i}.png', image)


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


'''
for testing 
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp') # Tuple for direct matching
    image_paths = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(image_extensions): # Check if the file ends with any of the image extensions
                image_paths.append(os.path.join(root, file))


                '''
