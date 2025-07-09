from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.secret_key = 'your_secret_key'

ADMIN_PASSWORD = 'ppoo6689'
UPLOAD_FOLDER = 'static/uploads'
THUMB_FOLDER = 'thumbs'
GALLERY_FOLDERS = ['book1', 'book2']

# 폴더 자동 생성
def create_folders():
    for folder in GALLERY_FOLDERS:
        full_path = os.path.join(UPLOAD_FOLDER, folder)
        thumb_path = os.path.join(full_path, THUMB_FOLDER)
        if not os.path.exists(thumb_path):
            os.makedirs(thumb_path)

create_folders()

# 썸네일 생성
def create_thumbnail(image_path, thumbnail_path):
    with Image.open(image_path) as img:
        img.thumbnail((300, 300))
        img.save(thumbnail_path)

@app.route('/')
def index():
    return redirect(url_for('gallery'))

@app.route('/gallery')
def gallery():
    gallery_data = {}
    for folder in GALLERY_FOLDERS:
        folder_path = os.path.join(UPLOAD_FOLDER, folder)
        thumb_path = os.path.join(folder_path, THUMB_FOLDER)
        images = [f for f in os.listdir(folder_path)
                  if os.path.isfile(os.path.join(folder_path, f)) and not f.startswith('.')]
        thumbs = [f for f in os.listdir(thumb_path)
                  if os.path.isfile(os.path.join(thumb_path, f)) and not f.startswith('.')]
        gallery_data[folder] = {
            'images': images,
            'thumbs': thumbs
        }
    is_admin = session.get('admin', False)
    return render_template('gallery.html', gallery_data=gallery_data, is_admin=is_admin)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
        return redirect(url_for('gallery'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('gallery'))

@app.route('/upload/<folder>', methods=['POST'])
def upload(folder):
    if not session.get('admin'):
        return redirect(url_for('login'))
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, folder, filename)
        file.save(save_path)

        # 썸네일 생성
        thumb_path = os.path.join(UPLOAD_FOLDER, folder, THUMB_FOLDER, filename)
        create_thumbnail(save_path, thumb_path)
    return redirect(url_for('gallery'))

@app.route('/delete/<folder>/<filename>', methods=['POST'])
def delete_image(folder, filename):
    if not session.get('admin'):
        return redirect(url_for('login'))
    os.remove(os.path.join(UPLOAD_FOLDER, folder, filename))
    thumb_path = os.path.join(UPLOAD_FOLDER, folder, THUMB_FOLDER, filename)
    if os.path.exists(thumb_path):
        os.remove(thumb_path)
    return redirect(url_for('gallery'))

if __name__ == '__main__':
    app.run(debug=True)
