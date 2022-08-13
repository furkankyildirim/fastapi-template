CREATE TABLE "users"
(
    id                VARCHAR PRIMARY KEY NOT NULL,
    name              VARCHAR NOT NULL,
    username          VARCHAR NOT NULL UNIQUE,
    email             VARCHAR NOT NULL UNIQUE,
    password          VARCHAR NOT NULL,
    profile_photo     VARCHAR
);