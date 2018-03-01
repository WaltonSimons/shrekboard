from shrekboard import app, db


class Board(db.Model):
    name = db.Column(db.String, primary_key=True)
    full_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    threads = db.relationship('Thread', backref=db.backref('board', lazy=True))
    post_counter = db.Column(db.Integer, default=0)

    def get_page(self, page_number):
        threads = sorted(self.get_threads(), key=lambda thread: thread.last_reply_date, reverse=True)
        return threads[page_number * 5: page_number * 5 + 5]

    def get_threads(self):
        return [thread for thread in self.threads if len(thread.replies) > 0]

    @property
    def last_page(self):
        length = len(self.threads)
        return int(length/5) + (1 if length%5 != 0 else 0)


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer)
    username = db.Column(db.String)
    user_ip = db.Column(db.String)
    tripcode = db.Column(db.String)
    options = db.Column(db.String)
    content = db.Column(db.Text)
    subject = db.Column(db.String)
    filename = db.Column(db.String)
    thumbnail_name = db.Column(db.String)
    original_filename = db.Column(db.String)
    file_res = db.Column(db.String)
    file_size = db.Column(db.String)
    date = db.Column(db.DateTime)
    main = db.Column(db.Boolean)
    thread_id = db.Column(db.String, db.ForeignKey('thread.id'), nullable=False)

    @property
    def html_content(self):
        return self.content.replace('\n', '</br>')

    @property
    def content_lines(self):
        return self.content.split('\n')


class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board_name = db.Column(db.String, db.ForeignKey('board.name'), nullable=False)
    replies = db.relationship('Reply', backref=db.backref('thread', lazy=True))

    @property
    def main_reply(self):
        for reply in self.replies:
            if reply.main:
                return reply

    @property
    def all_replies(self):
        return sorted([reply for reply in self.replies if not reply.main], key=lambda reply: reply.date)

    @property
    def last_replies(self):
        return sorted([reply for reply in self.replies if not reply.main], key=lambda reply: reply.date)[-5:]

    @property
    def last_reply_date(self):
        return max([reply.date for reply in self.replies if not ('sage' in reply.options and not reply.main)])

    @property
    def board_id(self):
        return self.main_reply.board_id


class BannedIP(db.Model):
    ip = db.Column(db.String, primary_key=True)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String, nullable=False)
