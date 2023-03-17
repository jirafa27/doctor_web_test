import os
import glob

from flask import render_template, request, flash, redirect
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db
from models import File
from .app import app
from helpers import get_hash_md5
from sqlalchemy import exc
from flask import send_from_directory

auth = HTTPBasicAuth()

users = {
    "john": generate_password_hash("hello"),
    "susan": generate_password_hash("bye")
}


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/')
@auth.login_required
def index():
    print(auth.username())
    return render_template("index.html")


@app.route('/logout')
@auth.login_required
def logout():
    return redirect('/')


@app.route('/add', methods=['POST'])
@auth.login_required
def add():
    if request.method == 'POST':
        f = request.files['file']
        if f.filename == '':
            flash('No selected file')
            return redirect('/')
        extension = f.filename.split('.')[1]
        filename = get_hash_md5(f)
        directory = filename[0:2]
        path = os.path.join(app.config['UPLOAD_FOLDER'],
                            directory)
        if not os.path.exists(path):
            os.makedirs(path)
        f.stream.seek(0)
        try:
            db.session.add(File(hash_sum=filename, username=request.authorization['username']))
            db.session.commit()
        except exc.IntegrityError as e:
            return render_template("result.html", message="File already exists", name=filename)
        f.save(os.path.join(path,
                            f'{filename}.{extension}'))
        return render_template("result.html", message="File uploaded successfully", name=filename)


@app.route('/get', methods=['POST'])
@auth.login_required
def get():
    if request.method == 'POST':
        filename = request.form.get('hash')
        print(filename)
        if filename == '':
            flash('No selected file')
            return redirect('/')
        directory = filename[0:2]
        path = os.path.join(app.config['UPLOAD_FOLDER'],
                            directory, filename)
        files = [filename for filename in glob.glob(f'{path}.*')]
        if not files:
            return render_template("result.html", message="File does not exists", name=filename)
        path = path + '.' + files[0].split('.')[-1]
        return send_from_directory(f"{os.getcwd()}/{app.config['UPLOAD_FOLDER']}/{directory}", path.split('/')[-1],
                                   as_attachment=True)


@app.route('/delete', methods=['POST'])
@auth.login_required
def delete():
    if request.method == 'POST':
        filename = request.form.get('hash')
        if filename == '':
            flash('No selected file')
            return redirect('/')
        directory = filename[0:2]
        path = os.path.join(app.config['UPLOAD_FOLDER'],
                            directory, filename)
        files = [filename for filename in glob.glob(f'{path}.*')]
        if not files:
            return render_template("result.html", message="File does not exists", name=filename)
        if not db.session.query(File).filter(File.hash_sum==filename, File.username==request.authorization['username']).all():
            return render_template("result.html", message=f"File has not created by user. It can not be deleted", name=filename)

        for f in files:
            os.remove(f)
        db.session.query(File).filter(File.hash_sum==filename).delete()
        db.session.commit()
        if not len(os.listdir(os.path.join(app.config['UPLOAD_FOLDER'],
                                directory))):
            os.rmdir(os.path.join(app.config['UPLOAD_FOLDER'],
                                directory))
        return render_template("result.html", message="File deleted successfully", name=filename)


if __name__ == '__main__':
    app.run(debug=True)
