from utils import crop_and_collect_images, place_images_on_canvas


def manage_images(image_paths: list, column_height=2360):
    image_componenets_lists = crop_and_collect_images(image_paths, column_height=column_height)
    images_placed = place_images_on_canvas(image_componenets_lists, column_height=column_height)
    return images_placed


'''
for testing 
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp') # Tuple for direct matching
    image_paths = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(image_extensions): # Check if the file ends with any of the image extensions
                image_paths.append(os.path.join(root, file))

# import cProfile
# cProfile.run('manage_images("image_paths")')

                '''
