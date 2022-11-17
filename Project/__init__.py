from flask import Flask

from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
session = Session(app)

import Project.librarian_views
import Project.manage_session
import Project.user_views
