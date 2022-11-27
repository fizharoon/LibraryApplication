-- Search for book by title
-- args: search 
SELECT b_title, b_pages, bs_rating, hb_type,
    CASE
    WHEN hb_userkey IS NULL
        THEN 'Available'
    ELSE 'Unavailable'
    END availability
FROM books, book_stats, hardcopy_books
WHERE
    bs_bookkey = b_bookkey AND
    hb_bookkey = b_bookkey AND
    b_title LIKE '%computer%'
UNION
SELECT b_title, b_pages, bs_rating, e_format, 'Available'
FROM books, book_stats, ebooks
WHERE
    bs_bookkey = b_bookkey AND
    e_bookkey = b_bookkey AND
    b_title LIKE '%computer%';

SELECT *
FROM book_search
WHERE b_title LIKE '%computer%';

----------------------------------------------------

-- Show all books in alphabetical order by title
SELECT b_title, b_pages, bs_rating, hb_type,
    CASE
    WHEN hb_userkey IS NULL
        THEN 'Available'
    ELSE 'Unavailable'
    END availability
FROM books, book_stats, hardcopy_books
WHERE
    bs_bookkey = b_bookkey AND
    hb_bookkey = b_bookkey
UNION
SELECT b_title, b_pages, bs_rating, e_format, 'Available'
FROM books, book_stats, ebooks
WHERE
    bs_bookkey = b_bookkey AND
    e_bookkey = b_bookkey
ORDER BY b_title;

----------------------------------------------------

-- Show all books in increasing order of page count
SELECT b_title, b_pages, bs_rating, hb_type,
    CASE
    WHEN hb_userkey IS NULL
        THEN 'Available'
    ELSE 'Unavailable'
    END availability
FROM books, book_stats, hardcopy_books
WHERE
    bs_bookkey = b_bookkey AND
    hb_bookkey = b_bookkey
UNION
SELECT b_title, b_pages, bs_rating, e_format, 'Available'
FROM books, book_stats, ebooks
WHERE
    bs_bookkey = b_bookkey AND
    e_bookkey = b_bookkey
ORDER BY b_pages;

----------------------------------------------------

-- Show all books in decreasing order of rating
SELECT b_title, b_pages, bs_rating, hb_type,
    CASE
    WHEN hb_userkey IS NULL
        THEN 'Available'
    ELSE 'Unavailable'
    END availability
FROM books, book_stats, hardcopy_books
WHERE
    bs_bookkey = b_bookkey AND
    hb_bookkey = b_bookkey
UNION
SELECT b_title, b_pages, bs_rating, e_format, 'Available'
FROM books, book_stats, ebooks
WHERE
    bs_bookkey = b_bookkey AND
    e_bookkey = b_bookkey
ORDER BY bs_rating DESC;

----------------------------------------------------

-- User places hold
-- args: book key, user key
INSERT INTO holds (h_bookkey, h_userkey, h_holdplaced)
VALUES (69, 69, date());

-- Hold removal (testing)
DELETE FROM holds
WHERE h_bookkey = 1 AND h_userkey = 201;

----------------------------------------------------

-- User checks out book
-- args: book key, user key
UPDATE hardcopy_books
SET
    hb_userkey = 69,
    hb_codate = DATE()
WHERE hb_bookkey = 69;

INSERT INTO ebook_checkout (ec_bookkey, ec_userkey, ec_codate)
SELECT e_bookkey, 69, DATE()
FROM ebooks
WHERE e_bookkey = 69;

----------------------------------------------------

-- User returns book
-- args: book key
INSERT INTO checkout_history (ch_bookkey, ch_userkey, ch_codate, ch_cidate)
SELECT hb_bookkey, hb_userkey, hb_codate, DATE()
FROM hardcopy_books
WHERE hb_bookkey = 69;

UPDATE hardcopy_books
SET
    hb_userkey = NULL,
    hb_codate = NULL
WHERE hb_bookkey = 69;

-- History deletion (for testing)
DELETE FROM checkout_history WHERE ch_bookkey = 69;

----------------------------------------------------

-- Count how many times each book has been held, past, present, future
SELECT count() as total_holds, b_bookkey
FROM books, holds
WHERE b_bookkey = h_bookkey
GROUP BY b_bookkey
ORDER BY total_holds DESC;

----------------------------------------------------

-- Count how many times a specific book has been held
-- args: book key
SELECT count() as total_holds
FROM holds
WHERE h_bookkey = 69;

----------------------------------------------------

