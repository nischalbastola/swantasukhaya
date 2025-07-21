from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from werkzeug.utils import secure_filename
import uuid
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
from functools import wraps
from sqlalchemy import or_

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(30))
    interest = db.Column(db.String(50))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Admin(UserMixin):
    id = 1
    username = "admin"
    password = "admin123"  # Change this in production
    def get_id(self):
        return "admin"

class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    file_names = db.Column(db.Text)  # comma-separated filenames
    image_filename = db.Column(db.String(120), nullable=True)  # thumbnail image
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)  # staff owner

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_filename = db.Column(db.String(120), nullable=True)
    file_attachment = db.Column(db.String(120), nullable=True)  # New column
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)

    # def __repr__(self):
    #     return f"BlogPost(title='{self.title}', author_name='{self.author_name}', date='{self.date_posted}')"

class Staff(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    if user_id == "admin":
        return Admin()
    try:
        staff_id = int(user_id)
    except (ValueError, TypeError):
        pass
    return Staff.query.get(staff_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/initiatives')
def initiatives():
    return render_template('programs.html')

@app.route('/initiatives/<program_id>')
def initiative_detail(program_id):
    # Define all programs data
    programs_data = {
        "funeral": {"id": "funeral", "title": "Funeral Assistance", "desc": "Providing financial support for dignified funeral ceremonies for poor families.", "bg": "images/funeral.jpg"},
        "education-centers": {"id": "education-centers", "title": "Education Centers", "desc": "Helping set up centers to provide free education for children in need.", "bg": "images/education.jpg"},
        "free-education": {"id": "free-education", "title": "Free Education", "desc": "Offering books, tuition, and educational guidance for underprivileged children.", "bg": "images/education.jpg"},
        "uniform": {"id": "uniform", "title": "Uniform Distribution", "desc": "Distributing school bags, shoes, sweaters, uniforms, and stationery to needy students.", "bg": "images/education.jpg"},
        "eye-camp": {"id": "eye-camp", "title": "Eye Camp", "desc": "Organizing free eye check-ups, providing glasses, and arranging cataract surgeries.", "bg": "images/education.jpg"},
        "stationery": {"id": "stationery", "title": "Stationery Distribution", "desc": "Distributing pens, notebooks, pencils, and other school supplies to children.", "bg": "images/education.jpg"},
        "motivation": {"id": "motivation", "title": "Motivation Events", "desc": "Conducting sessions to inspire children about education, confidence, and social responsibility.", "bg": "images/education.jpg"},
        "fund": {"id": "fund", "title": "Securing Fund", "desc": "Managing collected funds transparently for supporting needy individuals.", "bg": "images/education.jpg"},
        "collaboration": {"id": "collaboration", "title": "Collaboration", "desc": "Partnering with other social organizations to maximize social impact.", "bg": "images/education.jpg"},
        "hope": {"id": "hope", "title": "Hope & Confidence", "desc": "Empowering children by instilling hope, self-worth, and encouraging them towards education.", "bg": "images/education.jpg"},
        "awareness": {"id": "awareness", "title": "Support & Awareness", "desc": "Raising awareness about poverty, education, health, spirituality, and social equality.", "bg": "images/education.jpg"}
    }
    program = programs_data.get(program_id)
    if not program:
        return redirect(url_for('initiatives'))
    return render_template('program_detail.html', program=program)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone')
        interest = request.form.get('interest')
        message = request.form['message']
        new_msg = Message(name=name, email=email, phone=phone, interest=interest, message=message)
        db.session.add(new_msg)
        db.session.commit()
        flash('Message sent! Thank you for contacting us.')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == Admin.username and password == Admin.password:
            login_user(Admin())
            session.permanent = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('admin_login.html')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.get_id() != 'admin':
            flash('Please log in first', 'error')
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/messages')
@admin_required
def admin_messages():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return render_template('admin_messages.html', messages=messages)

@app.route('/admin/logout')
@admin_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/work')
def work():
    q = request.args.get('q', '').strip()
    if q:
        works = Work.query.filter(
            or_(Work.title.ilike(f'%{q}%'), Work.content.ilike(f'%{q}%'))
        ).order_by(Work.created_at.desc()).all()
    else:
        works = Work.query.order_by(Work.created_at.desc()).all()
    return render_template('notice.html', works=works)

@app.route('/work/<int:work_id>')
def work_detail(work_id):
    work = Work.query.get_or_404(work_id)
    return render_template('notice_detail.html', work=work)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin/work', methods=['GET', 'POST'])
@admin_required
def admin_work():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_filename = None
        image = request.files.get('image')
        if image and image.filename and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            base, ext = os.path.splitext(filename)
            unique_filename = filename
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)):
                unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
            try:
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                image_filename = unique_filename
            except Exception as e:
                flash(f"Failed to upload thumbnail: {str(e)}", 'error')
        files = request.files.getlist('files[]')
        saved_files = []
        for file in files:
            if file and file.filename:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    base, ext = os.path.splitext(filename)
                    unique_filename = filename
                    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)):
                        unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
                    try:
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                        saved_files.append(unique_filename)
                    except Exception as e:
                        flash(f"Failed to upload {filename}: {str(e)}", 'error')
                else:
                    flash(f"File type not allowed: {file.filename}", 'error')
        file_names = ','.join(saved_files)
        new_work = Work(title=title, content=content, file_names=file_names, image_filename=image_filename)
        db.session.add(new_work)
        db.session.commit()
        flash('Work added!')
        return redirect(url_for('admin_work'))
    works = Work.query.order_by(Work.created_at.desc()).all()
    return render_template('admin_notice.html', works=works)

