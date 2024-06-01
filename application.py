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

def get_next_record_from_csv(file_path, search_column, search_value):
  # return the next record for the supplied search_column/search_value
  # if record doesnt exist, or a subsequent record doesnt exist, return None
  records = get_all_records_from_csv(file_path)
  next_record = None

  for index, record in enumerate(records):
    if record.get(search_column) == search_value: # find matching record
      if index + 1 < len(records): # return the next record, if there is one
        next_record = records[index + 1]
        break

  return next_record

def get_previous_record_from_csv(file_path, search_column, search_value):
  # return the previous record for the supplied search_column/search_value
  # if record doesnt exist, or a previous record doesnt exist, return None
  records = get_all_records_from_csv(file_path)
  previous_record = None

  for index, record in enumerate(records):
    if record.get(search_column) == search_value: # find matching record
      if index - 1 >= 0: # return the previous record, if there is one
        previous_record = records[index - 1]
        break

  return previous_record

def organize_links(data):
  # Organize links into a dictionary of categories.
	data_organized = {}
	
	for item in data:
		if item['category'] not in data_organized.keys():
			data_organized[item['category']] = [item]
		else:
			data_organized[item['category']].append(item)
			
	return data_organized

def get_image_files(root_folder, path):
  # return list of image files for the given root_folder + path
  import os

  images = []

  for file in os.listdir(root_folder + path):
    name, ext = os.path.splitext(file)
    if ext in ['.jpg', '.JPG']:
      images.append(os.path.join(root_folder, path, file))

  return images

@app.route("/", methods=['GET'])
def index():
  photo_folders = get_all_records_from_csv(app.config['PHOTO_DATA'])
  drawing_folders = get_all_records_from_csv(app.config['DRAWING_DATA'])
  links = get_all_records_from_csv(app.config['LINK_DATA'])

  photo_of_the_month = None
  photo_of_the_month_files = get_image_files(app.config['PHOTO_FOLDER'], 'photo-of-the-month')

  if len(photo_of_the_month_files) > 0:
    photo_of_the_month = photo_of_the_month_files[0].replace(app.config['PHOTO_FOLDER'], 'photos/') # shorten full image path as required for the view

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

  previous_folder_record = get_previous_record_from_csv(app.config['PHOTO_DATA'], 'path', folder_path)
  next_folder_record = get_next_record_from_csv(app.config['PHOTO_DATA'], 'path', folder_path)

  photos = get_image_files(app.config["PHOTO_FOLDER"], folder_record.get('path'))
  photos_corrected_paths = [photo.replace(app.config["PHOTO_FOLDER"], 'photos/') for photo in photos]  # shorten full image paths as required for the view

  # sort photos
  if int(folder_record.get('reverse_order')) == 1:
    photos_sorted = sorted(photos_corrected_paths, reverse=True)
  else:
    photos_sorted = sorted(photos_corrected_paths)

  data = {
    'folder': folder_record,
    'previous_folder': previous_folder_record,
    'next_folder': next_folder_record,
    'show_folder_method': 'show_photo_folder',
    'images': photos_sorted
  }

  return render_template('images.html', data=data)

@app.route("/drawings/<path:folder_path>", methods=['GET'])
def show_drawing_folder(folder_path):
  folder_record = find_record_from_csv(app.config['DRAWING_DATA'], 'path', folder_path)

  if not folder_record:
    abort(404)

  previous_folder_record = get_previous_record_from_csv(app.config['DRAWING_DATA'], 'path', folder_path)
  next_folder_record = get_next_record_from_csv(app.config['DRAWING_DATA'], 'path', folder_path)

  drawings = get_image_files(app.config['DRAWING_FOLDER'], folder_record.get('path'))
  drawings_corrected_paths = [drawing.replace(app.config["DRAWING_FOLDER"], 'drawings/') for drawing in drawings]  # shorten full image paths as required for the view

  # sort drawings
  sorting_key = lambda x: int(x[:x.rindex('.')].split(' ')[-1])

  if int(folder_record.get('reverse_order')) == 1:
    drawings_sorted = sorted(drawings_corrected_paths, key=sorting_key, reverse=True)
  else:
    drawings_sorted = sorted(drawings_corrected_paths, key=sorting_key)

  data = {
    'folder': folder_record,
    'previous_folder': previous_folder_record,
    'next_folder': next_folder_record,
    'show_folder_method': 'show_drawing_folder',
    'images': drawings_sorted
  }

  return render_template('images.html', data=data)