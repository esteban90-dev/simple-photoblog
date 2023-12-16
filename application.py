from flask import Flask
from flask import render_template, redirect, url_for, abort

app = Flask(__name__)

def get_image_folders():
  import os
  from os.path import join, getsize

  folders = []

  IMAGE_DIRECTORY = 'static/photos/'

  for root, dirs, files in os.walk(IMAGE_DIRECTORY):
      for file in files:
          if file.endswith('.jpg') or file.endswith('.JPG'):
            folder = root.replace(IMAGE_DIRECTORY, "")
            if folder not in folders:
              folders.append(folder)

  folders.sort(reverse=True)
  return folders

def get_images(image_path):
  import os

  IMAGE_DIRECTORY = 'static/photos/'
  files = os.listdir(os.path.join(IMAGE_DIRECTORY, image_path))
  images = []
  for file in files:
    if file.endswith('.jpg') or file.endswith('.JPG'):
      images.append(os.path.join(IMAGE_DIRECTORY, image_path + '/' + file))

  return images

@app.route("/")
def redirect_to_photos_index():
  return redirect(url_for('photos_index'))

@app.route("/photos")
def photos_index():
  image_folders = get_image_folders()
  return render_template('images_index.html', image_folders=image_folders)

@app.route("/photos/<path:image_folder_path>")
def show_image_folder(image_folder_path):
    images = []
    if image_folder_path in get_image_folders():
      images = get_images(image_folder_path)
    else:
      abort(404)

    cleaned_images = []
    for image in images:
      cleaned_images.append(image.replace('static/', ''))

    return render_template('images.html', images=cleaned_images)

@app.route("/drawings")
def drawings_index():
  return render_template('drawings_index.html')

@app.route("/links")
def links_index():
  return render_template('links_index.html')