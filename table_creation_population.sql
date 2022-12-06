.mode csv
.separator ','

DROP TABLE import;
DROP TABLE hb_import;
DROP TABLE books;
DROP TABLE book_stats;
DROP TABLE hardcopy_books;
DROP TABLE ebooks;
DROP TABLE user;
DROP TABLE librarian;
DROP TABLE holds;
DROP TABLE ebook_checkout;
DROP TABLE checkout_history;

-- Define schema for tables
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
    hb_userkey      INTEGER(200) REFERENCES user(u_userkey),
    hb_codate       DATETIME,
    hb_type         VARCHAR(50),
    CHECK (hb_type IN ('Hardcover', 'Paperback', 'Unknown Binding', 'Boxed Set - Hardcover'))
);

CREATE TABLE ebooks(
    e_bookkey       INTEGER(270) PRIMARY KEY,
    e_loanperiod    INTEGER(30) DEFAULT '1000 days',
    e_format        VARCHAR(50),
    CHECK (e_format in ('ebook', 'Kindle Edition'))
);

CREATE TABLE user(
    u_userkey       INTEGER(200) PRIMARY KEY,
    u_name          VARCHAR(1000),
    u_username      VARCHAR(20),
    u_password      VARCHAR(20),
    u_librariankey  INTEGER(10),
    u_address       VARCHAR(1000),
    u_phone         VARCHAR(500)
);

CREATE TABLE librarian(
    l_librariankey  INTEGER(10) PRIMARY KEY,
    l_name          VARCHAR(1000),
    l_username      VARCHAR(20),
    l_password      VARCHAR(20)
);

CREATE TABLE holds(
    h_bookkey       INTEGER(270) REFERENCES hardcopy_books(hb_bookkey),
    h_userkey       INTEGER(200) REFERENCES user(u_userkey),
    h_holdplaced    DATETIME,
    h_status        VARCHAR(10) DEFAULT 'ACTIVE',
    UNIQUE(h_bookkey, h_userkey, h_holdplaced)
);

CREATE TABLE ebook_checkout(
    ec_bookkey      INTEGER(270) REFERENCES ebooks(e_bookkey),
    ec_userkey      INTEGER(270) REFERENCES user(u_userkey),
    ec_codate       DATETIME,
    UNIQUE(ec_bookkey, ec_userkey, ec_codate)
);

CREATE TABLE checkout_history(
    ch_bookkey      INTEGER(270) REFERENCES hardcopy_books(hb_bookkey),
    ch_userkey      INTEGER(200) REFERENCES user(u_userkey),
    ch_codate       DATETIME,
    ch_cidate       DATETIME,
    UNIQUE(ch_bookkey, ch_userkey, ch_codate, ch_cidate)
);

.import --skip 1 prog_book.csv import

-- Run this after importing full book dataset into import table
INSERT INTO books (b_pages, b_title)
SELECT number_of_pages, book_title FROM import WHERE 1;

-- Define book keys by row id (arbitrary but will be kept consistent)
UPDATE books
SET b_bookkey = ROWID;

-- Put all hard copy books into a table
INSERT INTO hardcopy_books (hb_bookkey, hb_type)
SELECT b_bookkey, type
FROM books, import
WHERE b_title = book_title AND
    b_bookkey NOT IN (SELECT hb_bookkey FROM hardcopy_books) AND
    type IN ('Hardcover', 'Paperback', 'Unknown Binding', 'Boxed Set - Hardcover');

-- Put all ebooks into a table
INSERT INTO ebooks (e_bookkey, e_format)
SELECT b_bookkey, type
FROM books, import
WHERE b_title = book_title AND
    type IN ('ebook', 'Kindle Edition');

-- Populate book stats from import table
INSERT INTO book_stats (bs_bookkey, bs_rating, bs_reviews, bs_price)
SELECT b_bookkey, rating, reviews, price
FROM books, import
WHERE b_title = book_title;

-- Schema for importing mock hard copy checkout data
CREATE TABLE hb_import (
    bookkey  INTEGER(270) PRIMARY KEY,
    userkey  INTEGER(200),
    codate   DATETIME
);

CREATE TABLE moreuser (
    id INTEGER(270) PRIMARY KEY,
    u_address VARCHAR(500),
    u_phone VARCHAR(500)
);

.import --skip 1 Librarian.csv librarian
.import --skip 1 user.csv user
.import --skip 1 moreuser.csv moreuser

UPDATE user
SET 
    u_address = (select u_address from moreuser
                where u_userkey = id),
    u_phone = (select u_phone from moreuser
                where u_userkey = id);

.import --skip 1 hardcopy_books.csv hb_import

-- ch_codate + days(random(0, date_diff('days', ch_codate, date('2022-06-30'))))

-- Set hard copy books as being checked out based on mock data
UPDATE hardcopy_books
SET
    hb_userkey =
        (SELECT userkey FROM hb_import
        WHERE hb_bookkey = bookkey),
    hb_codate = 
        (SELECT codate FROM hb_import
        WHERE hb_bookkey = bookkey);

CREATE TABLE temp(
    h_bookkey       INTEGER(270) REFERENCES hardcopy_books(hb_bookkey),
    h_userkey       INTEGER(200) REFERENCES user(u_userkey),
    h_holdplaced    DATETIME,
    h_status        VARCHAR(10) DEFAULT 'ACTIVE',
    UNIQUE(h_bookkey, h_userkey, h_holdplaced)
);

.import --skip 1 holds.csv temp

INSERT INTO holds(h_bookkey, h_userkey, h_holdplaced)
SELECT h_bookkey, h_userkey, h_holdplaced
FROM temp;

DROP TABLE temp;

-- Remove ebooks from holds table (ebooks can't be held)
-- DELETE FROM holds
-- WHERE h_bookkey IN
--     (SELECT e_bookkey FROM ebooks);

.import --skip 1 ebook_checkout.csv ebook_checkout

-- Remove hard copy books from ebook checkout table
-- DELETE FROM ebook_checkout
-- WHERE ec_bookkey IN
--     (SELECT hb_bookkey FROM hardcopy_books);

.import --skip 1 checkout_history.csv checkout_history

-- Remove ebooks from hard copy checkout table
-- DELETE FROM checkout_history
-- WHERE ch_bookkey IN
--     (SELECT e_bookkey FROM ebooks);

DROP TABLE moreuser;
DROP TABLE import;
DROP TABLE hb_import;

-- :::NOTE:::
-- Imports don't seem to work unless sqlite engine is launched from same directory as csv files
-- cd data\ files
-- sqlite3 ../progbooks.db

INSERT INTO librarian (l_librariankey, l_name, l_username, l_password)
VALUES (11, 'Robert', 'robert', '2345');