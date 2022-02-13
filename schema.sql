DROP TABLE IF EXISTS accounts;


CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT(49),
    last_name TEXT(49),
    email_add VARCHAR(255),
    contact_no INTEGER(11),
    user_name VARCHAR(15),
    user_pass VARCHAR(15),
    hours VARCHAR(15),
    user_type VARCHAR(15),
    sub_code VARCHAR(50),
    acc_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


DROP TABLE IF EXISTS subjects;
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name VARCHAR(15),
    first_name TEXT(49),
    last_name TEXT(49),
    details TEXT,
    hours_left int(10),
    date_submit TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
