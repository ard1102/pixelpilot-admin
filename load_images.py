import sqlite3
import os
from datetime import datetime

DATABASE = 'site.db'
IMAGE_DIR = 'images'


def load_initial_data():
    # Ensure images directory exists to avoid errors
    if not os.path.isdir(IMAGE_DIR):
        os.makedirs(IMAGE_DIR, exist_ok=True)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 1. Run the schema to create the table if it doesn't exist
    with open('schema.sql', 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())

    # 2. Recursively scan the images directory for supported files
    now = datetime.now()
    image_paths = []
    for root, _, files in os.walk(IMAGE_DIR):
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, IMAGE_DIR)
                # Normalize to forward slashes for consistency across platforms
                rel_path = rel_path.replace("\\", "/")
                image_paths.append(rel_path)

    # 3. Insert or ignore
    inserted = 0
    for rel_path in image_paths:
        try:
            cursor.execute(
                '''
                INSERT INTO images (filename, status, date_uploaded)
                VALUES (?, ?, ?)
                ''',
                (rel_path, 'pending', now)
            )
            print(f"[+] Inserted: {rel_path}")
            inserted += 1
        except sqlite3.IntegrityError:
            print(f"[!] Skipping: {rel_path} (Already exists)")

    total = cursor.execute('SELECT COUNT(*) FROM images').fetchone()[0]
    conn.commit()
    conn.close()
    print(
        f"\n--- Database setup complete. {len(image_paths)} images processed, "
        f"{inserted} inserted. Total rows: {total}. ---"
    )


if __name__ == '__main__':
    load_initial_data()