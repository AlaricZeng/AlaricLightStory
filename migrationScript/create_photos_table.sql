CREATE TABLE IF NOT EXISTS photos (
	id INT AUTO_INCREMENT,
	name VARCHAR(255) NOT NULL,
	tag VARCHAR(50),
	linked_page_index VARCHAR(255),
	uploaded_at DATETIME,
	created_at DATETIME,
	iso VARCHAR(20),
	aperture VARCHAR(20),
	shutter_speed VARCHAR(20),
	display BOOLEAN,
	PRIMARY KEY(id)
);