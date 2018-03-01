import crypt
import string
import bcrypt

import os

from models import Reply, BannedIP, Board, Admin, Thread
from shrekboard import ALLOWED_EXTENSIONS, app, db
import random
from datetime import datetime
from PIL import Image


def trip(pw):
    pw = pw[:8]
    salt = (pw + "H.")[1:3]
    tripcode = crypt.crypt(pw, salt)
    return tripcode[-10:]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_thumbnail(file):
    img = Image.open(file)
    ratio = min(250 / img.width, 300 / img.height)
    img.thumbnail([dim * ratio for dim in img.size], Image.ANTIALIAS)
    return img


def create_reply(request, thread_id, main, board_name):
    username = request.form.get('username')
    split_username = username.split('#', 1)
    user = split_username[0]
    if user == '':
        user = 'Anonymous'
    tripcode = split_username[1] if len(split_username) > 1 else None
    if tripcode:
        tripcode = trip(tripcode)
    options = request.form.get('options')
    subject = request.form.get('subject')
    content = request.form.get('content')
    file = request.files.get('upfile', False)
    filename = ''
    original_filename = ''
    thumbnail_name = ''
    if file and allowed_file(file.filename):
        original_filename = file.filename
        filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        thumbnail_name = filename + '_thumb'
        filename += '.' + original_filename.rsplit('.', 1)[1].lower()
        thumbnail_name += '.' + original_filename.rsplit('.', 1)[1].lower()
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        thumbnail = create_thumbnail(file)
        thumbnail.save(os.path.join(app.config['UPLOAD_FOLDER'], thumbnail_name))
    board = db.session.query(Board).filter_by(name=board_name)[0]
    board_id = board.post_counter + 1
    board.post_counter = board_id
    if not main:
        threads = db.session.query(Thread).filter_by(board_name=board_name)
        thread = [thread for thread in threads if thread.board_id == thread_id][0]
        thread_id = thread.id
    reply = Reply(
        board_id=board_id,
        username=user,
        user_ip=request.remote_addr,
        content=content,
        options=options,
        subject=subject,
        tripcode=tripcode,
        filename=filename,
        thumbnail_name=thumbnail_name,
        original_filename=original_filename,
        date=datetime.now(),
        main=main,
        thread_id=thread_id,
    )
    db.session.add(reply)
    db.session.commit()
    return reply


def check_banned_ip(ip):
    return db.session.query(BannedIP).filter_by(ip=ip).count() > 0


def create_admin(password):
    hashed_password = bcrypt.hashpw(password, salt=bcrypt.gensalt())
    admin = Admin(password=hashed_password)
    db.session.add(admin)
    db.session.commit()


def check_admin(password):
    admins = db.session.query(Admin).all()
    for admin in admins:
        if bcrypt.checkpw(password.encode('utf-8'), admin.password):
            return True
    return False
