from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
from PIL import Image

app = Flask(__name__)
app.secret_key = 'ppoo6689'  # 로그인 비번

UPLOAD_FOLDER = 'static/uploads'
THUMB_FOLDER_NAME = 'thumbs'
PASSWORD = 'ppoo6689'


def get_images(book):
    folder_path = os.path.join(UPLOAD_FOLDER, book)
    thumb_path = os.path.join(folder_path, THUMB_FOLDER_NAME)
    os.makedirs(thumb_path, exist_ok=True)

    image_files = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            thumb_file = os.path.join(thumb_path, filename)
            if not os.path.exists(thumb_file):
                make_thumbnail(file_path, thumb_file)
            image_files.append({
                'full': f"/{file_path.replace(os.sep, '/')}",
                'thumb': f"/{thumb_file.replace(os.sep, '/')}"
            })
    return image_files


def make_thumbnail(image_path, thumb_path):
    try:
        img = Image.open(image_path)
        img.thumbnail((300, 300))
        img.save(thumb_path)
    except Exception as e:
        print(f"Thumbnail Error: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pw = request.form.get('password')
        if pw == PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return "비밀번호가 틀렸습니다.", 401
    return render_template('admin.html')


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))


@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    books = os.listdir(UPLOAD_FOLDER)
    books = [b for b in books if os.path.isdir(os.path.join(UPLOAD_FOLDER, b))]
    return render_template('gallery.html', books=books)


@app.route('/gallery/<book>')
def gallery(book):
    if not session.get('admin'):
        return redirect(url_for('login'))
    images = get_images(book)
    return render_template('gallery.html', images=images, current_book=book, books=[])


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
