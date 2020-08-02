from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

from demo.auth import login_required
from demo.db import get_db
from . import blog

bp = Blueprint('home', __name__)

@bp.route('/')
def index():

  db = get_db()
  posts = db.execute(
    'SELECT p.id, title, body, created, author_id, username'
    ' FROM post p JOIN user u ON p.author_id = u.id'
    ' ORDER BY created DESC'
  ).fetchall()

  return render_template('home/home.html', posts=posts)

@bp.route("/validate", methods = ('GET', 'POST'))
def validate():

  if request.method == 'POST':

    username = request.form['username']
    password = request.form['password']

    error = None

    if not username:
      error = 'Username is required.'
    elif not password:
      error = 'Password is required.'

    if error is not None:
      flash(error)
      return render_template('home/home.html')

    db = get_db()
    if request.form['action'] == 'Log In':

      user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
      ).fetchone()

      if user is None:
        error = 'Incorrect username.'
      elif not check_password_hash(user['password'], password):
        error = 'Incorrect password.'

      if error is not None:
        flash(error)
        return render_template('home/home.html')

      session.clear()
      session['user_id'] = user['id']

      return redirect(url_for("blog.index"))

    # register
    if request.form['action'] == 'Register':

      if db.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone() is not None:
        error = 'User {} is already registered.'.format(username)
      else:
        db.execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (username, generate_password_hash(password))
          )
        db.commit()
        error = 'Hello \'{}\', please Log In.'.format(username)

      flash(error)
      return render_template('home/home.html')



