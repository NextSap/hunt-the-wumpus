CREATE TABLE users (
    id SERIAL,
    username varchar(50),
    password varchar(50),
    victory numeric DEFAULT 0,
    defeat_wumpus numeric DEFAULT 0,
    defeat_pit numeric DEFAULT 0
)