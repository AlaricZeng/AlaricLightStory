from __future__ import print_function
import sys

import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, Markup, send_file
from flask_mysqldb import MySQL
from datetime import datetime
from werkzeug import secure_filename
import markdown2

from constants import * 

app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'zyj395470395'
app.config['MYSQL_DB'] = 'AlaricLightStory'
app.config['MYSQL_HOST'] = 'localhost'

app.config['UPLOAD_IMG_FOLDER'] = UPLOAD_IMG_FOLDER
app.config['UPLOAD_ZOOM_IMG_FOLDER'] = UPLOAD_ZOOM_IMG_FOLDER
app.config['UPLOAD_STORY_FOLDER'] = UPLOAD_STORY_FOLDER
app.config['ALLOWED_IMG_EXTENSIONS'] = ALLOWED_IMG_EXTENSIONS
app.config['ALLOWED_STORY_EXTENSIONS'] = ALLOWED_STORY_EXTENSIONS

mysql = MySQL(app)

def allowed_img_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_IMG_EXTENSIONS']

def allowed_story_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_STORY_EXTENSIONS']

@app.route('/')
def first_page():
	cur = mysql.connection.cursor()
	
	fetch_all_images_query = "SELECT name, tag, linked_page_index FROM photos WHERE display=True"
	cur.execute(fetch_all_images_query)
	all_images = cur.fetchall()
	
	fetch_all_stories_query = "SELECT id, title, created_at FROM stories"
	cur.execute(fetch_all_stories_query)
	all_stories = cur.fetchall()
	cur.close()

	return render_template('index.html', images = all_images, stories = all_stories)

@app.route('/stories')
def get_story_content():
	story_id = request.args.get("story_id")
	cur = mysql.connection.cursor()
	fetch_story_title_query = "SELECT title FROM stories WHERE id =" + story_id
	cur.execute(fetch_story_title_query)
	story_title = cur.fetchone()[0]

	fetch_next_story_title_query = "SELECT id, title FROM stories WHERE id >" + story_id + " ORDER BY id"
	cur.execute(fetch_next_story_title_query)
	next_story = cur.fetchone()
	if next_story:
		next_story_id = next_story[0]
		next_story_title = next_story[1]
	else:
		fetch_first_story_title_query = "SELECT id, title FROM stories ORDER BY id"
		cur.execute(fetch_first_story_title_query)
		next_story = cur.fetchone()
		next_story_id = next_story[0]
		next_story_title = next_story[1]
	cur.close()

	with open(UPLOAD_STORY_FOLDER + story_title + ".md", "r") as f:
		content = f.read()

	content = Markup(markdown2.markdown(content, extras=["fenced-code-blocks"]))
	return render_template("story.html", content = content, next_story_id = next_story_id, next_story_title = next_story_title)

@app.route('/display')
def display_photos():
	cur = mysql.connection.cursor()
	query = "SELECT name, tag FROM photos"
	cur.execute(query)
	data = cur.fetchall()
	cur.close()
	return jsonify(data)

@app.route('/login')
def login_page():
	return render_template('login.html')

@app.route('/admin', methods = ['POST'])
def admin_default():
	username = request.form.get('username')
	password = request.form.get('password')
	is_logged_in = request.args.get('is_logged_in')
	if is_logged_in:
		return render_template('admin.html')
	elif username == ADMIN_USER and password == ADMIN_PASSWORD:
		return render_template('admin.html')
	else:
		return render_template('login.html')

@app.route('/admin/get_story_list')
def get_story_list():
	cur = mysql.connection.cursor()
	query = "SELECT id, title FROM stories"
	cur.execute(query)
	data = cur.fetchall()
	cur.close()
	return jsonify(data)

@app.route('/admin/get_image_list')
def get_image_list():
	cur = mysql.connection.cursor()
	query = "SELECT id, name, linked_page_index, display FROM photos"
	cur.execute(query)
	data = cur.fetchall()
	cur.close()
	return jsonify(data)

