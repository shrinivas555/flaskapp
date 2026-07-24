import datetime  # IMPORTS

# imort app_configuration file as ac
import requiredmodules as rm

# imort app_configuration file as ac
import app_configuration as ac

# imort db_models file as dm
import db_tables as dm

                                        # APP ACTIONS #

                                        # LOGIN METHOD

# @ac.app.route("/login", methods=['GET', 'POST'])
def login():
    next_url = rm.request.args.get('next')
    print(next_url)
    if rm.request.method == 'POST':

        username = rm.request.form.get('uname')
        password = rm.request.form.get('pass')
        user = dm.Admins.query.filter_by(username=username).first()

        if ac.bcrypt.check_password_hash(user.password, password):

            rm.login_user(user)
            # return rm.redirect(str(url))
            return rm.redirect(next_url)

        else:

            rm.flash("Invalid username/password", "danger")

    return rm.render_template("login.html", params=ac.params)


                                        # HOME METHOD

# @ac.app.route("/", methods=['GET', 'POST'])
def home():

    page = rm.request.args.get('page', 1)
    posts = dm.Posts.query.filter_by().order_by(dm.Posts.date.desc()).all()
    # print(posts)
    total_posts = len(posts)
    posts_per_page = ac.params['no_of_posts']
    total_pages = rm.math.ceil(total_posts / posts_per_page)
    starting_index = (int(page) - 1) * posts_per_page
    posts_content = posts[starting_index:starting_index + posts_per_page]

    return rm.render_template("index.html", params=ac.params, current_page=int(page), total_pages=total_pages,
                           posts_content=posts_content, current_user=rm.current_user)


                                    # METHOD FOR SEARCHING ARTICLE

# @app.route("/search")
def search_query():

    base_url = rm.request.base_url
    page = rm.request.args.get('page',1)
    search_query = rm.request.args.get('search')
    posts = search(search_query)
    total_posts = len(posts)
    posts_per_page = ac.params['no_of_posts']
    total_pages = rm.math.ceil(total_posts / posts_per_page)
    starting_index = (int(page) - 1) * posts_per_page
    posts_content = posts[starting_index:starting_index + posts_per_page]
    return rm.render_template("index.html", params=ac.params,search_query=search_query, base_url=base_url, current_page = int(page), total_pages=total_pages, posts_content=posts_content, current_user=rm.current_user)

def search(query):

    search_result = []
    posts = dm.Posts.query.filter_by().order_by(dm.Posts.date.desc()).all()

    for post in posts:

        if query.upper() in post.title.upper():
            search_result.append(post)
        if query.upper() in post.admin.upper():
            if post not in search_result:
                search_result.append(post)

    return search_result

                                # METHOD FOR ABOUT METHOD

# @app.route("/about")
def about():
    return rm.render_template("about.html", params=ac.params)

                                    # METHOD FOR CONTACT PAGE

# @app.route("/contact", methods=['GET', 'POST'])
def contact():
    '''get the data from the contact form '''
    if rm.request.method=="POST":
        name = rm.request.form.get('name')
        phone = rm.request.form.get('phone')
        email = rm.request.form.get('email')
        message = rm.request.form.get('message')
        date = rm.datetime.now()
        '''insert the data in the contacts table of codingthunder database'''
        '''
               sno, name, phone_num, msg, date, email
           '''
        entry = dm.Contacts(name=name, phone_num=phone, msg=message, email=email, date=date)
        ac.db.session.add(entry)
        ac.db.session.commit()
        rm.flash("Thanks for contacting us, Your form is submitted successfully", "success")
        email_msg = rm.Message('new message from ' + name, sender=email, recipients=[ac.params['gmail-user']])
        email_msg.body = message + "\n" + phone
        ac.mail.send(email_msg)

    return rm.render_template("contact.html", params=ac.params)

                                    # METHODS FOR CREATING AND DOWNLOADING ARTICLE IN PDF FORMAT

# @app.route('/post/<string:post_slug>/downloadpdf')
@rm.login_required
def download_pdf(post_slug):
    if rm.request.method == 'POST':
        create_pdf(post_slug)
        post = dm.Posts.query.filter_by(slug=post_slug).first()
        filename = post.title + '_' + post_slug + '.pdf'
        file_path = rm.os.path.join(ac.params['upload_location'], filename)
        # rm.os.remove(file_path)
        return rm.send_file(file_path, as_attachment=True)
    return "please log in and download PDF dear friend"



def create_pdf(post_slug):
    post = dm.Posts.query.filter_by(slug=post_slug).first()
    content = post.content
    paragraphs = content.split('|')
    filename = post.title + '_' + post_slug + '.pdf'
    pdf = rm.FPDF('P', 'mm', 'A4')
    pdf.set_top_margin(20)
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.set_auto_page_break(True, 15)
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

    save_location = rm.os.path.join(ac.params['upload_location'], filename)
    return pdf.output(save_location)

                                    # METHODS FOR DISPLAYINF ARTICLES ON HOMEPAGE

