CREATE TABLE IF NOT EXISTS stories (
	id INT AUTO_INCREMENT,
	title VARCHAR(255) NOT NULL,
	created_at DATETIME,
	PRIMARY KEY(id)
);