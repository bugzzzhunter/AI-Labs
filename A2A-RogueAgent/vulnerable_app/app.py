from flask import Flask, request, jsonify
import sqlite3
import logging


app = Flask(__name__)


# ============================================================
# INTENTIONALLY VULNERABLE CONFIGURATION
# ============================================================

# VULNERABILITY 1:
# Hardcoded credentials
DATABASE_USER = "app_admin"
DATABASE_PASSWORD = "Sup3rSecretPassword123!"


DATABASE = "company.db"


# ============================================================
# INSUFFICIENT SECURITY LOGGING
# ============================================================

# Basic application logging is enabled, but security-sensitive
# events are not logged with useful context.
logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# ============================================================
# DATABASE
# ============================================================

def get_db():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    db = get_db()

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """
    )

    existing = db.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    if existing == 0:

        db.executemany(
            """
            INSERT INTO users
            (username, email, role)
            VALUES (?, ?, ?)
            """,
            [
                (
                    "alice",
                    "alice@example.com",
                    "user"
                ),
                (
                    "bob",
                    "bob@example.com",
                    "developer"
                ),
                (
                    "admin",
                    "admin@example.com",
                    "administrator"
                ),
            ],
        )

    db.commit()

    db.close()


# ============================================================
# USER SEARCH
# ============================================================

@app.route("/users")
def search_users():

    username = request.args.get(
        "username",
        ""
    )

    # VULNERABILITY 2:
    # SQL injection
    #
    # User-controlled input is directly concatenated
    # into the SQL query.

    query = (
        "SELECT id, username, email, role "
        "FROM users "
        "WHERE username = '"
        + username
        + "'"
    )

    try:

        db = get_db()

        results = db.execute(
            query
        ).fetchall()

        db.close()

        # VULNERABILITY 3:
        # Insufficient security logging
        #
        # The sensitive database operation is not logged
        # with useful security context.

        return jsonify([
            dict(row)
            for row in results
        ])

    except Exception as ex:

        # VULNERABILITY 4:
        # Verbose error message
        #
        # Internal exception details are returned directly
        # to the client.

        return jsonify({
            "error": str(ex),
            "query": query
        }), 500


# ============================================================
# USER DETAILS
# ============================================================

@app.route("/users/<int:user_id>")
def get_user(user_id):

    try:

        db = get_db()

        user = db.execute(
            """
            SELECT id, username, email, role
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        db.close()

        if user is None:

            return jsonify({
                "error": "User not found"
            }), 404

        return jsonify(
            dict(user)
        )

    except Exception as ex:

        # Another example of verbose error handling.

        return jsonify({
            "error": str(ex),
            "database": DATABASE,
            "user_id": user_id
        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok"
    })


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    initialize_database()

    # Intentionally local-only for the lab.
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )