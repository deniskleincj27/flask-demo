import functools

from flask import (
  Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from demo.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')
print('auth __name__: ', __name__, ' bp: ', bp)

@bp.route('/register', methods=('GET', 'POST'))
def register():

  print('auth register method: ', request.method)
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None

    print('auth register username: ', username)
    if not username:
      error = 'Username is required.'
    elif not password:
      error = 'Password is required.'
    elif db.execute(
      'SELECT id FROM user WHERE username = ?', (username,)
    ).fetchone() is not None:
      error = 'User {} is already registered.'.format(username)

    if error is None:
      db.execute(
        'INSERT INTO user (username, password) VALUES (?, ?)',
        (username, generate_password_hash(password))
      )
      db.commit()
      return redirect(url_for('auth.login'))

    flash(error)

  return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():

  print('auth login method: ', request.method)
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None
    user = db.execute(
      'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
      error = 'Incorrect username.'
    elif not check_password_hash(user['password'], password):
      error = 'Incorrect password.'

    if error is None:
      session.clear()
      session['user_id'] = user['id']
# dkl      return redirect(url_for('index'))
      return redirect(url_for('test'))

    flash(error)

  return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
  user_id = session.get('user_id')
#  print('auth load_logged_in_user: ', request.method, ' user_id: ', user_id)
  if user_id is None:
    g.user = None
  else:
    g.user = get_db().execute(
      'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()
#  print('auth load_logged_in_user g.user: ', g.user)

@bp.route('/logout')
def logout():
  print('auth logout ')
  session.clear()

  return redirect(url_for('index'))

def login_required(view):
  print('login_required')

  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if g.user is None:
      print('login_required auth.login')
      return redirect(url_for('auth.login'))

    return view(**kwargs)

  return wrapped_view