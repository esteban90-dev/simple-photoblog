from flask import Flask
from flask import render_template, redirect, url_for, abort
import json

app = Flask(__name__)

app.config.from_file('config.json', load=json.load)

def get_all_records_from_csv(file_path):
  # return csv data as a list of dictionaries
  import csv

  results = []

  with open(file_path) as csv_file:
    reader = csv.DictReader(csv_file)

    for row in reader:
      results.append(row)

  return results

def find_record_from_csv(file_path, search_column, search_value):
  # Return matching record from csv as a dictionary.
  # If nothing is found, return None.
  import csv

  with open(file_path) as csv_file:
    reader = csv.DictReader(csv_file)

    for row in reader:
      if row.get(search_column) == search_value:
        return row

  return None

def organize_links(data):
  # Organize links into a dictionary of categories.
	data_organized = {}
	
	for item in data:
		if item['category'] not in data_organized.keys():
			data_organized[item['category']] = [item]
		else:
			data_organized[item['category']].append(item)
			
	return data_organized

def get_image_files(root_folder, path, prefix):
  # return list of image files for the given path
  import os

  images = []

  for file in os.listdir(root_folder + path):
    name, ext = os.path.splitext(file)
    if ext in ['.jpg', '.JPG']:
      images.append(os.path.join(prefix, path, file))

  return images

@app.route("/", methods=['GET'])
def index():
  photo_folders = get_all_records_from_csv(app.config['PHOTO_DATA'])
  drawing_folders = get_all_records_from_csv(app.config['DRAWING_DATA'])
  links = get_all_records_from_csv(app.config['LINK_DATA'])

  photo_of_the_month = None
  photo_of_the_month_files = get_image_files(app.config['PHOTO_FOLDER'], 'photo-of-the-month', 'photos')

  if len(photo_of_the_month_files) > 0:
    photo_of_the_month = photo_of_the_month_files[0]

  data = {
    'photo_folders': photo_folders,
    'drawing_folders': drawing_folders,
    'links': organize_links(links),
    'photo_of_the_month': photo_of_the_month
  }

  return render_template('index.html', data=data)

@app.route("/photos/<path:folder_path>", methods=['GET'])
def show_photo_folder(folder_path):
  folder_record = find_record_from_csv(app.config['PHOTO_DATA'], 'path', folder_path)

  if not folder_record:
    abort(404)

  photos = get_image_files(app.config["PHOTO_FOLDER"], folder_record.get('path'), 'photos')

  # sort photos
  if int(folder_record.get('reverse_order')) == 1:
    photos_sorted = sorted(photos, reverse=True)
  else:
    photos_sorted = sorted(photos)

  data = {
    'folder': folder_record,
    'images': photos_sorted
  }

  return render_template('images.html', data=data)

@app.route("/drawings/<path:folder_path>", methods=['GET'])
def show_drawing_folder(folder_path):
  folder_record = find_record_from_csv(app.config['DRAWING_DATA'], 'path', folder_path)

  if not folder_record:
    abort(404)

  drawings = get_image_files(app.config['DRAWING_FOLDER'], folder_record.get('path'), 'drawings')

  # sort drawings
  sorting_key = lambda x: int(x[:x.rindex('.')].split(' ')[-1])

  if int(folder_record.get('reverse_order')) == 1:
    drawings_sorted = sorted(drawings, key=sorting_key, reverse=True)
  else:
    drawings_sorted = sorted(drawings, key=sorting_key)

  data = {
    'folder': folder_record,
    'images': drawings_sorted
  }

  return render_template('images.html', data=data)