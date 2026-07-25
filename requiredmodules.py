import werkzeug.utils
from flask import Flask, render_template, send_file, request, redirect, url_for, session, flash, current_app
import math
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime, date
from flask_mail import Mail, Message
import os
import werkzeug
from flask_bcrypt import Bcrypt, check_password_hash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
import random
# from flask_share import Share
from fpdf import FPDF
import pymysql
