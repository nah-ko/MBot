-- Test tables for PostgreSQL
-- You will need to create a database before !!
-- $Id$

BEGIN;

-- Sequences creation

CREATE SEQUENCE news_test_id_seq;

CREATE SEQUENCE photo_test_id_seq;

-- Tables structures creation

CREATE TABLE news_test (
  id INT4 DEFAULT nextval('news_test_id_seq'),
  site text,
  DATE timestamp,
  de text,
  sujet text,
  message text,
  id_img INT4 NOT NULL DEFAULT '0',
  PRIMARY KEY (id)

);

CREATE TABLE photo_test (
  id INT4 DEFAULT nextval('photo_test_id_seq'),
  description varchar(50) DEFAULT NULL,
  img_data oid,
  tnimg_data oid,
  filename varchar(50) DEFAULT NULL,
  filesize varchar(50) DEFAULT NULL,
  filetype varchar(50) DEFAULT NULL,
  PRIMARY KEY (id)

);

-- Privileges for tables need user 'nes' to be created before

REVOKE ALL ON TABLE photo_test FROM PUBLIC;
GRANT INSERT,SELECT,UPDATE ON TABLE photo_test TO news;

REVOKE ALL ON TABLE news_test FROM PUBLIC;
GRANT INSERT,SELECT,UPDATE ON TABLE news_test TO news;

-- Indexes creation

CREATE INDEX id_news_test_index ON news_test USING btree (id);

CREATE INDEX id_photo_test_index ON photo_test USING btree (id);

-- Sequences options creation

SELECT SETVAL('news_test_id_seq',(select case when max(id)>0 then max(id)+1 else 1 end from news_test));

SELECT SETVAL('photo_test_id_seq',(select case when max(id)>0 then max(id)+1 else 1 end from photo_test));

-- Primary keys and references

ALTER TABLE ONLY news_test
    ADD CONSTRAINT news_test_pkey PRIMARY KEY (id);

ALTER TABLE ONLY photo_test
    ADD CONSTRAINT photo_test_pkey PRIMARY KEY (id);

ALTER TABLE ONLY news_test
    ADD CONSTRAINT constraint_id_img FOREIGN KEY (id_img) REFERENCES photo_test(id) ON UPDATE NO ACTION ON DELETE CASCADE;

COMMIT;
