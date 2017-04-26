import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
from werkzeug import secure_filename

UPLOAD_FOLDER = '/var/www/html/AlaricLightStory/static/images/'
UPLOAD_ZOOM_FOLDER = '/var/www/html/AlaricLightStory/static/images/thumbnails'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'zyj395470395'
app.config['MYSQL_DB'] = 'AlaricLightStory'
app.config['MYSQL_HOST'] = 'localhost'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_ZOOM_FOLDER'] = UPLOAD_ZOOM_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def first_page():
	cur = mysql.connection.cursor()
	query = "SELECT name, tag FROM photos"
	cur.execute(query)
	data = cur.fetchall()
	return render_template('index.html', result = data)

@app.route('/display')
def display_photos():
	cur = mysql.connection.cursor()
	query = "SELECT name, tag FROM photos"
	cur.execute(query)
	data = cur.fetchall()
	return jsonify(data)

@app.route('/admin')
def login_page():
	return render_template('login.html')

@app.route('/admin', methods = ['POST'])
def admin_default():
	username = request.form.get('username')
	password = request.form.get('password')
	if username == 'alariczeng' and password == 'zyj395470395':
		return render_template('admin.html')
	else:
		return render_template('login.html')


@app.route('/admin/upload', methods = ['POST'])
def upload_file():
	file = request.files['file']
	tag = request.form.get('tag')
	zoom_file = request.files['zoom_file']
	if file and allowed_file(file.filename) and zoom_file and allowed_file(zoom_file.filename):
		filename = secure_filename(file.filename)
		zoom_filename = secure_filename(zoom_file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		zoom_file.save(os.path.join(app.config['UPLOAD_ZOOM_FOLDER'], zoom_filename))
		cur = mysql.connection.cursor()
		query = "INSERT INTO photos (name, tag, pubdate) VALUES('" + filename + "', '" + tag + "', '" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "')"
		cur.execute(query)
		mysql.connection.commit()
		#data = cur.fetchall()
		#return str(data)
	return render_template('admin.html')



if __name__ == '__main__':
  app.run()
