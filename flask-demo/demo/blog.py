import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.datastructures import ImmutableMultiDict, FileStorage
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
import pymongo
import pprint
import json
import itertools

import importlib
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS, DATA, IMAGES, TEXT
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, StringField, SubmitField, TextAreaField, HiddenField, Field, Flags
from wtforms.validators import DataRequired
from wtforms.meta import DefaultMeta
from demo.db import get_db
from .__init__ import demoset

file_ext = ['txt', 'png', 'xlsx', 'jpeg', 'svg', 'bmp']

demo_database = 'demo_database'
bp = Blueprint('blog', __name__)

class UploadForm(FlaskForm):

  meta = DefaultMeta()
  message = HiddenField("Masge", validators=[DataRequired()], _meta = meta)

  demo = FileField(validators=[FileAllowed(file_ext, 'This extension is not allowed!'), FileRequired('File was empty!')])
  submit = SubmitField('Upload')

def load_data():

  client = pymongo.MongoClient("mongodb://localhost:27018")
  mdb = client[demo_database]
  collection = mdb.data_list

  dlist = []
  for data in collection.find():
    dic = {}
    dic.update({'file_name' : data['file_name']})
    dic.update({'location' : data['location']})
    dlist.append(dic)

  return dlist

@bp.route("/blog.index")
def index():

  posts = load_data()

  return render_template("blog/index.html", posts = posts) # , form = form)

@bp.route("/blog.download", methods = ('GET', 'POST'))
def download():

  if request.method == 'POST':

    posts = load_data()
    if len(posts) == 0:
      return render_template('blog/index.html', posts = posts) # "POST /blog.download HTTP/1.1" 200 -

    form = UploadForm(message = ('message', "hello download"), csrf_enabled=False)
    path = os.getcwd()
    path = path.replace('/flask-demo', '')
    posts = request.form.getlist('cbox_name')

    error = None
    for post in posts:
      post = post.replace("\'", "\"")
      post = json.loads(post)
      fname = path + post.get('location')[1:] + post.get('file_name').strip()

      try:
        f = open(fname, "rb")
        form.demo.data = FileStorage(stream = f, filename = post.get('file_name').strip(), content_type=('text/plain'))
        if len(form.errors) != 0:
          error = form.errors
          break

        if form.validate_on_submit():
          filename = demoset.save(form.demo.data)
          file_url = demoset.url(filename)

      except Exception as e:
        print("download error ", e)

    if error is None:
      error = 'Transfert Completed'
    flash(error, 'info')

    posts = load_data()
    return render_template('blog/index.html', posts = posts) # "POST /blog.download HTTP/1.1" 200 -
