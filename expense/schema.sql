DROP TABLE IF EXISTS expenses;

CREATE TABLE expenses (
	id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	created_on date DEFAULT NOW(),
	amount decimal(6,2) NOT NULL CHECK (amount >= 0.01),
	memo text NOT NULL
);

INSERT INTO expenses (amount, memo, created_on)
       VALUES (14.56, 'Pencils', NOW()),
              (3.29, 'Coffee', NOW()),
              (49.99, 'Text Editor', NOW());