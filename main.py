import cv2
import imutils
import numpy as np
import os

def list_images_in_folder(folder_path):
    try:
        files = os.listdir(folder_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"The folder {folder_path} does not exist.")

    images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    for i, img in enumerate(images):
        print(f"{i + 1}: {img}")
    return images


def convert_image(folder_path, filename):
    # Full path to the input image
    input_path = os.path.join(folder_path, filename)
    # Full path to the output image with "-edited" suffix
    output_filename = os.path.splitext(filename)[0] + '-edited.jpeg'
    output_path = os.path.join(folder_path, output_filename)

    # Using open cv to read in the image
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"The image {filename} does not exist.")

    status = "Success, File has been saved."

    # Adding Alpha Channel to Image
    BGRA = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    BGRA[:, :, 3] = 255

    # Resizing
    resized = imutils.resize(BGRA, width=800)

    # Mirror
    mirror = cv2.flip(resized, 0)

    # Crop Params
    width, height = 800, 200
    x, y = 0, 0

    # Crop
    cropped = mirror[y:y + height, x:x + width]

    # Design Gradient
    ht, wd = cropped.shape[:2]
    pct = 99
    ht2 = int(ht * pct / 100)
    ht3 = ht - ht2
    top = np.full((ht3, wd), 255, dtype=np.uint8)
    btm = np.linspace(200, 0, ht2, endpoint=True, dtype=np.uint8)
    btm = np.tile(btm, (wd, 1))
    btm = np.transpose(btm)
    alpha = np.vstack((top, btm))

    # Assign Gradient to Alpha
    result = cropped.copy()
    result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
    result[:, :, 3] = alpha

    # Merge Both Images
    final = np.concatenate((resized, result), axis=0)

    # Convert Alpha to White
    B, G, R, A = cv2.split(final)
    alpha = A / 255
    R = (255 * (1 - alpha) + R * alpha).astype(np.uint8)
    G = (255 * (1 - alpha) + G * alpha).astype(np.uint8)
    B = (255 * (1 - alpha) + B * alpha).astype(np.uint8)

    # Print File
    final = cv2.merge((B, G, R))

    # Write File to save with "-edited" suffix
    cv2.imwrite(output_path, final)
    return status


def set_path():
    path_input = input("Enter the folder path where images are stored: ")
    with open("path.txt", "w") as f:
        f.write(path_input)


def read_path():
    try:
        with open("path.txt", "r") as f:
            path = f.read().strip()
    except FileNotFoundError:
        path = ""
    return path


while True:
    folder_path = read_path()
    if not folder_path:
        set_path()
        folder_path = read_path()
        continue

    try:
        images = list_images_in_folder(folder_path)
    except FileNotFoundError as e:
        print(e)
        set_path()
        continue

    print("\n")

    while True:
        try:
            user_input = input(
                "Enter the number of the image you want to process (or type 'path' to reset the folder path): ")
            if user_input.lower() == 'path':
                set_path()
                break

            image_index = int(user_input) - 1
            if image_index < 0 or image_index >= len(images):
                raise ValueError("Invalid selection. Please enter a number corresponding to the listed images.")

            selected_image = images[image_index]

            # Check if the selected image still exists
            input_path = os.path.join(folder_path, selected_image)
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"The image {selected_image} does not exist.")

            # Convert the selected image
            status = convert_image(folder_path, selected_image)
            print(status)
            break

        except ValueError as e:
            print(e)
        except FileNotFoundError as e:
            print(e)
