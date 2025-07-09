from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
from PIL import Image

app = Flask(__name__)
app.secret_key = 'your_secret_key'

ADMIN_PASSWORD = 'ppoo6689'
UPLOAD_FOLDER = 'static/uploads'
THUMB_FOLDER = 'thumbs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 썸네일 생성 함수
def create_thumbnail(image_path, thumbnail_path):
    try:
        with Image.open(image_path) as img:
            img.thumbnail((300, 300))
            img.save(thumbnail_path)
    except Exception as e:
        print(f"썸네일 생성 오류: {e}")

# 초기 폴더 생성 함수
def create_folders():
    for folder in os.listdir(UPLOAD_FOLDER):
        full_folder = os.path.join(UPLOAD_FOLDER, folder)
        thumb_path = os.path.join(full_folder, THUMB_FOLDER)
        if os.path.isdir(full_folder):
            os.makedirs(thumb_path, exist_ok=True)
create_folders()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    galleries = [d for d in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))]
    return render_template('index.html', galleries=galleries, is_admin=session.get('admin'))

@app.route('/gallery/<folder>')
def gallery(folder):
    folder_path = os.path.join(UPLOAD_FOLDER, folder)
    thumb_path = os.path.join(folder_path, THUMB_FOLDER)
    images = [f for f in os.listdir(folder_path) if allowed_file(f)]
    thumbs = []
    for img in images:
        thumb_file = os.path.join(thumb_path, img)
        if not os.path.exists(thumb_file):
            create_thumbnail(os.path.join(folder_path, img), thumb_file)
        thumbs.append(img)
    return render_template('gallery.html', folder=folder, images=thumbs, is_admin=session.get('admin'))

@app.route('/upload/<folder>', methods=['POST'])
def upload(folder):
    if not session.get('admin'):
        return redirect(url_for('login'))

    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = file.filename
        save_path = os.path.join(UPLOAD_FOLDER, folder, filename)
        file.save(save_path)
        # 썸네일도 저장
        thumb_path = os.path.join(UPLOAD_FOLDER, folder, THUMB_FOLDER, filename)
        create_thumbnail(save_path, thumb_path)
    return redirect(url_for('gallery', folder=folder))

@app.route('/delete/<folder>/<filename>')
def delete(folder, filename):
    if not session.get('admin'):
        return redirect(url_for('login'))
    file_path = os.path.join(UPLOAD_FOLDER, folder, filename)
    thumb_path = os.path.join(UPLOAD_FOLDER, folder, THUMB_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(thumb_path):
        os.remove(thumb_path)
    return redirect(url_for('gallery', folder=folder))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
