from flask import render_template, redirect, request, abort, session, g, url_for, send_from_directory
from werkzeug.utils import secure_filename

from models import *
from shrekboard import app, db

from utils import *


@app.before_request
def before_request():
    if check_banned_ip(request.remote_addr) and not ('banned' in request.base_url or '.css' in request.base_url):
        return redirect(url_for('banned'))
    g.boards = db.session.query(Board).order_by(Board.name.asc()).all()
    g.authorized = session.get('authorized', False)


@app.route('/')
def index():
    return render_template(
        "index.html",
    )


@app.route('/<string:board_name>/<int:page_number>')
@app.route('/<string:board_name>/')
def board_view(board_name, page_number=0):
    boards = db.session.query(Board).filter_by(name=board_name)
    if boards.count() < 1:
        abort(404)
    board = boards[0]
    threads = db.session.query(Thread).filter_by(board_name=board_name)
    return render_template(
        "board.html",
        board=board,
        threads=threads,
        page_number=page_number,
        title='/{}/ - {}'.format(board_name, board.full_name)
    )


@app.route('/add_board', methods=['POST'])
def add_board():
    if request.method == 'POST':
        name = request.form['board_name']
        full_name = request.form['full_name']
        description = request.form['description']
        existing_board = db.session.query(Board).filter_by(name=name)
        if existing_board.count() > 0 or not session.get('authorized'):
            return 'A board with this name already exists!'
        else:
            board = Board(name=name, full_name=full_name, description=description)
            db.session.add(board)
            db.session.commit()
            return redirect(url_for('board_view', board_name=name))


@app.route('/<string:board_name>/create_thread', methods=['POST'])
def create_thread(board_name):
    thread = Thread(
        board_name=board_name
    )
    db.session.add(thread)
    db.session.commit()
    create_reply(request, thread.id, True, board_name)
    return redirect(url_for('board_view', board_name=board_name))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/<string:board_name>/thread/<int:thread_id>')
def thread_view(board_name, thread_id):
    boards = db.session.query(Board).filter_by(name=board_name)
    threads = db.session.query(Thread).filter_by(board_name=board_name)
    threads = [thread for thread in threads if thread.board_id == thread_id]
    if boards.count() + len(threads) < 2:
        abort(404)
    board = boards[0]
    thread = threads[0]
    return render_template(
        "thread.html",
        board=board,
        thread=thread,
        title='{} - {} - {}'.format(board_name, thread.main_reply.content[:30], board.full_name)
    )


@app.route('/<string:board_name>/thread/<int:thread_id>/add_reply', methods=['POST'])
def add_reply(board_name, thread_id):
    create_reply(request, thread_id, False, board_name)
    return redirect(url_for('thread_view', board_name=board_name, thread_id=thread_id))


@app.route('/banned')
def banned():
    return render_template(
        "banned.html",
    )


@app.route('/admin_panel', methods=['POST', 'GET'])
def admin_panel():
    if request.method == 'POST':
        password = request.form.get('password')
        if check_admin(password):
            session['authorized'] = True
        else:
            return 'Wrong password!'
    if not session.get('authorized', False):
        return render_template(
            "admin_login.html",
        )
    else:
        return render_template(
            "admin_panel.html",
        )


@app.route('/ban_ip', methods=['POST'])
def ban_ip():
    if session.get('authorized'):
        ip = request.form.get('ip')
        banned_ip = BannedIP(ip=ip)
        db.session.add(banned_ip)
        db.session.commit()
        return 'IP: {} was banned'.format(ip)
    else:
        return 'You do not have privileges to use this action.'
