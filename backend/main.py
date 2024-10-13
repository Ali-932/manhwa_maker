import cv2
from PIL import Image

from backend.utils import crop_and_collect_images, place_images_on_canvas, add_margin_for_canvas
import sys


sys.setrecursionlimit(2000)

def manage_images(image_paths: list, column_height=2300):
    image_componenets_lists = crop_and_collect_images(image_paths, column_height=column_height)
    images = place_images_on_canvas(image_componenets_lists, column_height=column_height)
    images = add_margin_for_canvas(images)
    return images


def pdfmaker_thread(file_path, images, callback, progress_callback):
    if images:
        pillow_images = []
        for image in images:
            pillow_images.append(Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                                 )
            progress_callback()
        first_image = pillow_images[0]
        pillow_images = pillow_images[1:]

        first_image.save(
            f'{file_path}',
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=pillow_images,
            optimize=True,
        )
    callback()


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
