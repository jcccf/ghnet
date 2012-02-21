CREATE TABLE forks (
  glogin VARCHAR(255) NOT NULL,
  gname VARCHAR(255) NOT NULL,
  gno INT(10) UNSIGNED NOT NULL,
  parent_glogin VARCHAR(255),
  parent_gname VARCHAR(255),
  json TEXT NOT NULL,
  created_at TIMESTAMP,
  root_gname VARCHAR(255) NOT NULL,
  PRIMARY KEY (glogin, gname, gno)
);

CREATE TABLE commits (
	glogin VARCHAR(255) NOT NULL,
	gname VARCHAR(255) NOT NULL,
	gno INT(10) UNSIGNED NOT NULL,
	json MEDIUMTEXT NOT NULL,
	created_at TIMESTAMP,
	PRIMARY KEY (glogin, gname, gno)
);

CREATE TABLE issues (
	glogin VARCHAR(255) NOT NULL,
	gname VARCHAR(255) NOT NULL,
	gno INT(10) UNSIGNED NOT NULL,
	is_open INT(1) UNSIGNED NOT NULL,
	json MEDIUMTEXT NOT NULL,
	created_at TIMESTAMP,
	PRIMARY KEY (glogin, gname, gno, is_open)
);

CREATE TABLE pull_requests (
	glogin VARCHAR(255) NOT NULL,
	gname VARCHAR(255) NOT NULL,
	gno INT(10) UNSIGNED NOT NULL,
	is_open INT(1) UNSIGNED NOT NULL,
	json MEDIUMTEXT NOT NULL,
	created_at TIMESTAMP,
	PRIMARY KEY (glogin, gname, gno, is_open)
);


CREATE TABLE commits_detailed (
	glogin VARCHAR(255) NOT NULL,
	gname VARCHAR(255) NOT NULL,
	sha VARCHAR(255) NOT NULL,
	commit_date DATETIME NOT NULL,
	json MEDIUMTEXT NOT NULL,
	created_at TIMESTAMP,
	PRIMARY KEY (glogin, gname, sha)
);

CREATE TABLE repos (
	glogin VARCHAR(255) NOT NULL,
	gname VARCHAR(255) NOT NULL,
	json TEXT NOT NULL,
	created_at TIMESTAMP,
	PRIMARY KEY (glogin, gname)
);

CREATE TABLE queues (
	id INT(10) UNSIGNED NOT NULL auto_increment,
	k VARCHAR(255) NOT NULL,
	v TEXT NOT NULL,
	in_use INT(1) DEFAULT 0,
	created_at TIMESTAMP,
	PRIMARY KEY(id)
);

CREATE TABLE trending (
  glogin varchar(255) NOT NULL,
  gname varchar(255) NOT NULL,
  url varchar(255) NOT NULL,
  rtype varchar(255) NOT NULL,
  created_at TIMESTAMP,
  PRIMARY KEY(glogin, gname)
);