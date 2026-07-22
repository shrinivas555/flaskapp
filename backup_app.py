import werkzeug.utils
from flask import Flask, render_template, send_file, request, redirect, url_for, session, flash
import math
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
from flask_mail import Mail, Message
import os
import werkzeug
from flask_bcrypt import Bcrypt, check_password_hash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
import random
from flask_share import Share
from fpdf import FPDF

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.session_protection="strong"
login_manager.login_view = "login"

local_server = True
with open ("config.json", "r") as c:
    params = json.load(c)["params"]

app = Flask(__name__)

share = Share(app)

bcrypt.init_app(app)
login_manager.init_app(app)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_PORT = "465",
    MAIL_USE_SSL = True,
    MAIL_USE_TLS = False,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)
mail = Mail(app)

if(local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']
db = SQLAlchemy(app)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["WHOOSH_BASE"] = "whoosh"

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

class Posts(db.Model):
    '''
        sno, title, slug, content, date, img_file, subtitle, admin
    '''
    # __searchable__ = ['title', 'subtitle', 'admin']
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, nullable=False)
    no_of_paras = db.Column(db.String, nullable=False)
    images = db.Column(db.String, nullable=True)
    content = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    img_file = db.Column(db.String, nullable=True)
    subtitle = db.Column(db.String, nullable=True)
    admin = db.Column(db.String, nullable=False)
    likes = db.Column(db.Integer, nullable=False, default=0)
    # dislikes = db.Column(db.Integer, nullable=False, default=0)
# whooshalchemy.whoosh_index(app, Posts)

class Likes(db.Model):
    username = db.Column(db.String, primary_key = True)
    postslug = db.Column(db.String, nullable=False, primary_key = True)

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String, nullable=False)
    post = db.Column(db.String, nullable=False)
    commentsonpost = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)

class Replies(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    commentid = db.Column(db.Integer, nullable=False)
    user = db.Column(db.String, nullable = False)
    reply = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)

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

@login_manager.user_loader
def load_user(username):
    print(username)
    return Admins.query.filter_by(username=username).first()

@app.route("/login", methods = ['GET', 'POST'])
def login(url):
    if request.method == 'POST':
        print(url)
        username = request.form.get('uname')
        password = request.form.get('pass')
        user = Admins.query.filter_by(username=username).first()
        # print(user)
        # try:
            # print(user.password)
        if check_password_hash(user.password, password):
            login_user(user)
            # print(load_user(user))

            return redirect(str(url))
        else:
            flash("Invalid username/password", "danger")
        # except Exception as e:
        #     flash("invalid username", "danger")

    return render_template("login.html", params=params)

@app.route("/", methods = ['GET', 'POST'])
def home():
    # query = request.args.get('search')
    page = request.args.get('page',1)
    print(page)
    # print(type(page))
    posts = Posts.query.filter_by().order_by(Posts.date.desc()).all()
    total_posts = len(posts)
    posts_per_page = params['no_of_posts']
    total_pages = math.ceil(total_posts/posts_per_page)
    # print(type(page))
    starting_index = (int(page) - 1) * posts_per_page
    posts_content = posts[starting_index:starting_index+posts_per_page]

    return render_template("index.html", params=params, current_page = int(page), total_pages=total_pages, posts_content=posts_content, current_user=current_user)


@app.route("/search")
def search_query():
    base_url = request.base_url
    page = request.args.get('page',1)
    search_query = request.args.get('search')
    posts = search(search_query)
    total_posts = len(posts)
    posts_per_page = params['no_of_posts']
    total_pages = math.ceil(total_posts / posts_per_page)
    # print(type(page))
    starting_index = (int(page) - 1) * posts_per_page
    posts_content = posts[starting_index:starting_index + posts_per_page]
    return render_template("index.html", params=params,search_query=search_query, base_url=base_url, current_page = int(page), total_pages=total_pages, posts_content=posts_content, current_user=current_user)
def search(query):
    search_result = []
    posts = Posts.query.filter_by().order_by(Posts.date.desc()).all()
    for post in posts:
        if query.upper() in post.title.upper():
            search_result.append(post)
        if query.upper() in post.admin.upper():
            if post not in search_result:
                search_result.append(post)
    return search_result

@app.route("/about")
def about():
    return render_template("about.html", params=params)

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    '''get the data from the contact form '''
    if request.method=="POST":
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        message = request.form.get('message')
        date = datetime.now()
        '''insert the data in the contacts table of codingthunder database'''
        '''
               sno, name, phone_num, msg, date, email
           '''
        entry = Contacts(name=name, phone_num=phone, msg=message, email=email, date=date)
        db.session.add(entry)
        db.session.commit()
        flash("Thanks for contacting us, Your form is submitted successfully", "success")
        email_msg = Message('new message from ' + name, sender=email, recipients=[params['gmail-user']])
        email_msg.body = message + "\n" + phone
        mail.send(email_msg)

    return render_template("contact.html", params=params)

