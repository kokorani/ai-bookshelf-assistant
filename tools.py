import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine(
     "mysql+pymysql://root:reallyStrongPwd123@localhost:3306/analytics"
)

def execute_query(query):
    """For SELECT queries. Returns a DataFrame."""
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df

def execute_write(query):
    """For INSERT/UPDATE/DELETE queries."""
    with engine.begin() as conn:
        conn.execute(text(query))

def add_book(title, author, genre=None, status='Currently Reading', target_month=None):
    query = f"""
    INSERT INTO books (title, author, genre, status, target_month) 
    VALUES ('{title}','{author}','{genre}','{status}',{target_month if target_month else 'NULL'})
    """
    execute_write(query)
    return f"Added book: {title} by {author} with status {status} "


def get_books(status=None, genre=None, author=None):
    query = "SELECT * from books WHERE 1=1"

    if status:
        query += f" AND status = '{status}' "

    if genre:
        query += f" AND genre = '{genre}' "

    if author:
            query += f" AND author = '{author}' "

    query += f" ORDER BY created_at DESC"

    return execute_query(query)

def update_book(book_id, status=None, rating=None, review=None, started_at=None, completed_at=None, target_month=None):
    fields = []

    if status:
        fields.append(f"status = '{status}'")
    if rating:
        fields.append(f"rating = {rating}")
    if review:
        fields.append(f"review = '{review}'")
    if started_at:
        fields.append(f"started_at = '{started_at}'")
    if completed_at:
        fields.append(f"completed_at = '{completed_at}'")
    if target_month:
        fields.append(f"target_month = {target_month}")

    if not fields:
        return "No fields provided to update"

    query = f"UPDATE books SET {', '.join(fields)} WHERE id = {book_id}"
    execute_write(query)
    return f"Updated book with id {book_id}"

def delete_book(book_id=None, title=None, author=None):
    if book_id is not None:
        query = f"DELETE FROM books WHERE id = {book_id}"

        execute_write(query)

        return f"Deleted book with id {book_id}"

    filters = []
    if title:
        filters.append(f"title = '{title}'")
    if author:
        filters.append(f"author = '{author}'")
 
    if not filters:
        return "No book_id or filters provided, nothing deleted"

    match_query = f"SELECT id FROM books WHERE {' AND '.join(filters)}"
    matches = execute_query(match_query)
 
    if len(matches) == 0:
        return "No matching book found, nothing deleted"
    if len(matches) > 1:
        return f"Found {len(matches)} matching books, please specify which id to delete: {matches['id'].tolist()}"
 
    matched_id = matches['id'].iloc[0]

    query = f"DELETE FROM books WHERE id = {matched_id}"

    execute_write(query)

    return f"Deleted book with id {matched_id}"

def get_reading_summary():
    query = """
        SELECT
            status,
            COUNT(*) AS book_count,
            AVG(rating) AS avg_rating
        FROM books
        GROUP BY status
    """
    return execute_query(query)