import sqlite3 as sl
import traceback
import sys

DB_PATH = 'faces.db'

def create_db () -> None:
	con = sl.connect(DB_PATH)
	with con:
		# Check if tables exist.
		tables = ['class', 'all_images', 'image_tags', 'untagged_images', 'tagged_faces']
		
		print("[!] Checking if all tables exist")
		for table_name in tables:
			sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
			output = con.execute(sql)

			if output.fetchone() == None:
				print(f"[!] Creating table: {table_name}")
				create_tables(con, table_name)
			
		print("[+] All tables exist")

def create_tables (con, table_name) -> None:
	
	# Create table: class
	if table_name == 'class':
		con.execute("""
			CREATE TABLE class (
				id INTEGER NOT NULL PRIMARY KEY,
				class TEXT
			);
		""")
		con.execute("""
			INSERT INTO class(id, class) VALUES (-1, 'none');
		""")

	# Create table: all_images
	if table_name == 'all_images':
		con.execute("""
			CREATE TABLE all_images (
				image_path TEXT NOT NULL PRIMARY KEY,
				tagged BOOL DEFAULT 0
			);
		""")

	# Create table: image_tags
	if table_name == 'image_tags':
		con.execute("""
			CREATE TABLE image_tags (
				image_path TEXT NOT NULL,
				face NUMBER,
				PRIMARY KEY (image_path, face)
			);
		""")

	# Create table: untagged_images
	if table_name == 'untagged_images':
		con.execute("""
			CREATE TABLE untagged_images (
				face_path TEXT PRIMARY KEY,
				complete_image_path TEXT
			);
		""")

	# Create table: tagged_faces
	if table_name == 'tagged_faces':
		con.execute("""
			CREATE TABLE tagged_faces (
				face_path TEXT PRIMARY KEY,
				class TEXT
			);
		""")

def get_classes () -> list:
	
	con = sl.connect(DB_PATH)
	cursor = con.cursor()

	rows = cursor.execute("""
		SELECT class, id FROM class;
	""")

	return rows.fetchall()

def get_class_label (id: int) -> str:
	con = sl.connect(DB_PATH)
	cursor = con.cursor()

	rows = cursor.execute("""
		SELECT class FROM class WHERE id=(?);
	""", (id,))
	return rows.fetchone()[0]

def get_training_data () -> list:
	
	con = sl.connect(DB_PATH)
	rows = con.execute("SELECT * FROM tagged_faces WHERE class!=-1")

	return rows.fetchall()

def print_error (er):
	exc_type, exc_value, exc_tb = sys.exc_info()
	print(' '.join(traceback.format_exception(exc_type, exc_value, exc_tb)))
	print('SQLite error: %s' % (' '.join(er.args)))

create_db()