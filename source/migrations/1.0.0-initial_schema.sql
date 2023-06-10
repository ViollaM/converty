CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    message text default '',
    createdat timestamp without time zone default now()
);