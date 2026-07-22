# import configuration file as ac
import app_configuration
from app_configuration import db
# declare db by retrieving sqlalchemy instant from configuration file
# db = ac.db

# creating an admins model(table) of database by class
class Admins(db.Model):
    '''
        sno, name, email, phone, username, password, date
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=True, nullable=True)
    date = db.Column(db.String, nullable=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.username)

# creating a Posts model(table) of database by class
class Posts(db.Model):
    '''
        sno, title, slug, content, date, img_file, subtitle, admin
    '''
    # __searchable__ = ['title', 'subtitle', 'admin']
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, nullable=False)
    no_of_paras = db.Column(db.Integer, nullable=False)
    # images = db.Column(db.String, nullable=True)
    content = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    img_file = db.Column(db.String, nullable=True)
    subtitle = db.Column(db.String, nullable=True)
    admin = db.Column(db.String, nullable=False)
    likes = db.Column(db.Integer, nullable=False, default=0)
    # dislikes = db.Column(db.Integer, nullable=False, default=0)
    # whooshalchemy.whoosh_index(app, Posts)

# creating a Likes model(table) of database by class
class Likes(db.Model):
    username = db.Column(db.String, primary_key = True)
    postslug = db.Column(db.String, nullable=False, primary_key = True)

# creating a Comments model(table) of database by class
class Comments(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String, nullable=False)
    post = db.Column(db.String, nullable=False)
    commentsonpost = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)

# creating a Replies model(table) of database by class
class Replies(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    commentid = db.Column(db.Integer, nullable=False)
    user = db.Column(db.String, nullable = False)
    reply = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)

# creating a Contacts model(table) of database by class
class Contacts(db.Model):
    '''
        sno, name, phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone_num = db.Column(db.String, nullable=False)
    msg = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)

@app_configuration.login_manager.user_loader
def load_user(username):
    return Admins.query.filter_by(username=username).first()