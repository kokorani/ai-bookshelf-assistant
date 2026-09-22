CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    genre VARCHAR(100),
    status ENUM('Currently Reading', 'On Hold', 'Completed') NOT NULL DEFAULT 'Currently Reading',
    rating TINYINT,
    review TEXT,
    target_month TINYINT,
    started_at DATE,
    completed_at DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (rating BETWEEN 1 AND 5),
    CHECK (target_month BETWEEN 1 AND 12)
);

INSERT INTO books
(title, author, genre, status, rating, review, target_month, started_at, completed_at)
VALUES
-- January
('Atomic Habits', 'James Clear', 'Self Help', 'Completed', 5,
 'Practical and motivating.', 1, '2026-01-03', '2026-01-18'),

-- February
('Dune', 'Frank Herbert', 'Science Fiction', 'Currently Reading', 4,
 NULL, 2, '2026-02-10', NULL),
('The Alchemist', 'Paulo Coelho', 'Fiction', 'On Hold', 3,
 'Paused midway.', 2, '2026-02-18', NULL),

-- March
('1984', 'George Orwell', 'Dystopian', 'Completed', 5,
 'Thought-provoking classic.', 3, '2026-03-02', '2026-03-12'),

-- April
('Pride and Prejudice', 'Jane Austen', 'Classic', 'Completed', 4,
 'Witty and charming.', 4, '2026-04-01', '2026-04-15'),
('Project Hail Mary', 'Andy Weir', 'Science Fiction', 'Currently Reading', 5,
 NULL, 4, '2026-04-08', NULL),

-- May
('The Silent Patient', 'Alex Michaelides', 'Thriller', 'Completed', 4,
 'Great twist.', 5, '2026-05-02', '2026-05-09'),

-- June
('Clean Code', 'Robert C. Martin', 'Technology', 'Currently Reading', 4,
 NULL, 6, '2026-06-10', NULL),
('Meditations', 'Marcus Aurelius', 'Philosophy', 'On Hold', 3,
 NULL, 6, '2026-06-22', NULL),

-- July
('The Martian', 'Andy Weir', 'Science Fiction', 'Completed', 5,
 'Fast-paced and funny.', 7, '2026-07-03', '2026-07-11'),
('Ikigai', 'Hector Garcia', 'Self Help', 'Currently Reading', 4,
 NULL, 7, '2026-07-14', NULL),

-- August
('To Kill a Mockingbird', 'Harper Lee', 'Classic', 'Completed', 5,
 'Powerful read.', 8, '2026-08-01', '2026-08-15'),

-- September
('The Midnight Library', 'Matt Haig', 'Fantasy', 'Completed', 4,
 'Reflective and uplifting.', 9, '2026-09-02', '2026-09-10'),
('A Little Life', 'Hanya Yanagihara', 'Drama', 'On Hold', 4,
 NULL, 9, '2026-09-12', NULL),

-- October
('Dracula', 'Bram Stoker', 'Horror', 'Completed', 4,
 'Perfect October read.', 10, '2026-10-01', '2026-10-13'),

-- November
('The Book Thief', 'Markus Zusak', 'Historical Fiction', 'Completed', 5,
 'Heartbreaking and memorable.', 11, '2026-11-02', '2026-11-18'),
('Becoming', 'Michelle Obama', 'Memoir', 'Currently Reading', 4,
 NULL, 11, '2026-11-11', NULL),

-- December
('A Christmas Carol', 'Charles Dickens', 'Classic', 'Completed', 4,
 'A festive classic.', 12, '2026-12-01', '2026-12-06');
 
 select * from books;
 
  select 
	* from books
    where title='Dune';
  
 
 
 select
	distinct(status)
    from books;