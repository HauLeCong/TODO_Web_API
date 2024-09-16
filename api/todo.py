from flask import current_app, g, Blueprint, jsonify, request
from api.auth import login_required
from api.db import get_db
from datetime import datetime, timezone

bp = Blueprint("todo", __name__, url_prefix="/todo")


@bp.route("/<int:id>", methods=["GET"])
@login_required
def get_todo(id):

    db = get_db()
    todo = db.execute(
        "SELECT * FROM todo WHERE userid = ? AND id = ?", (g.userid, id)
    ).fetchone()
    db.commit()
    return jsonify(todo), 200


@bp.route("/", methods=["GET"])
@login_required
def get_todos():
    db = get_db()
    todos = db.execute("SELECT * FROM todo WHERE userid = ?", (g.userid,)).fetchall()
    db.commit()
    return jsonify(todos), 200


@bp.route("/", methods=["POST"])
@login_required
def create_todo():
    data = request.get_json()
    name = data["name"]
    db = get_db()
    try:
        db.execute(
            "INSERT INTO todo(userid, name, created_at) VALUES (?, ?, ?)",
            (
                g.userid,
                name,
                datetime.now(tz=timezone.utc).strftime("%Y-%m-%d, %H:%M:%S"),
            ),
        )
        db.commit()
    except Exception as e:
        return jsonify({"error": "Internal error", "message": e}), 400
    else:
        return jsonify({"message": "Successful created"}), 201


@bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_todo(id):
    data = request.get_json()
    db = get_db()
    todo = db.execute(
        "SELECT * FROM todo WHERE userid = ? and id = ?", (g.userid, id)
    ).fetchone()

    if todo is None:
        return jsonify({"error": "todo not found"}), 400
    else:
        name = data["name"] if data["name"] is not None else todo["name"]
        db.execute(
            "UPDATE todo SET name = ? WHERE userid = ? AND id = ?", (name, g.userid, id)
        )
        todo = db.execute("SELECT last_insert_rowid()").fetchone()
        db.commit()
        return jsonify({"message": "Successful udpate", "todo": todo}), 200


@bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_todo(id):
    db = get_db()
    todo = db.execute(
        "SELECT * FROM todo WHERE userid = ? and id = ?", (g.userid, id)
    ).fetchone()

    if todo is None:
        return jsonify({"error": "todo not found"}), 400
    else:
        db.execute("DELETE FROM todo WHERE userid = ? and id = ?", (g.userid, id))
        db.commit()
        return jsonify({"message": f"Successful delete todo id: {id}"}), 201
