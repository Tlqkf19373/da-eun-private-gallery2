from flask import Flask, render_template, request, redirect, session, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ADMIN_PASSWORD = 'ppoo6689'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    albums = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', albums=albums)

@app.route('/gallery/<album>')
def gallery(album):
    path = os.path.join(UPLOAD_FOLDER, album)
    if not os.path.exists(path):
        return "앨범이 존재하지 않습니다."
    photos = os.listdir(path)
    return render_template('gallery.html', photos=photos, album=album)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/upload/<album>', methods=['POST'])
def upload(album):
    if not session.get('admin'):
        return "권한 없음"
    if 'photo' not in request.files:
        return redirect('/')
    file = request.files['photo']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, album, filename)
        file.save(save_path)
    return redirect(f'/gallery/{album}')

@app.route('/delete/<album>/<filename>')
def delete(album, filename):
    if not session.get('admin'):
        return "권한 없음"
    file_path = os.path.join(UPLOAD_FOLDER, album, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(f'/gallery/{album}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