@app.route('/post/<string:post_slug>/downloadpdf')
def download_pdf(post_slug):
    create_pdf(post_slug)
    post = Posts.query.filter_by(slug=post_slug).first()
    filename = post.title + '_' + post_slug + '.pdf'
    file_path = os.path.join(params['upload_location'], filename)
    return send_file(file_path, as_attachment=True)

def create_pdf(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    content = post.content
    paragraphs = content.split('|')
    filename = post.title + '_' + post_slug + '.pdf'
    pdf = FPDF('P', 'mm', 'A4')
    pdf.set_top_margin(20)
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.set_auto_page_break(True, 15)
    # pdf.set_text_color(3,15,252)
    pdf.add_page()

    def subtitle_font():
        pdf.set_font('Arial', 'I', 12)
        pdf.multi_cell(190, 8, txt='- "' + post.subtitle + '"', align='C', border=0)

    pdf.set_font('Arial','BU',16)
    pdf.cell(190, 10, txt=post.title,ln=1, align='C', border=0)

    subtitle_font()

    pdf.set_font('Arial', '', 10)
    pdf.cell(190, 5, txt='Posted on: ' + str(post.date), ln=1, align='R', border=0)
    pdf.cell(190, 5, txt='Posted by: ' + post.admin, ln=1, align='R', border=0)
    pdf.cell(190, 5, txt='', ln=1, align='R', border=0)

    pdf.set_font('Arial', '', 12)
    for i in range(len(paragraphs)):
        pdf.cell(190, 5, txt='', ln=1, align='R', border=0)
        pdf.multi_cell(190, 5, txt=paragraphs[i], align='L', border=0)

    save_location = os.path.join(params['upload_location'], filename)
    return pdf.output(save_location)

@app.route("/post/<string:post_slug>", methods = ['GET', 'POST'])
# @login_required
def post_route(post_slug):
    '''fetching the single post if they are multiple
    posts are filter by slug which is given to the function as paraaeter
    here slug is the database column and slug_post is the backend variable'''
    # login()
    # if login() == "authentication successful":
    if current_user.is_authenticated:
        recorded_like = Likes.query.filter_by(postslug=post_slug, username=current_user.username).first()
        post = Posts.query.filter_by(slug=post_slug).first()
        content = post.content
        paras = content.split('|')
        comments = Comments.query.filter_by(post=post_slug).all()

        return render_template("post.html",recorded_like=recorded_like, params=params, post=post, paras=paras, comments=comments)

    return login(str(url_for('home')))

@app.route('/post/<string:postslug>/comment', methods = ['GET', 'POST'])
@login_required
def comments(postslug):
    if request.method == 'POST':
        comment = request.form.get('comment')
        user = current_user.username
        date = datetime.now()
        post = postslug
        entry = Comments(user=user, post=post, commentsonpost=comment, date=date)
        db.session.add(entry)
        db.session.commit()
        return redirect('/post/' + postslug)
    return redirect('/post/' + postslug)

@app.route('/post/<string:postslug>/comment-<int:comment_id>', methods = ['GET', 'POST'])
@login_required
def reply(postslug, comment_id):
    replies = Replies.query.filter_by(commentid = comment_id).all()
    post = Posts.query.filter_by(slug=postslug).first()
    comment = Comments.query.filter_by(id=comment_id).first()
    if request.method == 'POST':
        reply = request.form.get('reply')
        user = current_user.username
        date = datetime.now()

        entry = Replies(commentid=comment_id, user=user, reply=reply, date=date)
        db.session.add(entry)
        db.session.commit()
        return redirect('/post/' + postslug)
    return render_template('replies.html', params=params, replies=replies, post=post, comment=comment)

@app.route('/likes', methods = ['GET', 'POST'])
@login_required
def likes():
    if request.method == 'POST':
        data = request.get_json()
        post_slug = data.get('post_slug')
        username = current_user.username
        recorded_like = Likes.query.filter_by(postslug=post_slug,username=username).first()
        print(recorded_like)
        print(type(recorded_like))
        if recorded_like == None:
            entry = Likes(postslug=post_slug, username=username)
            post = Posts.query.filter_by(slug=post_slug).first()
            post.likes += 1
            db.session.add(entry)
            db.session.commit()
            return redirect('/post/' + post_slug)
        else:
            return redirect('/post/' + post_slug)

@app.route('/dislikes', methods = ['GET', 'POST'])
@login_required
def dislikes():
    if request.method == 'POST':
        data = request.get_json()
        post_slug = data.get('post_slug')
        username = current_user.username
        recorded_like = Likes.query.filter_by(postslug=post_slug, username=username).first()
        post = Posts.query.filter_by(slug=post_slug).first()
        post.likes -= 1
        db.session.delete(recorded_like)
        db.session.commit()
        return redirect('/post/' + post_slug)

@app.route('/dashboard', methods = ['GET', 'POST'])
# @login_required
def dashboard():
    if current_user.is_authenticated:
        posts = Posts.query.filter_by(admin=current_user.username).all()
        return render_template('dashboard.html', params=params, posts=posts, admin = current_user.name)
    return login(str(url_for('dashboard')))
    # if request.method=='POST':
    #     username = request.form.get('uname')
    #     password = request.form.get('pass')
    #     user = Admins.query.filter_by(username=username).first()
    #     # print(user)
    #     try:
    #         # print(user.password)
    #         if check_password_hash(user.password, password):
    #             login_user(user)
    #             posts = Posts.query.filter_by(admin=current_user.username).all()
    #             flash("You are logged in successfully", "success")
    #             return render_template('dashboard.html', params=params, posts=posts, admin = current_user.name)
    #         else:
    #             flash("Invalid username/password", "danger")
    #     except Exception as e:
    #         flash("invalid username", "danger")
    # return render_template('login.html', params=params)

@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
@login_required
def edit(sno):
    # print(type(sno))
    # print(current_user.username)
    if request.method =='POST':
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        slug = request.form.get('slug')
        # content = request.form.get('content')
        no_of_paras = request.form.get('no_of_paras')
        img_file = request.form.get('bgimg')
        admin = current_user.username  #code for admin is to be written************************
        date = datetime.now()

        post = Posts.query.filter_by(sno=sno).first()
        post.title = title
        post.subtitle = subtitle
        post.slug = slug
        post.no_of_paras = no_of_paras
        # post.content = content
        post.img_file = img_file
        post.date = date
        db.session.commit()
        # noras_count = len(paras)
        flash("Your post saved successfully", "success")
        # return redirect('/edit/' + str(sno))
        return redirect("/edit/content/" + str(sno))
        # return render_template("edit_content.html", names=edit_names, params=params, paras=paras, post=post, admin = current_user.name)
    post =Posts.query.filter_by(sno=sno).first()
    # print(post)
    return render_template('edit.html', params=params, post=post, admin = current_user.name)

@app.route('/edit/content/<string:sno>', methods = ['GET', 'POST'])
@login_required
def edit_content(sno):
    int(sno)
    post = Posts.query.filter_by(sno=sno).first()
    edit_names = []
    for i in range(int(post.no_of_paras)):
        name = 'para' + str(i)
        edit_names.append(name)
    if request.method=='POST':
        post = Posts.query.filter_by(sno=sno).first()
        paras_list = []
        separator = '|'
        for i in range(post.no_of_paras):
            para = request.form.get(edit_names[i])
            paras_list.append(para)
        content = separator.join(paras_list)
        print(content)
        post.content = content
        db.session.commit()
        flash('Your post updated successfully', 'success')
        return redirect(url_for('dashboard'))
    content = post.content
    paras = content.split('|')
    return render_template("edit_content.html", names=edit_names, params=params, paras=paras, post=post, admin = current_user.name)

@app.route('/addnewpost', methods = ['GET', 'POST'])
# @login_required
def addnewpost():
    if current_user.is_authenticated:
        if request.method=='POST':
            title = request.form.get('title')
            subtitle = request.form.get('subtitle')
            slug = request.form.get('slug')
            no_of_paras = request.form.get('no_of_paras')
            content = "None"
            images = "no image uploaded"
            img_file = request.form.get('bgimg')
            admin = current_user.username  # code for admin is to be written************************
            date = datetime.now()
            global names
            names = []
            for i in range(int(no_of_paras)):
                name = 'para' + str(i)
                names.append(name)
            entry = Posts(title=title, images=images, subtitle=subtitle, slug=slug, content=content, img_file=img_file, admin=admin, date=date, no_of_paras=no_of_paras, )
            # print(names)
            db.session.add(entry)
            db.session.commit()
            flash("Your post detail saved successfully", "success")
            post = Posts.query.filter_by(slug=slug).first()
            return render_template("postcontent.html", names=names, params=params, post=post, admin = current_user.name)
        return render_template('addnewpost.html', params=params, admin = current_user.name)
    return login(str(url_for('addnewpost')))

@app.route("/addnewpost/content/<string:post_slug>", methods = ['GET', 'POST'])
@login_required
def addcontent(post_slug):
    if request.method == 'POST':
        post = Posts.query.filter_by(slug=post_slug).first()
        paras_list = []
        separator = '|'
        for i in range(post.no_of_paras):
            para = request.form.get(names[i])
            paras_list.append(para)
        content = separator.join(paras_list)
        # print(content)
        # print(paras_list)
        post.content = content
        db.session.commit()
        flash("Your post added successfully", "success")
        return redirect('/dashboard')
    return render_template("postcontent.html", params=params)

@app.route("/uploader", methods=['GET', 'POST'])
@login_required
def uploader():
    if request.method=='POST':
        f = request.files['file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], werkzeug.utils.secure_filename(f.filename)))
        flash("Uour file uploaded successfully", "success")
        return redirect("/dashboard")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are logged out uccessfully", "success")
    return redirect('/dashboard')

@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
@login_required
def delete(sno):
    post = Posts.query.filter_by(sno =sno).first()
    db.session.delete(post)
    db.session.commit()
    flash(f"Ypur post of Sno. {sno} deleted.", "success")
    return redirect('/dashboard')

@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    if request.method=='POST':
        '''
            sno, name, email, phone, username, password, date
        '''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        username = request.form.get('username')
        password = request.form.get('password')
        date = datetime.now()
        # try:
        entry = Admins(name=name, email=email, phone=phone, username=username,
                       password=bcrypt.generate_password_hash(password), date=date)
        db.session.add(entry)
        db.session.commit()
        flash("Your account created successfully", "success")
        return redirect('/login')
        # except Exception as e:
        #     flash("The username/ password already exists, please enter another username/password","danger")
        #     return redirect('/signup')

    return render_template("signup.html", params=params)

@app.route('/admin_profile')
@login_required
def admin_profile():
    info = Admins.query.filter_by(username = current_user.username).first()
    return render_template('profile.html', params=params, admin = current_user.name, info = info)

@app.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        username = request.form.get('username')
        password = request.form.get('password')
        password = bcrypt.generate_password_hash(password)
        date = datetime.now()

        admin = Admins.query.filter_by(username = current_user.username).first()

        admin.name = name
        admin.email = email
        admin.phone =phone
        admin.username = username
        admin.password = password
        admin.date = date
        db.session.commit()
        flash("Your profile updated successfully", "success")
        return redirect('/admin_profile')

    admin = Admins.query.filter_by(username=current_user.username).first()
    return render_template('edit_profile.html', params=params, admin=admin)

@app.route("/forgetpassword/sendotp", methods = ['GET', 'POST'])
def sendotp():
    if request.method=='POST':
        try:
            global registered_email
            registered_email = request.form.get('email')
            global otp_by_sys
            otp_by_sys = random.randint(100000, 999999)
            print(otp_by_sys)
            email_msg = Message('email validation OTP - PostMyArticle', sender=params['gmail-user'], recipients=[registered_email])
            email_msg.body = "email validation OTP for PostMyArticle forget password is: " + str(otp_by_sys) + " -\nPostMyArticle"
            mail.send(email_msg)

            return render_template("verifyotp.html", params=params)
        except Exception as e:
            print(e)
    return render_template("sendotp.html", params=params)

@app.route("/forgetpassword/verifyotp", methods = ['GET', 'POST'])
def verifyotp():
    if request.method=='POST':
        otp_from_admin = request.form.get('OTP')
        # print(otp_from_admin)
        if(int(otp_from_admin) == otp_by_sys):
            return render_template("setnewpassword.html", params=params)
        else:
            flash('FAILED! your OTP is incorrect. Please try again.', 'danger')
    return render_template("verifyotp.html", params=params)

@app.route('/forgetpassword/setnewpassword', methods = ['GET', 'POST'])
def setnewpassword():
    if request.method =='POST':
        info = Admins.query.filter_by(email = registered_email).first()
        trial_password = request.form.get('password')
        confirm_password = request.form.get('confirmpasswod')
        if(trial_password == confirm_password):
            old_password = info.password
            info.password = bcrypt.generate_password_hash(confirm_password)
            db.session.commit()
            # print(info.password)
            flash('Password Changed Successfully', "success")
            return render_template('login.html', params=params)
        else:
            flash('Please enter correct password', "danger")
    return render_template("setnewpassword.html", params=params)
# print("this is my web")
# print(dir)
app.run(debug=True)
