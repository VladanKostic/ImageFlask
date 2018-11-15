from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms_alchemy.fields import QuerySelectField

import os

__author__ = 'Vladan M. Kostic'

basedir = os.path.abspath(os.path.dirname(__file__))
app_root = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'build-new-code'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'file.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class FileContents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_of_person = db.Column(db.String(64))
    name_of_file = db.Column(db.String(128))
    data = db.Column(db.LargeBinary)

    def __repr__(self):
        return '{}'.format(self.name_of_file)

def choice_query():
    return FileContents.query.all()

class ChiceImageForm(FlaskForm):
    opts = QuerySelectField(query_factory=choice_query,  get_label='name_of_file', allow_blank=False)

class ChicePersonForChangeImageForm(FlaskForm):
    opts_id = QuerySelectField(query_factory=choice_query, get_label='id', allow_blank=False)

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

    person = request.form['person']
    file = request.files['file']
    print(file, ' ', person)

    filename = file.filename
    destination = "/".join([target, filename])
    print(destination)
    file.save(destination)

    thedata = open(destination, 'rb').read()
    print(thedata)

    newFile = FileContents(name_of_person=person, name_of_file=file.filename, data=thedata)
    db.session.add(newFile)
    db.session.commit()

    return render_template("complete.html", filename=file.filename)

@app.route('/show', methods=['GET','POST'])
def show():
    form = ChiceImageForm()
    if form.validate_on_submit():
        print(form.opts.data)
        file = FileContents.query.filter_by(name_of_file=str(form.opts.data)).first()
        return render_template('/download.html', file=file)

    return render_template('show.html',title='Show', form=form)

@app.route('/change', methods=['GET','POST'])
def change():
    form = ChicePersonForChangeImageForm()
    if form.validate_on_submit():
        target = os.path.join(app_root, 'static/images/')
        print(target)

        file = request.files['file']
        old_name_of_file = form.opts_id.data
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print(destination)
        file.save(destination)
        print(old_name_of_file)

        existFile = FileContents.query.filter_by(name_of_file = str(old_name_of_file)).first()
        print(existFile)
        destination_del = "/".join([target, existFile.name_of_file])
        print(destination_del)
        os.remove(destination_del)

        existFile.name_of_file = file.filename
        existFile.data = file.read()
        db.session.commit()
        return render_template("complete_change.html", filename=file.filename)

    return render_template('change.html', title='Change', form=form)

if __name__ =='__main__':
    app.run()
