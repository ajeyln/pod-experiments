from flask import Flask, request
import mysql.connector
import os
import socket

app = Flask(__name__)

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
    <table border="1" cellpadding="5" cellspacing="0">
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
        html += f"""
        <tr>
          <td>
            <input type="radio" name="book_id" value="{book[0]}" required>
          </td>
          <td>{book[0]}</td>
          <td>{book[1]}</td>
          <td>{book[2]}</td>
          <td>{book[3]}</td>
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
        html += f"""
        <hr>
        <h3>Selected Book</h3>
        <ul>
          <li><b>Index:</b> {selected[0]}</li>
          <li><b>Name:</b> {selected[1]}</li>
          <li><b>Author:</b> {selected[2]}</li>
          <li><b>Image:</b> {selected[3]}</li>
          <li><b>Copies:</b> {selected[4]}</li>
          <li><b>Year:</b> {selected[5]}</li>
        </ul>
        """

    cursor.close()
    db.close()

    return html

app.run(host="0.0.0.0", port=5000)
