from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
import os
from io import BytesIO

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////mnt/D/GitHub/python/updown/file.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'file.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class FileContents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    data = db.Column(db.LargeBinary)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['inputFile']

    newFile = FileContents(name=file.filename, data=file.read())
    db.session.add(newFile)
    db.session.commit()

    return 'Saved ' + file.filename + ' to the database'

@app.route('/download')
def download():
    file_data = FileContents.query.filter_by(id=2).first()
    return send_file(BytesIO(file_data.data),attachment_filename='download.pdf', as_attachment=True)

if __name__ =='__main__':
    app.run()