# @app.route("/post/<string:post_slug>", methods = ['GET', 'POST'])
@rm.login_required
def post_route(post_slug):
    '''fetching the single post if they are multiple
    posts are filter by slug which is given to the function as paraaeter
    here slug is the database column and slug_post is the backend variable'''
    # login()
    # if login() == "authentication successful":

    # if rm.current_user.is_authenticated:
    recorded_like = dm.Likes.query.filter_by(postslug=post_slug, username=rm.current_user.username).first()
    post = dm.Posts.query.filter_by(slug=post_slug).first()
    content = post.content
    paras = content.split('|')
    comments = dm.Comments.query.filter_by(post=post_slug).all()

    return rm.render_template("post.html",recorded_like=recorded_like, params=ac.params, post=post, paras=paras, comments=comments)

    # return login("/post/" + post_slug)

                                        # METHODS FOR COMMENTS SECTION

# @app.route('/post/<string:postslug>/comment', methods = ['GET', 'POST'])
@rm.login_required
def comments(postslug):

    if rm.request.method == 'POST':

        comment = rm.request.form.get('comment')
        user = rm.current_user.username
        date = rm.datetime.now()
        post = postslug
        entry = dm.Comments(user=user, post=post, commentsonpost=comment, date=date)
        ac.db.session.add(entry)
        ac.db.session.commit()

        return rm.redirect('/post/' + postslug)

    return rm.redirect('/post/' + postslug)

                                            # METHODS FOR COMMENTS REPLY

# @app.route('/post/<string:postslug>/comment-<int:comment_id>', methods = ['GET', 'POST'])
@rm.login_required
def reply(postslug, comment_id):

    replies = dm.Replies.query.filter_by(commentid = comment_id).all()
    post = dm.Posts.query.filter_by(slug=postslug).first()
    comment = dm.Comments.query.filter_by(id=comment_id).first()

    if rm.request.method == 'POST':

        reply = rm.request.form.get('reply')
        user = rm.current_user.username
        date = rm.datetime.now()

        entry = dm.Replies(commentid=comment_id, user=user, reply=reply, date=date)
        ac.db.session.add(entry)
        ac.db.session.commit()

        return rm.redirect('/post/' + postslug)

    return rm.render_template('replies.html', params=ac.params, replies=replies, post=post, comment=comment)

                                            # METHODS FOR MANAGING LIKES OF AN ARTICLES

# @app.route('/likes', methods = ['GET', 'POST'])
@rm.login_required
def likes():

    if rm.request.method == 'POST':

        data = rm.request.get_json()
        post_slug = data.get('post_slug')
        username = rm.current_user.username
        recorded_like = dm.Likes.query.filter_by(postslug=post_slug,username=username).first()
        print(recorded_like)
        print(type(recorded_like))

        if recorded_like == None:

            entry = dm.Likes(postslug=post_slug, username=username)
            post = dm.Posts.query.filter_by(slug=post_slug).first()
            post.likes += 1
            ac.db.session.add(entry)
            ac.db.session.commit()

            return rm.redirect('/post/' + post_slug)
        else:

            return rm.redirect('/post/' + post_slug)

                                        # METHODS FOR MANAGING DISLIKES OF AN ARTICLES

# @app.route('/dislikes', methods = ['GET', 'POST'])
@rm.login_required
def dislikes():

    if rm.request.method == 'POST':
        data = rm.request.get_json()
        post_slug = data.get('post_slug')
        username = rm.current_user.username
        recorded_like = dm.Likes.query.filter_by(postslug=post_slug, username=username).first()
        post = dm.Posts.query.filter_by(slug=post_slug).first()
        post.likes -= 1
        ac.db.session.delete(recorded_like)
        ac.db.session.commit()

        return rm.redirect('/post/' + post_slug)

                                    # METHODS TO MANAGE DASHBOARD

# @app.route('/dashboard', methods = ['GET', 'POST'])
@rm.login_required
def dashboard():

    # if rm.current_user.is_authenticated:
    posts = dm.Posts.query.filter_by(admin=rm.current_user.username).all()

    return rm.render_template('dashboard.html', params=ac.params, posts=posts, admin = rm.current_user.name)

    # return login(str(rm.url_for('dashboard')))
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


                                            # METHODS TO MANAGE EDITING OF AN ARTICLE