@app.route('/admin/work/delete/<int:work_id>', methods=['POST'])
@admin_required
def delete_work(work_id):
    work = Work.query.get_or_404(work_id)
    if work.file_names:
        for fname in work.file_names.split(','):
            if fname:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                except Exception:
                    pass
    db.session.delete(work)
    db.session.commit()
    flash('Work deleted!')
    return redirect(url_for('admin_work'))

@app.route('/admin/work/edit/<int:work_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_work(work_id):
    work = Work.query.get_or_404(work_id)
    if request.method == 'POST':
        work.title = request.form['title']
        work.content = request.form['content']
        image = request.files.get('image')
        remove_image = request.form.get('remove_image')
        if remove_image == 'on' and work.image_filename:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], work.image_filename))
            except OSError:
                pass
            work.image_filename = None
        if image and image.filename and allowed_file(image.filename):
            if work.image_filename:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], work.image_filename))
                except OSError:
                    pass
            filename = secure_filename(image.filename)
            base, ext = os.path.splitext(filename)
            unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            work.image_filename = unique_filename
        remove_files = request.form.getlist('remove_files')
        current_files = [fname for fname in (work.file_names or '').split(',') if fname]
        for fname in remove_files:
            if fname in current_files:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                except Exception:
                    pass
                current_files.remove(fname)
        files = request.files.getlist('files[]')
        for file in files:
            if file and file.filename:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    base, ext = os.path.splitext(filename)
                    unique_filename = filename
                    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)):
                        unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
                    try:
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                        current_files.append(unique_filename)
                    except Exception as e:
                        flash(f"Failed to upload {filename}: {str(e)}", 'error')
                else:
                    flash(f"File type not allowed: {file.filename}", 'error')
        work.file_names = ','.join(current_files)
        db.session.commit()
        flash('Work updated successfully!')
        return redirect(url_for('admin_work'))
    return render_template('admin_edit_notice.html', work=work)

@app.route('/admin/messages/delete/<int:msg_id>', methods=['POST'])
@admin_required
def delete_message(msg_id):
    msg = Message.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted!')
    return redirect(url_for('admin_messages'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/blogs')
def blogs():
    search_query = request.args.get('q')
    if search_query:
        posts = BlogPost.query.filter(
            or_(
                BlogPost.title.ilike(f'%{search_query}%'),
                BlogPost.content.ilike(f'%{search_query}%'),
                BlogPost.author_name.ilike(f'%{search_query}%')
            )
        ).order_by(BlogPost.date_posted.desc()).all()
    else:
        posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).all()
    return render_template('blogs.html', posts=posts)

@app.route('/admin/blogs', methods=['GET', 'POST'])
@admin_required
def admin_blogs():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        content = request.form['content']
        image = request.files.get('image')
        files = request.files.getlist('files[]')

        image_filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            base, ext = os.path.splitext(filename)
            unique_filename = filename
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)):
                unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            image_filename = unique_filename

        attachment_filenames = []
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                base, ext = os.path.splitext(filename)
                unique_filename = filename
                while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)):
                    unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                attachment_filenames.append(unique_filename)

        staff_id = None
        if current_user.is_authenticated and hasattr(current_user, 'id') and current_user.get_id() != 'admin':
            staff_id = current_user.id

        new_post = BlogPost(title=title, author_name=author, content=content, image_filename=image_filename, file_attachment=','.join(attachment_filenames), staff_id=staff_id)
        db.session.add(new_post)
        db.session.commit()
        flash('Blog post added!')
        return redirect(url_for('admin_blogs'))
    
    posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).all()
    staff_map = {s.id: s for s in Staff.query.all()}
    return render_template('admin_blogs.html', posts=posts, staff_map=staff_map)

