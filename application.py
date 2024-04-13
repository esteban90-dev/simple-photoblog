from flask import Flask
from flask import render_template, redirect, url_for, abort

app = Flask(__name__)

PHOTOS_LOCATION = './static/photos/'
PHOTO_OF_THE_MONTH_LOCATION = './static/photos/photo-of-the-month/'
DRAWINGS_LOCATION = './static/drawings/'

PHOTO_DATA_LOCATION = './data/photos.csv'
DRAWING_DATA_LOCATION = './data/drawings.csv'
LINK_DATA_LOCATION = './data/links.csv'

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
      # ignore if every field in the record is blank
      if all(value == '' for value in row.values()):
        continue

      elif row.get(search_column) == search_value:
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

def get_image_files(path):
  # return list of image files for the given path
  import os

  images = []

  for file in os.listdir(path):
    name, ext = os.path.splitext(file)
    if ext in ['.jpg', '.JPG']:
      images.append(os.path.join(path, file))

  return images

@app.route("/", methods=['GET'])
def index():
  photo_folders = get_all_records_from_csv(PHOTO_DATA_LOCATION)
  drawing_folders = get_all_records_from_csv(DRAWING_DATA_LOCATION)
  links = get_all_records_from_csv(LINK_DATA_LOCATION)

  photo_of_the_month = None
  photo_of_the_month_files = get_image_files('static/photos/photo-of-the-month')

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
  folder_record = find_record_from_csv('./data/photos.csv', 'path', folder_path)

  if not folder_record:
    abort(404)

  photos = get_image_files('./static/photos/' + folder_record.get('path'))

  # sort photos
  if int(folder_record.get('reverse_order')) == 1:
    photos_sorted = sorted(photos, reverse=True)
  else:
    photos_sorted = sorted(photos)

  data = {
    'folder': folder_record,
    'photos': photos_sorted
  }

  return render_template('photos.html', data=data)

@app.route("/drawings/<path:folder_path>", methods=['GET'])
def show_drawing_folder(folder_path):
  folder_record = find_record_from_csv('./data/drawings.csv', 'path', folder_path)

  if not folder_record:
    abort(404)

  drawings = get_image_files('./static/drawings/' + folder_record.get('path'))

  # sort drawings
  sorting_key = lambda x: int(x[:x.rindex('.')].split(' ')[-1])

  if int(folder_record.get('reverse_order')) == 1:
    drawings_sorted = sorted(drawings, key=sorting_key, reverse=True)
  else:
    drawings_sorted = sorted(drawings, key=sorting_key)

  data = {
    'folder': folder_record,
    'drawings': drawings_sorted
  }

  return render_template('drawings.html', data=data)