# @app.route("/edit/<string:sno>", methods=['GET', 'POST'])
@rm.login_required
def edit(sno):

    if rm.request.method =='POST':

        title = rm.request.form.get('title')
        subtitle = rm.request.form.get('subtitle')
        slug = rm.request.form.get('slug')
        no_of_paras = rm.request.form.get('no_of_paras')
        img_file = rm.request.form.get('bgimg')
        # admin = rm.current_user.username  #code for admin is to be written************************
        date = rm.date.today().strftime('%b-%d-%Y')
        print(date)

        post = dm.Posts.query.filter_by(sno=sno).first()
        post.title = title
        post.subtitle = subtitle
        post.slug = slug
        post.no_of_paras = no_of_paras
        post.img_file = img_file
        post.date = date
        ac.db.session.commit()
        rm.flash("Your post saved successfully", "success")

        return rm.redirect("/edit/content/" + str(sno))

    post = dm.Posts.query.filter_by(sno=sno).first()

    return rm.render_template('edit.html', params=ac.params, post=post, admin = rm.current_user.name)

                                                    # METHODS TO MANAGE EDITING OF CONTENT OF AN ARTICLE

# @app.route('/edit/content/<string:sno>', methods = ['GET', 'POST'])
@rm.login_required
def edit_content(sno):

    int(sno)
    post = dm.Posts.query.filter_by(sno=sno).first()
    edit_names = []

    for i in range(int(post.no_of_paras)):
        name = 'para' + str(i)
        edit_names.append(name)

    if rm.request.method=='POST':
        post = dm.Posts.query.filter_by(sno=sno).first()
        paras_list = []
        separator = '|'

        for i in range(int(post.no_of_paras)):
            para = rm.request.form.get(edit_names[i])
            paras_list.append(para)

        content = separator.join(paras_list)
        print(content)
        post.content = content
        ac.db.session.commit()
        rm.flash('Your post updated successfully', 'success')

        return rm.redirect(rm.url_for('dashboard'))

    content = post.content
    paras = content.split('|')

    return rm.render_template("edit_content.html", names=edit_names, params=ac.params, paras=paras, post=post, admin = rm.current_user.name)

                                            # METHODS TO ADD NEW ARTICLES

# @app.route('/addnewpost', methods = ['GET', 'POST'])
@rm.login_required
def addnewpost():

    # if rm.current_user.is_authenticated:

    if rm.request.method=='POST':

        title = rm.request.form.get('title')
        subtitle = rm.request.form.get('subtitle')
        slug = rm.request.form.get('slug')
        no_of_paras = rm.request.form.get('no_of_paras')
        content = "None"
        # images = "no image uploaded"
        img_file = rm.request.form.get('bgimg')
        admin = rm.current_user.username  # code for admin is to be written************************
        date = rm.date.today().strftime('%b-%d-%Y')
        global names
        names = []

        for i in range(int(no_of_paras)):
            name = 'para' + str(i)
            names.append(name)

        entry = dm.Posts(title=title, subtitle=subtitle, slug=slug, content=content, img_file=img_file, admin=admin, date=date, no_of_paras=no_of_paras, )
        ac.db.session.add(entry)
        ac.db.session.commit()
        rm.flash("Your post detail saved successfully", "success")
        post = dm.Posts.query.filter_by(slug=slug).first()

        return rm.render_template("postcontent.html", names=names, params=ac.params, post=post, admin = rm.current_user.name)

    return rm.render_template('addnewpost.html', params=ac.params, admin = rm.current_user.name)

    # return login(str(rm.url_for('addnewpost')))


                                                # METHODS TO ADD CONTENT OF AN ARTICLE

# @app.route("/addnewpost/content/<string:post_slug>", methods = ['GET', 'POST'])
@rm.login_required
def addcontent(post_slug):

    if rm.request.method == 'POST':
        post = dm.Posts.query.filter_by(slug=post_slug).first()
        paras_list = []
        separator = '|'

        for i in range(int(post.no_of_paras)):
            para = rm.request.form.get(names[i])
            paras_list.append(para)

        content = separator.join(paras_list)
        post.content = content
        ac.db.session.commit()
        rm.flash("Your post added successfully", "success")

        return rm.redirect('/dashboard')

    return rm.render_template("postcontent.html", params=ac.params)

                                            # METHODS TO UPLOAD FILES

# @app.route("/uploader", methods=['GET', 'POST'])
@rm.login_required
def uploader():

    if rm.request.method=='POST':

        f = rm.request.files['file']
        f.save(rm.os.path.join(ac.app.config['UPLOAD_FOLDER'], rm.werkzeug.utils.secure_filename(f.filename)))
        rm.flash("Uour file uploaded successfully", "success")

        return rm.redirect("/dashboard")

                                            # METHODS TO LOGOUT

# @app.route("/logout")
@rm.login_required
def logout():

    rm.logout_user()
    rm.flash("You are logged out uccessfully", "success")

    return rm.redirect('/dashboard')

                                                                # METHODS TO DELETE AN ARTICLE