@app.route('/admin/blogs/edit/<int:blog_id>', methods=['GET', 'POST'])
@admin_required
def admin_blogs_edit(blog_id):
    post = BlogPost.query.get_or_404(blog_id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.author_name = request.form['author']
        post.content = request.form['content']
        # Handle feature image update
        image = request.files.get('image')
        remove_image = request.form.get('remove_image')
        if remove_image == 'on' and post.image_filename:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image_filename))
            except OSError:
                pass
            post.image_filename = None
        if image and image.filename and allowed_file(image.filename):
            if post.image_filename:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image_filename))
                except OSError:
                    pass
            filename = secure_filename(image.filename)
            base, ext = os.path.splitext(filename)
            unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            post.image_filename = unique_filename
        # Handle file attachments (multiple)
        remove_files = request.form.getlist('remove_files')
        current_files = [fname for fname in (post.file_attachment or '').split(',') if fname]
        for fname in remove_files:
            if fname in current_files:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                except Exception:
                    pass
                current_files.remove(fname)
        files = request.files.getlist('files[]')
        for file in files:
            if file and file.filename:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    base, ext = os.path.splitext(filename)
                    unique_filename = filename
                    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)):
                        unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
                    try:
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                        current_files.append(unique_filename)
                    except Exception as e:
                        flash(f"Failed to upload {filename}: {str(e)}", 'error')
                else:
                    flash(f"File type not allowed: {file.filename}", 'error')
        post.file_attachment = ','.join(current_files)
        db.session.commit()
        flash('Blog post updated successfully!')
        return redirect(url_for('admin_blogs'))
    return render_template('admin_edit_blog.html', post=post)

@app.route('/admin/blogs/delete/<int:blog_id>', methods=['POST'])
@admin_required
def delete_blog(blog_id):
    post = BlogPost.query.get_or_404(blog_id)
    if post.image_filename:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image_filename))
        except OSError:
            pass # File doesn't exist, ignore
    if post.file_attachment:
        for fname in post.file_attachment.split(','):
            if fname:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                except Exception:
                    pass
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted!')
    return redirect(url_for('admin_blogs'))

@app.route('/blogs/<int:blog_id>')
def blog_detail(blog_id):
    post = BlogPost.query.get_or_404(blog_id)
    return render_template('blog_detail.html', post=post)

@app.cli.command("cleanup-uploads")
def cleanup_uploads():
    """Deletes files from static/uploads that are not referenced in the database."""
    UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
    referenced = set()
    # Notice attachments
    for work in Work.query.all():
        if work.file_names:
            referenced.update([fname for fname in work.file_names.split(',') if fname])
    # Blog images
    for blog in BlogPost.query.all():
        if blog.image_filename:
            referenced.add(blog.image_filename)
    all_files = set(os.listdir(UPLOAD_FOLDER))
    orphaned = all_files - referenced
    for fname in orphaned:
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, fname))
            print(f"Deleted orphaned file: {fname}")
        except Exception as e:
            print(f"Failed to delete {fname}: {e}")
    print("Cleanup complete.")

@app.route('/admin/staff', methods=['GET', 'POST'])
@admin_required
def admin_staff():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        if Staff.query.filter_by(username=username).first():
            flash(f"Username '{username}' already exists.", 'error')
        else:
            new_staff = Staff(username=username, name=name)
            new_staff.set_password(password)
            db.session.add(new_staff)
            db.session.commit()
            flash('Staff account created successfully!')
        return redirect(url_for('admin_staff'))
    staff_list = Staff.query.all()
    return render_template('admin_staff.html', staff_list=staff_list)

