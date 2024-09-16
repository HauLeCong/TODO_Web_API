# %%
import functools
import jwt
from flask import Blueprint, g, request, jsonify, make_response, current_app
from datetime import datetime, timezone, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from api.db import get_db


# %%
bp = Blueprint("auth", __name__, url_prefix="/auth")


def generate_token(userid: int):
    payload = {
        "userid": userid,
        "createdAt": datetime.now().strftime("%Y-%m-%d, %H:%M:%S"),
        "exp": datetime.now(tz=timezone.utc)
        + timedelta(seconds=int(current_app.config["JWT_EXPR_TIME"])),
    }
    token = jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], "HS256")
    return token


@bp.before_app_request
def before_app_request():
    token = request.cookies.get("jwt_token")
    if token:
        try:
            decode = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], "HS256")
        except jwt.ExpiredSignatureError:
            g.userid = None
        except jwt.InvalidTokenError:
            g.userid = None
        else:
            g.userid = decode["userid"]
    else:
        g.userid = None


def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("jwt_token")
        if token:
            try:
                decode = jwt.decode(
                    token, current_app.config["JWT_SECRET_KEY"], "HS256"
                )
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            else:
                g.userid = decode["userid"]
        else:
            return jsonify({"error": "Token missing"}), 401
        return f(*args, **kwargs)

    return decorated_function


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    db = get_db()
    error = None

    if not username:
        error = "User name required"
    elif not password:
        error = "Password is required"

    if error is None:
        try:
            db.execute(
                "INSERT INTO user (username, password, email, created_at) VALUES (?, ?, ?, ?)",
                (
                    username,
                    generate_password_hash(password),
                    email,
                    datetime.now(tz=timezone.utc).strftime("%Y-%m-%d, %H:%M:%S"),
                ),
            )
            user = db.execute(
                "SELECT * FROM user WHERE username = ?", (username,)
            ).fetchone()
            db.commit()
        except db.InterfaceError:
            error = f"User {username} is already registered"
        except db.ProgrammingError:
            error = f"Incorrect querry"
        else:
            token = generate_token(userid=user["id"])
            response = make_response(
                jsonify({"message": "User registered successfully", "user": username})
            )
            response.set_cookie("jwt_token", token, httponly=True, samesite="Lax")
            return response, 201

    else:
        return jsonify({"error:", error}), 400


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    db = get_db()
    error = None
    user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
    db.commit()
    if user is None:
        error = "Incorrect username or password"
    elif not check_password_hash(user["password"], password):
        error = "Incorrect username or password"

    if error is None:
        token = generate_token(userid=user["id"])
        reponse = make_response(
            jsonify({"message": "Succesful login", "user": username})
        )
        reponse.set_cookie("jwt_token", token, httponly=True, samesite="Lax")
        return reponse, 200

    else:
        return jsonify({"error": error}), 400


@bp.route("/logout", methods=["POST"])
def logout():
    response = make_response(jsonify({"message": "Succesful logout"}))
    response.delete_cookie("jwt_token")
    return response, 200
