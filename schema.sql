
DROP TABLE IF EXISTS users;


CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT UNIQUE NOT NULL,                  
    email TEXT UNIQUE NOT NULL,           
    password TEXT NOT NULL               
);