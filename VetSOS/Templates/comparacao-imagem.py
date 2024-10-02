import os
from google.cloud import vision
from google.cloud.vision import types

# Set the environment variable for authentication
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'Templates\cloudkey.json'

def load_image(image_path):
    """Loads the image from the given path and returns it as a Vision API Image object."""
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    return vision.Image(content=content)

def analyze_image(image):
    """Analyzes the image using Google Cloud Vision API and returns the objects detected."""
    client = vision.ImageAnnotatorClient()
    response = client.object_localization(image=image)
    objects = response.localized_object_annotations
    return objects

def compare_objects(objects1, objects2):
    """Compares objects detected in two images."""
    objects1_names = {obj.name for obj in objects1}
    objects2_names = {obj.name for obj in objects2}

    common_objects = objects1_names.intersection(objects2_names)
    unique_to_image1 = objects1_names - objects2_names
    unique_to_image2 = objects2_names - objects1_names

    print(f"Objects in both images: {common_objects}")
    print(f"Objects unique to image 1: {unique_to_image1}")
    print(f"Objects unique to image 2: {unique_to_image2}")

def compare_images(image1_path, image2_path):
    """Compares two images by analyzing the objects in them."""
    image1 = load_image(image1_path)
    image2 = load_image(image2_path)

    objects1 = analyze_image(image1)
    objects2 = analyze_image(image2)

    compare_objects(objects1, objects2)

# Paths to the images you want to compare
image1_path = 'path_to_first_image.jpg'
image2_path = 'path_to_second_image.jpg'

# Compare the images
compare_images(image1_path, image2_path)