-- Count how many times each book has been checked out
SELECT past_checkouts + current_checkouts as total_checkouts, past.b_bookkey
FROM
    (SELECT count() as past_checkouts, b_bookkey
    FROM books, checkout_history
    WHERE b_bookkey = ch_bookkey
    GROUP BY b_bookkey
    ) past,
    (SELECT count() as current_checkouts, b_bookkey
    FROM books, hardcopy_books
    WHERE
        b_bookkey = hb_bookkey AND
        hb_codate NOT NULL
    GROUP BY b_bookkey
    ) present
GROUP BY past.b_bookkey
UNION
SELECT count() as total_checkouts, b_bookkey
FROM books, ebook_checkout
WHERE b_bookkey = ec_bookkey
GROUP BY b_bookkey
ORDER BY total_checkouts DESC;

----------------------------------------------------

-- Count how many times a specific book has been checked out, past only
-- args: book key
SELECT hardcopy_checkouts + ebook_checkouts as total_checkouts
FROM
    (SELECT count() as hardcopy_checkouts
    FROM checkout_history
    WHERE ch_bookkey = 79),
    (SELECT count() as ebook_checkouts
    FROM ebook_checkout
    WHERE ec_bookkey = 79);

----------------------------------------------------

-- List a specific user's current holds
-- args: user key
SELECT h_bookkey
FROM holds
WHERE h_userkey = 69;

----------------------------------------------------

-- List a specific user's current checkouts
-- args: user key
SELECT hb_bookkey as book_key, hb_type as book_format
FROM hardcopy_books
WHERE hb_userkey = 69
UNION
SELECT ec_bookkey, e_format
FROM ebook_checkout, ebooks
WHERE
    ec_bookkey = e_bookkey AND
    ec_userkey = 69 AND
    DATE(ec_codate, e_loanperiod) > DATE();

----------------------------------------------------

-- find a kindle edition book
select b_title from books, ebooks 
where b_bookkey = e_bookkey
    and e_format = 'Kindle Edition'

----------------------------------------------------

-- find paperback books
select b_title from books, hardcopy_books
where b_bookkey = hb_bookkey
    and hb_type = 'Paperback'

----------------------------------------------------

-- librarian inserts user into user table
-- args: librarian key
INSERT INTO user VALUES ((SELECT max(ch_userkey) FROM checkout_history)+1, "Stella Chang", "schang99", "sdfeIdf", 9, '123 Sesame St', '209-555-5555')

----------------------------------------------------

-- librarian removes user
-- args: user key
DELETE FROM user
WHERE u_userkey = 201

----------------------------------------------------

-- how many books each user has checked out
select u_userkey, u_name, count(hb_bookkey) 
from user , hardcopy_books
where u_userkey = hb_userkey
group by u_userkey

----------------------------------------------------

-- find specific user 
select * from user 
where u_name = 'Camala Wedgbrow'

----------------------------------------------------

-- update user's information
update user 
set u_address = '42958 Katie Drive'
where u_userkey = 1

----------------------------------------------------

-- List user's holds and whether they can be checked out now
-- args: userkey
SELECT b_title, h_holdplaced,
    CASE
    WHEN hb_userkey IS NULL
        THEN 'Available'
    ELSE 'Unavailable'
    END availability
FROM books, holds LEFT OUTER JOIN
    (SELECT * FROM hardcopy_books WHERE hb_userkey IS NOT NULL)
    ON h_bookkey = hb_bookkey
WHERE
    b_bookkey = h_bookkey AND
    h_userkey = 69;

----------------- INDEXES -----------------

CREATE INDEX ebook_checkout_idx_ec_userkey ON ebook_checkout(ec_userkey);
CREATE INDEX hardcopy_books_idx_hb_userkey ON hardcopy_books(hb_userkey);

----------------- VIEWS -----------------

DROP VIEW book_search;
CREATE VIEW book_search(b_bookkey, b_title, b_pages, b_rating, b_type, b_availability) AS
SELECT b_bookkey, b_title, b_pages, bs_rating, hb_type,
    CASE
    WHEN hb_userkey IS NULL
        THEN 'Available'
    ELSE 'Unavailable'
    END availability
FROM books, book_stats, hardcopy_books
WHERE
    bs_bookkey = b_bookkey AND
    hb_bookkey = b_bookkey
UNION
SELECT b_bookkey, b_title, b_pages, bs_rating, e_format, 'Available'
FROM books, book_stats, ebooks
WHERE
    bs_bookkey = b_bookkey AND
    e_bookkey = b_bookkey;

