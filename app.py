from flask import Flask, render_template, request, redirect, url_for, session
import os
from PIL import Image

app = Flask(__name__)
app.secret_key = "ppoo6689"

UPLOAD_FOLDER = "static/uploads"
THUMB_FOLDER = "thumbs"
ADMIN_PASSWORD = "ppoo6689"

# 초기 폴더 생성
def create_folders():
    for folder in ["book1", "book2"]:
        folder_path = os.path.join(UPLOAD_FOLDER, folder)
        thumb_path = os.path.join(folder_path, THUMB_FOLDER)
        os.makedirs(thumb_path, exist_ok=True)

def generate_thumbnail(image_path, thumb_path):
    size = (300, 300)
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size)
            img.save(thumb_path)
    except Exception as e:
        print(f"썸네일 생성 실패: {e}")

@app.route("/")
def index():
    return redirect(url_for("gallery"))

@app.route("/gallery")
def gallery():
    folders = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, f))]
    is_admin = session.get("is_admin", False)
    return render_template("gallery.html", folders=folders, is_admin=is_admin)

@app.route("/gallery/<folder>")
def folder_view(folder):
    thumb_dir = os.path.join(UPLOAD_FOLDER, folder, THUMB_FOLDER)
    thumbs = sorted(os.listdir(thumb_dir)) if os.path.exists(thumb_dir) else []
    is_admin = session.get("is_admin", False)
    return render_template("folder.html", folder=folder, thumbs=thumbs, is_admin=is_admin)

@app.route("/upload/<folder>", methods=["POST"])
def upload(folder):
    if not session.get("is_admin"):
        return "관리자 권한이 필요합니다.", 403
    file = request.files["file"]
    if file:
        save_path = os.path.join(UPLOAD_FOLDER, folder, file.filename)
        file.save(save_path)
        thumb_path = os.path.join(UPLOAD_FOLDER, folder, THUMB_FOLDER, file.filename)
        generate_thumbnail(save_path, thumb_path)
    return redirect(url_for("folder_view", folder=folder))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("gallery"))
        return "비밀번호가 틀렸습니다", 403
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("gallery"))

if __name__ == "__main__":
    create_folders()
    app.run(debug=True)
