                                        # IMPORTING app_router.py FILE
import app_router

                                         # CREATING CLASS TO ADD ENDPOINTS

class Flaskappwrapper(object):

    def __init__(self, app):
        self.flask_app = app

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.flask_app.add_url_rule(endpoint, endpoint_name, handler, methods=['GET', 'POST'])

    def run(self, **kwargs):
        self.flask_app.run(**kwargs)

                                        # CREATING INSTANCE OF A CLASS Flaskappwrapper

my_flask_app = Flaskappwrapper(app_router.ac.app)

                            # CALLING ADD_ENDPOINT() BY USING INSTANCE OF A CLASS TO ADD ENDPOINTS

my_flask_app.add_endpoint("/", "home", app_router.home)
my_flask_app.add_endpoint("/login", "login", app_router.login)
my_flask_app.add_endpoint("/search", "search_query", app_router.search_query)
my_flask_app.add_endpoint("/about", "about", app_router.about)
my_flask_app.add_endpoint("/contact", "contact", app_router.contact)
my_flask_app.add_endpoint("/post/<string:post_slug>/downloadpdf", "download_pdf", app_router.download_pdf)
my_flask_app.add_endpoint("/post/<string:post_slug>", "post_route", app_router.post_route)
my_flask_app.add_endpoint("/post/<string:postslug>/comment", "comments", app_router.comments)
my_flask_app.add_endpoint("/post/<string:postslug>/comment-<int:comment_id>", "reply", app_router.reply)
my_flask_app.add_endpoint("/likes", "likes", app_router.likes)
my_flask_app.add_endpoint("/dislikes", "dislikes", app_router.dislikes)
my_flask_app.add_endpoint("/dashboard", "dashboard", app_router.dashboard)
my_flask_app.add_endpoint("/edit/<string:sno>", "edit", app_router.edit)
my_flask_app.add_endpoint("/edit/content/<string:sno>", "edit_content", app_router.edit_content)
my_flask_app.add_endpoint("/addnewpost", "addnewpost", app_router.addnewpost)
my_flask_app.add_endpoint("/addnewpost/content/<string:post_slug>", "addcontent", app_router.addcontent)
my_flask_app.add_endpoint("/uploader", "uploader", app_router.uploader)
my_flask_app.add_endpoint("/logout", "logout", app_router.logout)
my_flask_app.add_endpoint("/delete/<string:sno>", "delete", app_router.delete)
my_flask_app.add_endpoint("/signup", "signup", app_router.signup)
my_flask_app.add_endpoint("/admin_profile", "admin_profile", app_router.admin_profile)
my_flask_app.add_endpoint("/edit_profile", "edit_profile", app_router.edit_profile)
my_flask_app.add_endpoint("/forgetpassword/sendotp", "sendotp", app_router.sendotp)
my_flask_app.add_endpoint("/forgetpassword/verifyotp", "verifyotp", app_router.verifyotp)
my_flask_app.add_endpoint("/forgetpassword/setnewpassword", "setnewpassword", app_router.setnewpassword)


                            # CALLING RUN() TO RUN THE FLASK APP BY USING THE INSTANCE OF THE CLASS

# my_flask_app.run(debug=True)
app = my_flask_app.flask_app
# print(my_flask_app)
# print(app)