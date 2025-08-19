CREATE DATABASE contact_book;

USE contact_book;

CREATE TABLE contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100)
);

ALTER TABLE contacts DROP COLUMN email;

SELECT * FROM contacts;
DESCRIBE contacts