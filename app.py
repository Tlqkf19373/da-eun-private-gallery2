from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
import os
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # 세션용 키

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ADMIN_PASSWORD = 'ppoo6689'

# 관리자 로그인 확인용 데코레이터
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            flash('관리자 로그인이 필요합니다.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# 확장자 확인
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 홈 - 사진첩 목록
@app.route('/')
def index():
    folders = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', folders=folders, logged_in=session.get('logged_in'))

# 각 사진첩 보기
@app.route('/gallery/<folder>')
def gallery(folder):
    folder_path = os.path.join(UPLOAD_FOLDER, folder)
    if not os.path.exists(folder_path):
        return "폴더가 존재하지 않습니다.", 404
    images = os.listdir(folder_path)
    return render_template('gallery.html', folder=folder, images=images, logged_in=session.get('logged_in'))

# 관리자 로그인
@app.route('/admin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('로그인 성공')
            return redirect(url_for('index'))
        else:
            flash('비밀번호가 틀렸습니다.')
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('로그아웃 되었습니다.')
    return redirect(url_for('index'))

# 업로드
@app.route('/upload/<folder>', methods=['POST'])
@login_required
def upload(folder):
    if 'file' not in request.files:
        return '파일이 없습니다.', 400
    file = request.files['file']
    if file.filename == '':
        return '선택된 파일이 없습니다.', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        folder_path = os.path.join(UPLOAD_FOLDER, folder)
        os.makedirs(folder_path, exist_ok=True)
        file.save(os.path.join(folder_path, filename))
        return redirect(url_for('gallery', folder=folder))
    return '허용되지 않는 파일 형식입니다.', 400

# 삭제
@app.route('/delete/<folder>/<filename>')
@login_required
def delete(folder, filename):
    file_path = os.path.join(UPLOAD_FOLDER, folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('gallery', folder=folder))
