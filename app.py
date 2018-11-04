from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
import os
from io import BytesIO
from flask import send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

__author__ = 'Vladan M. Kostic'

basedir = os.path.abspath(os.path.dirname(__file__))
app_root = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'file.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class FileContents(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    data = db.Column(db.LargeBinary)

class SlikaPregledForm(FlaskForm):
    izbor_slika = StringField('Unesi sifru slike:', validators=[DataRequired()])
    submit = SubmitField('Prikazi')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/up', methods=['GET','POST'])
def up():
    return render_template('upload.html')

@app.route('/upload', methods=['GET','POST'])
def upload():

    target = os.path.join(app_root, 'static/images/')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    file = request.files['file']

    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print(destination)
        file.save(destination)

        newFile = FileContents(name=file.filename, data=file.read())
        db.session.add(newFile)
        db.session.commit()

    return render_template("complete.html", filename=file.filename)

@app.route('/show', methods=['GET','POST'])
def show():
    search = SlikaPregledForm(request.form)
    if request.method == 'POST':
        return search_results_slika(search)

    return render_template('show.html',title='Pregled', form=search)

#app.route('/download')
def search_results_slika(search):
    file = FileContents.query.filter_by(id=search.data['izbor_slika']).first()
    #return send_from_directory("images", file.name) #Linija koda koja nam je potreba kada pozivamo bez pripremljene stranice
    return render_template('/download.html', file=file) #Linija koda koja nam je potreba kada pozivamo sa pripremljenom stranicom

@app.route('/ch', methods=['GET','POST'])
def ch():
    return render_template('change.html', title='Change')

@app.route('/change', methods=['GET','POST'])
def change():
    target = os.path.join(app_root, 'images/')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    file = request.files['file']
    old_id = request.form['img_id']
    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print(destination)
        file.save(destination)

    existFile = FileContents.query.filter_by(id = old_id).first()
    existFile.name = file.filename
    existFile.data = file.read()
    db.session.commit()

    return render_template("complete_change.html", filename=file.filename)

if __name__ =='__main__':
    app.run()