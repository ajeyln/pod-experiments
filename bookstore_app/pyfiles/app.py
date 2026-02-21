from flask import Flask, request, redirect, session, url_for
import mysql.connector
import os
import socket
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "supersecretkey")

# =========================
# Environment Variables
# =========================
KEYCLOAK_INTERNAL = os.environ.get("KEYCLOAK_INTERNAL")
KEYCLOAK_EXTERNAL = os.environ.get("KEYCLOAK_EXTERNAL")

REALM = os.environ.get("REALM")
CLIENT_ID = os.environ.get("CLIENT_ID")
REDIRECT_URI = os.environ.get("REDIRECT_URI")

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT")
MINIO_BUCKET = "book-images"

# =========================
# Keycloak URLs
# =========================
AUTH_URL = f"{KEYCLOAK_EXTERNAL}/realms/{REALM}/protocol/openid-connect/auth"
TOKEN_URL = f"{KEYCLOAK_INTERNAL}/realms/{REALM}/protocol/openid-connect/token"
LOGOUT_URL = f"{KEYCLOAK_EXTERNAL}/realms/{REALM}/protocol/openid-connect/logout"

# =========================
# Database Connection
# =========================
def get_db():
    return mysql.connector.connect(
        host="mysql-service",
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"]
    )

# =========================
# Login Route
# =========================
@app.route("/login")
def login():
    return redirect(
        f"{AUTH_URL}"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&scope=openid"
        f"&redirect_uri={REDIRECT_URI}"
        f"&prompt=login"
    )

# =========================
# Callback Route
# =========================
@app.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return "No authorization code received", 400

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID
        # No client_secret (public client)
    }

    response = requests.post(TOKEN_URL, data=data)

    if response.status_code != 200:
        return f"Token error: {response.text}", 400

    token_data = response.json()

    session["access_token"] = token_data.get("access_token")
    session["id_token"] = token_data.get("id_token")

    return redirect(url_for("home"))

# =========================
# Logout
# =========================
@app.route("/logout")
def logout():
    logout_redirect = (
        f"{LOGOUT_URL}"
        f"?client_id={CLIENT_ID}"
        f"&post_logout_redirect_uri={REDIRECT_URI.replace('/callback','')}"
    )
    session.clear()
    return redirect(logout_redirect)

# =========================
# Protected Home
# =========================
@app.route("/", methods=["GET"])
def home():

    if "access_token" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT index_no, book_name, book_author,
               image_of_front_page, no_of_copies, year_published
        FROM books
        ORDER BY index_no
    """)
    books = cursor.fetchall()

    pod_name = socket.gethostname()

    html = f"""
    <h2>Hi from Pod: {pod_name}</h2>
    <a href="/logout">Logout</a>
    <table border="1">
    <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Author</th>
        <th>Image</th>
        <th>Copies</th>
        <th>Year</th>
    </tr>
    """

    for book in books:
        image_url = f"{MINIO_ENDPOINT}/{MINIO_BUCKET}/{book[3]}"
        html += f"""
        <tr>
          <td>{book[0]}</td>
          <td>{book[1]}</td>
          <td>{book[2]}</td>
          <td><img src="{image_url}" width="80"></td>
          <td>{book[4]}</td>
          <td>{book[5]}</td>
        </tr>
        """

    html += "</table>"

    cursor.close()
    db.close()

    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)