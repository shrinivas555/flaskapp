import requiredmodules

    # creating a instant of flask app

app = requiredmodules.Flask(__name__)

    # loading parameters from config.json file

with open ("config.json","r") as c:
    params = requiredmodules.json.load(c)["params"]

    # configuroing database in flask application
app.secret_key = 'super-secret-key'
# app.config["SQLALCHEMY_DATABASE_URI"] = params["prod_uri"]
app.config["SQLALCHEMY_DATABASE_URI"] = requiredmodules.os.environ.get('PROD_URI')
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {
        "ssl": {
            "ssl_ca": requiredmodules.os.path.join(requiredmodules.os.path.dirname(__file__), "ca.pem")
        }
    }
}
db = requiredmodules.SQLAlchemy()
db.init_app(app)

    # creating an instant of Bcrypt() class

bcrypt = requiredmodules.Bcrypt()
bcrypt.init_app(app)

    # configuring file uploader

# app.config["UPLOAD_FOLDER"] = params["upload_location"]
# base_static_url = requiredmodules.url_for('static')
# image_upload_location = params["upload_location"]
upload_folder = requiredmodules.os.path.join(app.root_path, '/static/assets/img')
# requiredmodules.os.makedirs(upload_folder, exist_ok=True)
app.config["UPLOAD_FOLDER"] = upload_folder


    # creating an instant of LoginManager()

login_manager = requiredmodules.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"
login_manager.login_message = "You Are Not Logged In"

    # configuring mail and creating an instant of mail()

app.config.update(
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_PORT = "465",
    MAIL_USE_SSL = True,
    MAIL_USE_TLS = False,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)
mail = requiredmodules.Mail()
mail.init_app(app)

    #creating an instant of Share()

# share = requiredmodules.Share()
# share.init_app(app)
