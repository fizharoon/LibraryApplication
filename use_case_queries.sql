-- Search for book by title
-- args: search keyword
SELECT books.*, book_stats.*, hb_type,
    CASE
    WHEN hb_userkey IS NULL
        THEN 'Available'
    ELSE 'Unavailable'
    END availability
FROM books, book_stats, hardcopy_books
WHERE
    bs_bookkey = b_bookkey AND
    hb_bookkey = b_bookkey AND
    b_title LIKE '%game%'
UNION
SELECT books.*, book_stats.*, e_format, 'Available'
FROM books, book_stats, ebooks
WHERE
    bs_bookkey = b_bookkey AND
    e_bookkey = b_bookkey AND
    b_title LIKE '%game%';

----------------------------------------------------

-- User places hold
-- args: book key, user key
INSERT INTO holds (h_bookkey, h_userkey, h_holdplaced)
VALUES (69, 69, date());

-- Hold removal (testing)
DELETE FROM holds
WHERE h_bookkey = 69 AND h_userkey = 69;

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
SELECT past_checkouts + current_checkouts as total_checkouts, past.b_title
FROM
    (SELECT count() as past_checkouts, b_title
    FROM books, checkout_history
    WHERE b_bookkey = ch_bookkey
    GROUP BY b_bookkey
    ) past,
    (SELECT count() as current_checkouts, b_title
    FROM books, hardcopy_books
    WHERE
        b_bookkey = hb_bookkey AND
        hb_codate NOT NULL
    GROUP BY b_bookkey
    ) present
GROUP BY past.b_title
UNION
SELECT count() as total_checkouts, b_title
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
    WHERE ch_bookkey = 69),
    (SELECT count() as ebook_checkouts
    FROM ebook_checkout
    WHERE ec_bookkey = 69);

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