@app.route('/admin/staff/delete/<int:staff_id>', methods=['POST'])
@admin_required
def delete_staff(staff_id):
    staff_to_delete = Staff.query.get_or_404(staff_id)
    db.session.delete(staff_to_delete)
    db.session.commit()
    flash('Staff account deleted.')
    return redirect(url_for('admin_staff'))

@app.route('/staff/login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        staff = Staff.query.filter_by(username=username).first()
        if staff and staff.check_password(password):
            login_user(staff)
            session.permanent = True
            return redirect(url_for('staff_dashboard'))
        else:
            flash('Invalid credentials for staff', 'error')
    return render_template('staff_login.html')

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.get_id() == 'admin':
            flash('You must be logged in as staff to see this page.', 'error')
            return redirect(url_for('staff_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/staff/logout')
@staff_required
def staff_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/staff/blogs', methods=['GET', 'POST'])
@staff_required
def staff_blogs():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        content = request.form['content']
        image = request.files.get('image')
        files = request.files.getlist('files[]')
        
        image_filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            base, ext = os.path.splitext(filename)
            unique_filename = filename
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)):
                unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            image_filename = unique_filename
        
        saved_files = []
        for file in files:
            if file and file.filename:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    base, ext = os.path.splitext(filename)
                    unique_filename = filename
                    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)):
                        unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
                    try:
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                        saved_files.append(unique_filename)
                    except Exception as e:
                        flash(f"Failed to upload {filename}: {str(e)}", 'error')
                else:
                    flash(f"File type not allowed: {file.filename}", 'error')
        file_attachment = ','.join(saved_files)

        new_post = BlogPost(title=title, author_name=author, content=content, image_filename=image_filename, file_attachment=file_attachment, staff_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        flash('Blog post added!')
        return redirect(url_for('staff_blogs'))
    
    posts = BlogPost.query.filter_by(staff_id=current_user.id).order_by(BlogPost.date_posted.desc()).all()
    return render_template('staff_blogs.html', posts=posts)

@app.route('/staff/blogs/edit/<int:blog_id>', methods=['GET', 'POST'])
@staff_required
def staff_blogs_edit(blog_id):
    post = BlogPost.query.get_or_404(blog_id)
    if post.staff_id != current_user.id:
        flash("You are not authorized to edit this post.", "error")
        return redirect(url_for('staff_blogs'))

    if request.method == 'POST':
        post.title = request.form['title']
        post.author_name = request.form['author']
        post.content = request.form['content']

        # Handle feature image update
        image = request.files.get('image')
        remove_image = request.form.get('remove_image')

        if remove_image == 'on' and post.image_filename:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image_filename))
            except OSError:
                pass
            post.image_filename = None
        
        if image and image.filename and allowed_file(image.filename):
            if post.image_filename:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image_filename))
                except OSError:
                    pass
            filename = secure_filename(image.filename)
            base, ext = os.path.splitext(filename)
            unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            post.image_filename = unique_filename
        
        # Handle file attachment update
        attachment = request.files.get('attachment')
        remove_attachment = request.form.get('remove_attachment')

        if remove_attachment == 'on' and post.file_attachment:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.file_attachment))
            except OSError:
                pass
            post.file_attachment = None

        if attachment and attachment.filename and allowed_file(attachment.filename):
            if post.file_attachment:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.file_attachment))
                except OSError:
                    pass
            filename = secure_filename(attachment.filename)
            base, ext = os.path.splitext(filename)
            unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
            attachment.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            post.file_attachment = unique_filename
        
        db.session.commit()
        flash('Blog post updated successfully!')
        return redirect(url_for('staff_blogs'))

    return render_template('admin_edit_blog.html', post=post)

@app.route('/staff/blogs/delete/<int:blog_id>', methods=['POST'])
@staff_required
def staff_delete_blog(blog_id):
    post = BlogPost.query.get_or_404(blog_id)
    if post.image_filename:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image_filename))
        except OSError:
            pass # File doesn't exist, ignore
    if post.file_attachment:
        for fname in post.file_attachment.split(','):
            if fname:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                except Exception:
                    pass
    
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted!')
    return redirect(url_for('staff_blogs'))