@app.route('/admin/edit_image_info', methods = ['POST'])
def edit_image_info():
	id = request.form.get('id')
	storyTitle = request.form.get('storyTitle')
	display = request.form.get('display')
	if (storyTitle == 'None'):
		linked_page_index = 'NULL'
	else:
		linked_page_index = storyTitle.split("-")[0].strip()
	cur = mysql.connection.cursor()
	query = "UPDATE photos SET linked_page_index = " + linked_page_index + ", display = " + display + " WHERE id = " + id;
	cur.execute(query)
	mysql.connection.commit()
	cur.close()
	return jsonify(id)

@app.route('/admin/delete_image', methods = ['POST'])
def delete_image():
	id = request.form.get('id')

	cur = mysql.connection.cursor()
	query = "DELETE FROM photos WHERE id = " + id
	cur.execute(query)
	mysql.connection.commit()
	cur.close()
	return jsonify(id)

@app.route('/admin/upload_image', methods = ['POST'])
def upload_image():
	file = request.files['file']
	tag = request.form.get('tag')
	zoom_file = request.files['zoom_file']
	linked_page = request.form.get('linked_page')
	if (linked_page == 'None'):
		linked_page_index = None
	else:
		linked_page_index = linked_page.split("-")[0].strip()
	if request.form.get('display') == "display":
		display = DISPLAY_PICTURE
	else:
		display = NOT_DISPLAY_PICTURE
	if file and allowed_img_file(file.filename) and zoom_file and allowed_img_file(zoom_file.filename):
		filename = secure_filename(file.filename)
		zoom_filename = secure_filename(zoom_file.filename)
		file.save(os.path.join(app.config['UPLOAD_IMG_FOLDER'], filename))
		zoom_file.save(os.path.join(app.config['UPLOAD_ZOOM_IMG_FOLDER'], zoom_filename))
		cur = mysql.connection.cursor()
		query = "INSERT INTO photos (name, tag, linked_page_index, created_at, display) VALUES('" + filename + "', '" + tag + "', '" + linked_page_index + "', '" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "', '" + display + "')"
		cur.execute(query)
		mysql.connection.commit()
		cur.close()
	return redirect(url_for('admin_default', is_logged_in = True), code=307)

@app.route('/admin/upload_story', methods = ['POST'])
def upload_story():
	file = request.files['file']
	title = request.form.get('title')
	if file and allowed_story_file(file.filename):
		filename = title + MARKDOWN_EXTENSION
		file.save(os.path.join(app.config['UPLOAD_STORY_FOLDER'], filename))
		cur = mysql.connection.cursor()
		query = "INSERT INTO stories (title, created_at) VALUES('" + title + "', '" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "')"
		cur.execute(query)
		mysql.connection.commit()
		cur.close()
	return redirect(url_for('admin_default', is_logged_in = True), code=307)

@app.route('/admin/edit_story_info', methods = ['POST'])
def edit_story_info():
	id = request.form.get('id')
	file = request.files['file']
	title = request.form.get('title')
	if file and allowed_story_file(file.filename):
		filename = title + MARKDOWN_EXTENSION
		file.save(os.path.join(app.config['UPLOAD_STORY_FOLDER'], filename))
		cur = mysql.connection.cursor()
		query = "UPDATE stories SET title = '" + title + "' WHERE id = " + id;
		print(query, file=sys.stderr)
		cur.execute(query)
		mysql.connection.commit()
		cur.close()
	return redirect(url_for('admin_default', is_logged_in = True), code=307)

@app.route('/admin/delete_story', methods = ['POST'])
def delete_story():
	id = request.form.get('id')

	cur = mysql.connection.cursor()
	query = "UPDATE photos SET linked_page_index = NULL WHERE linked_page_index = " + id;
	cur.execute(query)
	query = "DELETE FROM stories WHERE id = " + id
	cur.execute(query)
	mysql.connection.commit()
	cur.close()
	return jsonify(id)

@app.route('/admin/download_story', methods = ['POST'])
def download_story():
	title = request.form.get('title')
	filename = title + MARKDOWN_EXTENSION

	file = os.path.join(app.config['UPLOAD_STORY_FOLDER'], filename)
	return file

if __name__ == '__main__':
  app.run()
