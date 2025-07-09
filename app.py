from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.secret_key = 'ppoo6689'

UPLOAD_FOLDER = 'static/uploads'
THUMB_FOLDER = 'thumbs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 폴더 자동 생성
def create_folders():
    for folder in ['book1', 'book2']:
        os.makedirs(os.path.join(UPLOAD_FOLDER, folder, THUMB_FOLDER), exist_ok=True)

create_folders()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_images(book):
    path = os.path.join(UPLOAD_FOLDER, book)
    files = [f for f in os.listdir(path) if allowed_file(f)]
    return files

def create_thumbnail(image_path, thumb_path):
    size = (300, 300)
    img = Image.open(image_path)
    img.thumbnail(size)
    img.save(thumb_path)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    password = request.form['password']
    if password == 'ppoo6689':
        session['logged_in'] = True
        return redirect(url_for('gallery'))
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('gallery'))

@app.route('/gallery')
def gallery():
    book1_images = get_images('book1')
    book2_images = get_images('book2')
    return render_template('gallery.html', book1=book1_images, book2=book2_images, logged_in=session.get('logged_in'))

@app.route('/upload/<book>', methods=['POST'])
def upload(book):
    if not session.get('logged_in'):
        return "Unauthorized", 403

    if 'file' not in request.files:
        return redirect(url_for('gallery'))

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return redirect(url_for('gallery'))

    filename = secure_filename(file.filename)
    book_path = os.path.join(UPLOAD_FOLDER, book)
    file_path = os.path.join(book_path, filename)
    file.save(file_path)

    thumb_dir = os.path.join(book_path, THUMB_FOLDER)
    thumb_path = os.path.join(thumb_dir, filename)
    create_thumbnail(file_path, thumb_path)

    return redirect(url_for('gallery'))

if __name__ == '__main__':
    app.run(debug=True)