DROP VIEW book_info;
CREATE VIEW book_info(b_bookkey, b_title, b_pages, b_rating, b_format, b_checkedOutBy, b_totalholds, b_totalcheckouts) AS
SELECT b_bookkey, b_title, b_pages, bs_rating, hb_type, hb_userkey, IFNULL(total_holds, 0) total_holds, IFNULL(total_checkouts, 0) total_checkouts
FROM books, book_stats, hardcopy_books
    LEFT OUTER JOIN
    (SELECT h_bookkey, count() as total_holds FROM holds GROUP BY h_bookkey) tholds ON hb_bookkey = tholds.h_bookkey
    LEFT OUTER JOIN
    (SELECT ch_bookkey, count() as total_checkouts FROM checkout_history GROUP BY ch_bookkey) tcheckouts ON hb_bookkey = tcheckouts.ch_bookkey
WHERE
    b_bookkey = bs_bookkey AND
    b_bookkey = hb_bookkey
UNION
SELECT b_bookkey, b_title, b_pages, bs_rating, e_format, 'n/a', 'n/a', total_checkouts
FROM books, book_stats, ebooks
    LEFT OUTER JOIN
    (SELECT ec_bookkey, count() as total_checkouts FROM ebook_checkout GROUP BY ec_bookkey) tcheckouts ON e_bookkey = tcheckouts.ec_bookkey
WHERE
    b_bookkey = bs_bookkey AND
    b_bookkey = e_bookkey;

CREATE VIEW user_checkouts(b_userkey, b_bookkey, b_title, b_format, b_checkout, b_remaining) AS
SELECT hb_userkey, b_bookkey, b_title, hb_type as book_format, hb_codate, 'n/a' as remaining
FROM hardcopy_books, books
WHERE
    hb_userkey NOT NULL AND
    hb_bookkey = b_bookkey
UNION
SELECT ec_userkey, b_bookkey, b_title, e_format, ec_codate,
    ROUND(JULIANDAY(ec_codate, e_loanperiod) - JULIANDAY(DATE())) as remaining
FROM ebook_checkout, ebooks, books
WHERE
    e_bookkey = b_bookkey AND
    ec_bookkey = e_bookkey AND
    DATE(ec_codate, e_loanperiod) > DATE();

DROP VIEW user_holds;
CREATE VIEW user_holds(b_userkey, b_bookkey, b_title, b_holdplaced, b_availability) AS
SELECT h_userkey, b_bookkey, b_title, h_holdplaced,
    CASE
    WHEN hb_userkey IS NULL
        THEN 'Available'
    ELSE 'Unavailable'
    END availability
FROM books, holds LEFT OUTER JOIN
    (SELECT * FROM hardcopy_books WHERE hb_userkey IS NOT NULL)
    ON h_bookkey = hb_bookkey
WHERE
    h_status = 'ACTIVE' AND
    b_bookkey = h_bookkey
ORDER BY h_holdplaced;

SELECT book_search.*,
    CASE
    WHEN SQ1.b_userkey IS NULL
        THEN FALSE
    ELSE TRUE
    END isCheckedOut,
    CASE
    WHEN SQ2.h_userkey IS NULL
        THEN FALSE
    ELSE TRUE
    END isHeld
FROM book_search LEFT JOIN
    (SELECT * FROM user_checkouts WHERE b_userkey = 1) SQ1
        ON book_search.b_bookkey = SQ1.b_bookkey
    LEFT JOIN
    (SELECT * FROM holds WHERE h_userkey = 1) SQ2
        ON book_search.b_bookkey = SQ2.h_bookkey;

CREATE VIEW user_info(u_userkey, u_name, u_username, u_password, u_librariankey, u_address, u_phone, u_pastcheckouts, u_curcheckouts, u_curholds) AS
SELECT user.*,
    IFNULL(past_checkouts, 0) as past_checkouts,
    IFNULL(current_checkouts + ebook_checkouts, 0) as current_checkouts,
    IFNULL(cur_holds, 0) as cur_holds
FROM user LEFT OUTER JOIN
    (SELECT ch_userkey, count() past_checkouts
        FROM checkout_history GROUP BY ch_userkey)
        ON u_userkey = ch_userkey LEFT OUTER JOIN
    (SELECT hb_userkey, count() current_checkouts
        FROM hardcopy_books GROUP BY hb_userkey)
        ON u_userkey = hb_userkey LEFT OUTER JOIN
    (SELECT ec_userkey, count() ebook_checkouts
        FROM ebook_checkout GROUP BY ec_userkey)
        ON u_userkey = ec_userkey LEFT OUTER JOIN
    (SELECT h_userkey, count() cur_holds
        FROM holds GROUP BY h_userkey)
        ON u_userkey = h_userkey;

SELECT max(userkey)
FROM
    (SELECT max(u_userkey) as userkey FROM user
    UNION
    SELECT max(ch_userkey) as userkey FROM checkout_history
    UNION
    SELECT max(ec_userkey) as userkey FROM ebook_checkout
    UNION
    SELECT max(h_userkey) as userkey FROM holds
    )