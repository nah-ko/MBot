BEGIN;

CREATE SEQUENCE news_test_id_seq;

CREATE TABLE news_test (
  id INT4 DEFAULT nextval('news_test_id_seq'),
  site text,
  DATE text,
  de text,
  sujet text,
  message text,
  id_img INT4 NOT NULL DEFAULT '0',
  PRIMARY KEY (id)

);

CREATE SEQUENCE photo_test_id_seq;

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

CREATE INDEX id_news_test_index ON news_test (id);

CREATE INDEX id_photo_test_index ON photo_test (id);

SELECT SETVAL('news_test_id_seq',(select case when max(id)>0 then max(id)+1 else 1 end from news_test));

SELECT SETVAL('photo_test_id_seq',(select case when max(id)>0 then max(id)+1 else 1 end from photo_test));

COMMIT;
