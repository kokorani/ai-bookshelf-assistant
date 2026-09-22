my_tools = [
    {
        "type": "function",
        "name": "add_book",
        "description": "Add a new book to the reading tracker",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the book"
                },
                "author": {
                    "type": "string",
                    "description": "Author of the book"
                },
                "genre": {
                    "type": "string",
                    "description": "Genre of the book (e.g. Fiction, Sci-Fi, Self-help, Memoir)"
                },
                "status": {
                    "type": "string",
                    "description": "Reading status: 'Currently Reading', 'On Hold', or 'Completed'. Defaults to 'Currently Reading' if not specified."
                },
                "target_month": {
                    "type": "integer",
                    "description": "Month (1-12) the user plans to read this book"
                }
            },
            "required": ["title", "author"]
        }
    },

    {
        "type": "function",
        "name": "get_books",
        "description": "Get books from the tracker, optionally filtered by status, genre, and/or author",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Filter by status: 'Currently Reading', 'On Hold', or 'Completed'"
                },
                "genre": {
                    "type": "string",
                    "description": "Filter by genre"
                },
                "author": {
                    "type": "string",
                    "description": "Filter by author"
                }
            },
            "required": []
        }
    },

    {
        "type": "function",
        "name": "update_book",
        "description": "Update one or more fields of an existing book, including marking it as read (set status to 'Completed') and rating it",
        "parameters": {
            "type": "object",
            "properties": {
                "book_id": {
                    "type": "integer",
                    "description": "The id of the book to update"
                },
                "status": {
                    "type": "string",
                    "description": "New status: 'Currently Reading', 'On Hold', or 'Completed'"
                },
                "rating": {
                    "type": "integer",
                    "description": "Rating from 1 to 5"
                },
                "review": {
                    "type": "string",
                    "description": "Review text for the book"
                },
                "started_at": {
                    "type": "string",
                    "description": "Date the user started reading, in YYYY-MM-DD format"
                },
                "completed_at": {
                    "type": "string",
                    "description": "Date the user finished reading, in YYYY-MM-DD format"
                },
                "target_month": {
                    "type": "integer",
                    "description": "Month (1-12) the user plans to read this book"
                }
            },
            "required": ["book_id"]
        }
    },

    {
        "type": "function",
        "name": "delete_book",
        "description": "Delete a book. Use book_id if known. If not known, provide title/author to look up and delete a matching book instead.",
        "parameters": {
            "type": "object",
            "properties": {
                "book_id": {
                    "type": "integer",
                    "description": "The id of the book to delete, if known"
                },
                "title": {
                    "type": "string",
                    "description": "Title to match when book_id is not known"
                },
                "author": {
                    "type": "string",
                    "description": "Author to match when book_id is not known"
                }
            },
            "required": []
        }
    },

    {
        "type": "function",
        "name": "get_reading_summary",
        "description": "Get a summary of books grouped by status, including count and average rating",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]