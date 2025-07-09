from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # 세션용

UPLOAD_FOLDER = 'static/uploads'
ADMIN_PASSWORD = 'ppoo6689'  # 관리자 비밀번호

@app.route('/')
def index():
    books = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', books=books)

@app.route('/gallery/<book_name>')
def gallery(book_name):
    image_dir = os.path.join(UPLOAD_FOLDER, book_name)
    if not os.path.exists(image_dir):
        return "Not Found", 404
    images = os.listdir(image_dir)
    is_admin = session.get('admin', False)
    return render_template('gallery.html', book_name=book_name, images=images, is_admin=is_admin)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('index'))
        else:
            return "비밀번호가 틀렸습니다."
    return render_template('admin.html')

@app.route('/upload/<book_name>', methods=['POST'])
def upload(book_name):
    if not session.get('admin'):
        return "Unauthorized", 403
    file = request.files['image']
    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, book_name, filename)
    file.save(save_path)
    return redirect(url_for('gallery', book_name=book_name))

@app.route('/delete/<book_name>/<filename>', methods=['POST'])
def delete_image(book_name, filename):
    if not session.get('admin'):
        return "Unauthorized", 403
    file_path = os.path.join(UPLOAD_FOLDER, book_name, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('gallery', book_name=book_name))

if __name__ == '__main__':
    app.run(debug=True)
