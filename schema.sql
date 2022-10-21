DROP TABLE "book";

CREATE TABLE book(
    Rating DECIMAL(3, 2),
    Reviews DECIMAL(5, 0),
    Book_title STRING(1000),
    Description STRING(1000),
    Number_Of_Pages DECIMAL(5,0),
    Type VARCHAR(50),
    Price DECIMAL(4,2)
);

select Book_title from book
WHERE Book_title LIKE "%graphic%"

CREATE TABLE user(
    u_userkey INTEGER,
    u_name STRING(500),
    u_address STRING(1000),
    u_state 
);