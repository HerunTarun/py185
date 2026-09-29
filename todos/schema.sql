CREATE TABLE lists (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title varchar(255) NOT NULL UNIQUE
);

CREATE TABLE todos (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title text NOT NULL,
    completed boolean NOT NULL DEFAULT false,
    list_id integer NOT NULL REFERENCES lists(id) ON DELETE CASCADE
);