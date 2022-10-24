DROP TABLE import;
DROP TABLE books;
DROP TABLE book_stats;
DROP TABLE hardcopy_books;
DROP TABLE ebooks;
DROP TABLE user;
DROP TABLE librarian;
DROP TABLE holds;
DROP TABLE ebook_checkout;
DROP TABLE checkout_history;

CREATE TABLE import(
    rating          DECIMAL(3,2) not null,
    reviews         DECIMAL(4,0) not null,
    book_title      VARCHAR(1000) not null,
    description     VARCHAR(1000) not null,
    number_of_pages INTEGER(255) not null,
    type            VARCHAR(1000) not null,
    price           FLOAT(1)
);

CREATE TABLE books(
    b_bookkey       INTEGER(270) PRIMARY KEY,
    b_title         VARCHAR(1000),
    b_pages         INTEGER(255),
    b_librarian     INTEGER(20)
);

CREATE TABLE book_stats(
    bs_bookkey      INTEGER(270) PRIMARY KEY,
    bs_rating       DECIMAL(3,2),
    bs_reviews      DECIMAL(4,0),
    bs_price        FLOAT(1)
);

CREATE TABLE hardcopy_books(
    hb_bookkey      INTEGER(270) PRIMARY KEY,
    hb_userkey      INTEGER(200),
    hb_codate       DATETIME,
    hb_type         VARCHAR(50)
);

CREATE TABLE ebooks(
    e_bookkey       INTEGER(270) PRIMARY KEY,
    e_loanperiod    INTEGER(30),
    e_format        VARCHAR(50)
);

CREATE TABLE user(
    u_userkey       INTEGER(200) PRIMARY KEY,
    u_name          VARCHAR(1000),
    u_username      VARCHAR(20),
    u_password      VARCHAR(20),
    u_librariankey  INTEGER(10)
);

CREATE TABLE librarian(
    l_librariankey  INTEGER(10) PRIMARY KEY,
    l_name          VARCHAR(1000),
    l_username      VARCHAR(20),
    l_password      VARCHAR(20)
);

CREATE TABLE holds(
    h_bookkey       INTEGER(270),
    h_userkey       INTEGER(200),
    h_holdplaced    DATETIME,
    UNIQUE(h_bookkey, h_userkey)
);

CREATE TABLE ebook_checkout(
    ec_bookkey      INTEGER(270),
    ec_userkey      INTEGER(270),
    ec_codate       DATETIME,
    UNIQUE(ec_bookkey, ec_userkey)
);

CREATE TABLE checkout_history(
    ch_bookkey      INTEGER(270),
    ch_userkey      INTEGER(200),
    ch_codate       DATETIME,
    ch_cidate       DATETIME,
    UNIQUE(ch_bookkey, ch_userkey, ch_codate, ch_cidate)
);

INSERT INTO books (b_pages, b_title)
SELECT number_of_pages, book_title FROM import WHERE 1;

UPDATE books
SET b_bookkey = ROWID;

INSERT INTO hardcopy_books (hb_bookkey, hb_type)
SELECT b_bookkey, type
FROM books, import
WHERE b_title = book_title AND
    type IN ('Hardcover', 'Paperback', 'Unknown Binding');

INSERT INTO ebooks (e_bookkey, e_format)
SELECT b_bookkey, type
FROM books, import
WHERE b_title = book_title AND
    type IN ('ebook', 'Kindle Edition');

INSERT INTO book_stats (bs_bookkey, bs_rating, bs_reviews, bs_price)
SELECT b_bookkey, rating, reviews, price
FROM books, import
WHERE b_title = book_title;

CREATE TABLE hb_import (
    bookkey  INTEGER(270) PRIMARY KEY,
    userkey  INTEGER(200),
    codate   DATETIME
);

-- .import --skip 1 hardcopy_books.csv hb_import

UPDATE hardcopy_books
SET
    hb_userkey =
        (SELECT userkey FROM hb_import
        WHERE hb_bookkey = bookkey),
    hb_codate = 
        (SELECT codate FROM hb_import
        WHERE hb_bookkey = bookkey);

SELECT *
FROM ebook_checkout
ORDER BY ec_userkey;

DELETE FROM holds
WHERE h_bookkey IN
    (SELECT e_bookkey FROM ebooks);

DELETE FROM ebook_checkout
WHERE ec_bookkey IN
    (SELECT hb_bookkey FROM hardcopy_books);

DELETE FROM checkout_history
WHERE ch_bookkey IN
    (SELECT e_bookkey FROM ebooks);

SELECT *
FROM holds
ORDER BY h_bookkey;