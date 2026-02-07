from flask import Flask, request
import mysql.connector
import os
import socket

app = Flask(__name__)

MINIO_ENDPOINT = "http://localhost:9000"
MINIO_BUCKET = "book-images"

def get_db():
    return mysql.connector.connect(
        host="mysql-service",
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"]
    )

@app.route("/", methods=["GET", "POST"])
def home():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT
          index_no,
          book_name,
          book_author,
          image_of_front_page,
          no_of_copies,
          year_published
        FROM books
        ORDER BY index_no
    """)
    books = cursor.fetchall()

    selected = None
    if request.method == "POST":
        book_id = request.form.get("book_id")
        cursor.execute("""
            SELECT
              index_no,
              book_name,
              book_author,
              image_of_front_page,
              no_of_copies,
              year_published
            FROM books
            WHERE index_no = %s
        """, (book_id,))
        selected = cursor.fetchone()

    pod_name = socket.gethostname()

    html = f"""
    <h2>Hi {pod_name}</h2>
    <form method="POST">
    <table border="1" cellpadding="6" cellspacing="0">
      <tr>
        <th>Select</th>
        <th>Index</th>
        <th>Book Name</th>
        <th>Author</th>
        <th>Image</th>
        <th>Copies</th>
        <th>Year</th>
      </tr>
    """

    for book in books:
        image_url = f"{MINIO_ENDPOINT}/{MINIO_BUCKET}/{book[3]}"
        print(image_url)
        html += f"""
        <tr>
          <td><input type="radio" name="book_id" value="{book[0]}" required></td>
          <td>{book[0]}</td>
          <td>{book[1]}</td>
          <td>{book[2]}</td>
          <td>
            <img src="{image_url}" width="80" height="120">
          </td>
          <td>{book[4]}</td>
          <td>{book[5]}</td>
        </tr>
        """

    html += """
    </table>
    <br>
    <input type="submit" value="View Selected Book">
    </form>
    """

    if selected:
        selected_image = f"{MINIO_ENDPOINT}/{MINIO_BUCKET}/{selected[3]}"
        print(f"selected_image:{selected_image}")
        html += f"""
        <hr>
        <h3>Selected Book</h3>
        <img src="{selected_image}" width="150"><br><br>
        <b>Name:</b> {selected[1]}<br>
        <b>Author:</b> {selected[2]}<br>
        <b>Copies:</b> {selected[4]}<br>
        <b>Year:</b> {selected[5]}<br>
        """

    cursor.close()
    db.close()

    return html

app.run(host="0.0.0.0", port=5000)
