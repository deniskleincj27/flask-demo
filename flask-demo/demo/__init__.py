import os
import pprint

from flask import Flask
from flask_uploads import UploadSet, configure_uploads, patch_request_class, DOCUMENTS, DATA, IMAGES, TEXT

from . import auth, db, blog, home

demoset = UploadSet('demoset', TEXT + DOCUMENTS + IMAGES)

def create_app(test_config=None):

  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_pyfile('demo.cfg')

  # ensure the instance folder exists
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass

  db.init_app(app)

  app.register_blueprint(auth.bp)
  app.register_blueprint(blog.bp)
  app.register_blueprint(home.bp)

  configure_uploads(app, demoset)
  patch_request_class(app)  # set maximum file size, default is 16MB
  app.add_url_rule('/home', endpoint = 'home')

  return app

