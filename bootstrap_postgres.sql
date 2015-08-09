-- make sure the user exists
DO
$body$
BEGIN
  IF NOT EXISTS (
    SELECT *
    FROM pg_catalog.pg_user
    WHERE usename = 'ffldata'
  ) THEN
    CREATE ROLE ffldata LOGIN PASSWORD 'ffldata';
  END IF;
END
$body$
;

-- create the database
CREATE DATABASE ffldata OWNER ffldata;

-- connect to the database we just created
\c ffldata

-- create the raw_data table
BEGIN;
  CREATE TABLE raw_data (
    ffl_source text,
    playername text,
    team text,
    pos text,
    status_type text,
    passing_c real,
    passing_a real,
    passing_yds real,
    passing_td real,
    passing_int real,
    rushing_r real,
    rushing_yds real,
    rushing_td real,
    receiving_rec real,
    receiving_yds real,
    receiving_tot real,
    pts_total real,
    parsed_on timestamp,
    PRIMARY KEY (ffl_source, playername, pos, team)
  );
COMMIT;

BEGIN;
GRANT ALL PRIVILEGES ON TABLE raw_data TO ffldata;
COMMIT;