@app.route('/admin/messages/<int:msg_id>')
@admin_required
def admin_message_detail(msg_id):
    msg = Message.query.get_or_404(msg_id)
    return render_template('admin_message_detail.html', msg=msg)

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

@app.route('/staff/work', methods=['GET', 'POST'])
@staff_required
def staff_work():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_filename = None
        image = request.files.get('image')
        if image and image.filename and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            base, ext = os.path.splitext(filename)
            unique_filename = filename
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)):
                unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
            try:
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                image_filename = unique_filename
            except Exception as e:
                flash(f"Failed to upload thumbnail: {str(e)}", 'error')
        files = request.files.getlist('files[]')
        saved_files = []
        for file in files:
            if file and file.filename:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    base, ext = os.path.splitext(filename)
                    unique_filename = filename
                    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)):
                        unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
                    try:
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                        saved_files.append(unique_filename)
                    except Exception as e:
                        flash(f"Failed to upload {filename}: {str(e)}", 'error')
                else:
                    flash(f"File type not allowed: {file.filename}", 'error')
        file_names = ','.join(saved_files)
        new_work = Work(title=title, content=content, file_names=file_names, image_filename=image_filename, staff_id=current_user.id)
        db.session.add(new_work)
        db.session.commit()
        flash('Work added!')
        return redirect(url_for('staff_work'))
    works = Work.query.order_by(Work.created_at.desc()).all()
    return render_template('admin_notice.html', works=works)

@app.route('/staff/work/edit/<int:work_id>', methods=['GET', 'POST'])
@staff_required
def staff_edit_work(work_id):
    work = Work.query.get_or_404(work_id)
    if work.staff_id != current_user.id:
        flash('You are not authorized to edit this work.', 'error')
        return redirect(url_for('staff_work'))
    if request.method == 'POST':
        work.title = request.form['title']
        work.content = request.form['content']
        image = request.files.get('image')
        remove_image = request.form.get('remove_image')
        if remove_image == 'on' and work.image_filename:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], work.image_filename))
            except OSError:
                pass
            work.image_filename = None
        if image and image.filename and allowed_file(image.filename):
            if work.image_filename:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], work.image_filename))
                except OSError:
                    pass
            filename = secure_filename(image.filename)
            base, ext = os.path.splitext(filename)
            unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            work.image_filename = unique_filename
        remove_files = request.form.getlist('remove_files')
        current_files = [fname for fname in (work.file_names or '').split(',') if fname]
        for fname in remove_files:
            if fname in current_files:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                except Exception:
                    pass
                current_files.remove(fname)
        files = request.files.getlist('files[]')
        for file in files:
            if file and file.filename:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    base, ext = os.path.splitext(filename)
                    unique_filename = filename
                    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)):
                        unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
                    try:
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                        current_files.append(unique_filename)
                    except Exception as e:
                        flash(f"Failed to upload {filename}: {str(e)}", 'error')
                else:
                    flash(f"File type not allowed: {file.filename}", 'error')
        work.file_names = ','.join(current_files)
        db.session.commit()
        flash('Work updated successfully!')
        return redirect(url_for('staff_work'))
    return render_template('admin_edit_notice.html', work=work)

@app.route('/staff/work/delete/<int:work_id>', methods=['POST'])
@staff_required
def staff_delete_work(work_id):
    work = Work.query.get_or_404(work_id)
    if work.staff_id != current_user.id:
        flash('You are not authorized to delete this work.', 'error')
        return redirect(url_for('staff_work'))
    if work.file_names:
        for fname in work.file_names.split(','):
            if fname:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                except Exception:
                    pass
    if work.image_filename:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], work.image_filename))
        except Exception:
            pass
    db.session.delete(work)
    db.session.commit()
    flash('Work deleted!')
    return redirect(url_for('staff_work'))

@app.route('/staff/dashboard')
@staff_required
def staff_dashboard():
    works = Work.query.filter_by(staff_id=current_user.id).order_by(Work.created_at.desc()).all()
    blogs = BlogPost.query.filter_by(staff_id=current_user.id).order_by(BlogPost.date_posted.desc()).all()
    return render_template('staff_dashboard.html', works=works, blogs=blogs)

@app.route('/donate')
def donate():
    return render_template('donate.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)