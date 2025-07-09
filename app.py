from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'ppoo6689'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
PASSWORD = 'ppoo6689'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    folders = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, f))]
    return render_template('index.html', folders=folders)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['admin'] = True
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/gallery/<folder>')
def gallery(folder):
    folder_path = os.path.join(UPLOAD_FOLDER, folder)
    if not os.path.exists(folder_path):
        return "Folder not found", 404
    images = os.listdir(folder_path)
    return render_template('gallery.html', folder=folder, images=images, admin=session.get('admin', False))

@app.route('/upload/<folder>', methods=['POST'])
def upload(folder):
    if not session.get('admin'):
        return "Unauthorized", 403

    if 'file' not in request.files:
        return redirect(request.referrer)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.referrer)
    if file and '.' in file.filename and \
       file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        filename = secure_filename(file.filename)
        target_folder = os.path.join(UPLOAD_FOLDER, folder)
        os.makedirs(target_folder, exist_ok=True)
        file.save(os.path.join(target_folder, filename))
    return redirect(url_for('gallery', folder=folder))

@app.route('/delete/<folder>/<filename>', methods=['POST'])
def delete_image(folder, filename):
    if not session.get('admin'):
        return "Unauthorized", 403

    path = os.path.join(UPLOAD_FOLDER, folder, filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for('gallery', folder=folder))

if __name__ == '__main__':
    app.run(debug=False)
