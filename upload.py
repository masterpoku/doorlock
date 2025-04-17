import os
import requests

# Folder containing images
IMAGE_FOLDER = "image"

# API endpoint for uploading images
UPLOAD_URL = "https://sikapngalah.com/rfid/upload.php"

def get_last_image(folder):
    try:
        # List all files in the directory
        files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        
        # Filter for image files (e.g., .jpg, .png)
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
        if not image_files:
            print("No images found in the folder.")
            return None
        
        # Get the most recently modified file
        latest_image = max(image_files, key=os.path.getmtime)
        return latest_image
    except Exception as e:
        print(f"Error retrieving the last image: {e}")
        return None
    

def upload_image(image_path):
    try:
        with open(image_path, 'rb') as file:
            # Send the image to the server
            response = requests.post(UPLOAD_URL, files={'file': file})
            if response.status_code == 200:
                print(f"Image uploaded successfully: {response.json()}")
            else:
                print(f"Failed to upload image. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error uploading the image: {e}")

if __name__ == "__main__":
    last_image = get_last_image(IMAGE_FOLDER)
    if last_image:
        print(f"Last image found: {last_image}")
        upload_image(last_image)
