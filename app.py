from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.secret_key = 'ppoo6689'

UPLOAD_FOLDER = 'static/uploads'
THUMB_FOLDER = 'thumbs'
FOLDERS = ['book1', 'book2']
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 관리자 비밀번호
ADMIN_PASSWORD = 'ppoo6689'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_folders():
    for folder in FOLDERS:
        target_thumb_path = os.path.join(UPLOAD_FOLDER, folder, THUMB_FOLDER)
        if not os.path.exists(target_thumb_path):
            os.makedirs(target_thumb_path, exist_ok=True)
        elif not os.path.isdir(target_thumb_path):
            os.remove(target_thumb_path)
            os.makedirs(target_thumb_path, exist_ok=True)

create_folders()

@app.route('/')
def index():
    return render_template('index.html', folders=FOLDERS, is_admin=session.get('admin', False))

@app.route('/<folder>')
def gallery(folder):
    if folder not in FOLDERS:
        return "Folder not found", 404
    path = os.path.join(UPLOAD_FOLDER, folder)
    thumb_path = os.path.join(path, THUMB_FOLDER)
    images = [f for f in os.listdir(path) if allowed_file(f)]
    return render_template('gallery.html', images=images, folder=folder, thumbs=os.listdir(thumb_path), is_admin=session.get('admin', False))

@app.route('/upload/<folder>', methods=['POST'])
def upload(folder):
    if not session.get('admin'):
        return "Unauthorized", 403
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        folder_path = os.path.join(UPLOAD_FOLDER, folder)
        save_path = os.path.join(folder_path, filename)
        file.save(save_path)

        # 썸네일 생성
        thumb_dir = os.path.join(folder_path, THUMB_FOLDER)
        img = Image.open(save_path)
        img.thumbnail((300, 300))
        img.save(os.path.join(thumb_dir, filename))
    return redirect(url_for('gallery', folder=folder))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, folder), filename)

@app.route('/uploads/<folder>/thumbs/<filename>')
def thumbnail_file(folder, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, folder, THUMB_FOLDER), filename)

if __name__ == '__main__':
    app.run(debug=True)
