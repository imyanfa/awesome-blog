wesome blog
DROP DATABASE IF EXISTS awesome_blog;
CREATE DATABASE IF NOT EXISTS awesome_blog
  DEFAULT CHARSET utf8mb4
  COLLATE utf8mb4_general_ci;
USE awesome_blog;

DROP TABLE IF EXISTS test;
CREATE TABLE test (
          id          INTEGER PRIMARY KEY AUTO_INCREMENT,
          name        VARCHAR(255),
          create_time TIMESTAMP           DEFAULT current_timestamp(), -- 创建时间
          update_time TIMESTAMP           DEFAULT current_timestamp() ON UPDATE current_timestamp() -- 更新时间
);

DROP TABLE IF EXISTS user;
CREATE TABLE user (
          `id`        INTEGER PRIMARY KEY AUTO_INCREMENT,
          `email`     VARCHAR(255) UNIQUE NOT NULL,
          `passwd`    VARCHAR(255)        NOT NULL,
          `admin`     BOOL                NOT NULL,
          `name`      VARCHAR(255)        NOT NULL,
          `image`     VARCHAR(255)        NOT NULL,
          `create_at` TIMESTAMP           DEFAULT current_timestamp(),
          `update_at` TIMESTAMP           DEFAULT current_timestamp() ON UPDATE current_timestamp(),
          KEY (`create_at`),
          KEY (`update_at`)
);

DROP TABLE IF EXISTS blog;
CREATE TABLE blog (
          `id`         INTEGER PRIMARY KEY AUTO_INCREMENT,
          `user_id`    INTEGER      NOT NULL,
          `user_name`  VARCHAR(255) NOT NULL,
          `user_image` VARCHAR(255) NOT NULL,
          `name`       VARCHAR(255) NOT NULL,
          `summary`    VARCHAR(255) NOT NULL,
          `content`    MEDIUMTEXT   NOT NULL,
          `create_at`  TIMESTAMP           DEFAULT current_timestamp(),
          `update_at`  TIMESTAMP           DEFAULT current_timestamp() ON UPDATE current_timestamp(),
          KEY (`create_at`),
          KEY (`update_at`)
);

DROP TABLE IF EXISTS comment;
CREATE TABLE comment (
          `id`         INTEGER PRIMARY KEY AUTO_INCREMENT,
          `blog_id`    INTEGER      NOT NULL,
          `user_id`    INTEGER      NOT NULL,
          `user_name`  VARCHAR(255) NOT NULL,
          `user_image` VARCHAR(255) NOT NULL,
          `content`    MEDIUMTEXT   NOT NULL,
          `create_at`  TIMESTAMP           DEFAULT current_timestamp(),
          `update_at`  TIMESTAMP           DEFAULT current_timestamp() ON UPDATE current_timestamp(),
          KEY (`create_at`),
          KEY (`update_at`)
);