# @app.route("/delete/<string:sno>", methods=['GET', 'POST'])
@rm.login_required
def delete(sno):

    post = dm.Posts.query.filter_by(sno =sno).first()
    ac.db.session.delete(post)
    ac.db.session.commit()
    rm.flash(f"Ypur post of Sno. {sno} deleted.", "success")

    return rm.redirect('/dashboard')

                                                    # METHODS TO SIGNUP

# @app.route("/signup", methods = ['GET', 'POST'])
def signup():

    if rm.request.method=='POST':
        '''
            sno, name, email, phone, username, password, date
        '''
        name = rm.request.form.get('name')
        email = rm.request.form.get('email')
        phone = rm.request.form.get('phone')
        username = rm.request.form.get('username')
        password = rm.request.form.get('password')
        date = rm.datetime.now(datetime.timezone.utc)
        entry = dm.Admins(name=name, email=email, phone=phone, username=username,
                       password=ac.bcrypt.generate_password_hash(password), date=date)
        ac.db.session.add(entry)
        ac.db.session.commit()
        rm.flash("Your account created successfully", "success")

        return rm.redirect('/dashboard')

    return rm.render_template("signup.html", params=ac.params)

                                                # METHOD TO DISPLAY ADMIN PROFILE

# @app.route('/admin_profile')
@rm.login_required
def admin_profile():

    info = dm.Admins.query.filter_by(username = rm.current_user.username).first()

    return rm.render_template('profile.html', params=ac.params, admin = rm.current_user.name, info = info)

                                                        # METHODS TO EDIT PROFILE

# @app.route('/edit_profile', methods = ['GET', 'POST'])
@rm.login_required
def edit_profile():

    if rm.request.method == 'POST':

        name = rm.request.form.get('name')
        email = rm.request.form.get('email')
        phone = rm.request.form.get('phone')
        username = rm.request.form.get('username')
        password = rm.request.form.get('password')
        password = ac.bcrypt.generate_password_hash(password)
        date = rm.datetime.now()
        admin = dm.Admins.query.filter_by(username = rm.current_user.username).first()
        admin.name = name
        admin.email = email
        admin.phone =phone
        admin.username = username
        admin.password = password
        admin.date = date
        ac.db.session.commit()
        rm.flash("Your profile updated successfully", "success")

        return rm.redirect('/admin_profile')

    admin = dm.Admins.query.filter_by(username=rm.current_user.username).first()

    return rm.render_template('edit_profile.html', params=ac.params, admin=admin)

                                                            # METHOD FOR SENDING OTP TO RESET PASSWORD

# @app.route("/forgetpassword/sendotp", methods = ['GET', 'POST'])
@rm.login_required
def sendotp():

    if rm.request.method=='POST':

        try:
            global registered_email
            registered_email = rm.request.form.get('email')
            global otp_by_sys
            otp_by_sys = rm.random.randint(100000, 999999)
            print(otp_by_sys)
            email_msg = rm.Message('email validation OTP - PostMyArticle', sender=a.params['gmail-user'], recipients=[registered_email])
            email_msg.body = "email validation OTP for PostMyArticle forget password is: " + str(otp_by_sys) + " -\nPostMyArticle"
            ac.mail.send(email_msg)

            return rm.render_template("verifyotp.html", params=ac.params)

        except Exception as e:
            print(e)

    return rm.render_template("sendotp.html", params=ac.params)

                                                            # METHOD TO VERIFY OTP

# @app.route("/forgetpassword/verifyotp", methods = ['GET', 'POST'])
@rm.login_required
def verifyotp():

    if rm.request.method=='POST':

        otp_from_admin = rm.request.form.get('OTP')
        if(int(otp_from_admin) == otp_by_sys):

            return rm.render_template("setnewpassword.html", params=ac.params)

        else:

            rm.flash('FAILED! your OTP is incorrect. Please try again.', 'danger')

    return rm.render_template("verifyotp.html", params=ac.params)

                                                        # METHOD TO SET MEW PASSWORD

# @app.route('/forgetpassword/setnewpassword', methods = ['GET', 'POST'])
@rm.login_required
def setnewpassword():

    if rm.request.method =='POST':

        info = dm.Admins.query.filter_by(email = registered_email).first()
        trial_password = rm.request.form.get('password')
        confirm_password = rm.request.form.get('confirmpasswod')

        if(trial_password == confirm_password):
            old_password = info.password
            info.password = ac.bcrypt.generate_password_hash(confirm_password)
            ac.db.session.commit()
            rm.flash('Password Changed Successfully', "success")

            return rm.render_template('login.html', params=ac.params)

        else:
            rm.flash('Please enter correct password', "danger")

    return rm.render_template("setnewpassword.html", params=ac.params)
