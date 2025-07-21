import os
from app import app, db, Work, BlogPost

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')

# Add all images used in /programs here
WHITELISTED_FILES = {
    'gallery1.jpg',
    'gallery3.jpg',
    'funeral.jpg',
    # Add more filenames as you use them in /programs
}

def get_referenced_files():
    referenced = set()
    # Work attachments and thumbnails
    for work in Work.query.all():
        if work.file_names:
            referenced.update([fname for fname in work.file_names.split(',') if fname])
        if work.image_filename:
            referenced.add(work.image_filename)
    # Blog images
    for blog in BlogPost.query.all():
        if blog.image_filename:
            referenced.add(blog.image_filename)
    return referenced

def cleanup_uploads():
    referenced = get_referenced_files()
    all_files = set(os.listdir(UPLOAD_FOLDER))
    orphaned = all_files - referenced - WHITELISTED_FILES
    for fname in orphaned:
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, fname))
            print(f"Deleted orphaned file: {fname}")
        except Exception as e:
            print(f"Failed to delete {fname}: {e}")
    print("Cleanup complete.")

if __name__ == "__main__":
    with app.app_context():
        cleanup_uploads() 