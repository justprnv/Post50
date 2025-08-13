import os
import re
import secrets
import datetime as dt
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER_AVATARS = BASE_DIR / 'static' / 'uploads' / 'avatars'
UPLOAD_FOLDER_POSTS = BASE_DIR / 'static' / 'uploads' / 'posts'

os.makedirs(UPLOAD_FOLDER_AVATARS, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_POSTS, exist_ok=True)


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-' + secrets.token_hex(16))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(BASE_DIR / 'post50.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB uploads

    app.config['UPLOAD_FOLDER_AVATARS'] = str(UPLOAD_FOLDER_AVATARS)
    app.config['UPLOAD_FOLDER_POSTS'] = str(UPLOAD_FOLDER_POSTS)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar_path = db.Column(db.String(255))
    theme_preference = db.Column(db.String(10), default='system')  # 'light', 'dark', 'system'
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    votes = db.relationship('Vote', backref='voter', lazy=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


post_tags = db.Table(
    'post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # HTML content from rich editor
    image_path = db.Column(db.String(255))  # optional featured image
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    tags = db.relationship('Tag', secondary=post_tags, lazy='subquery', backref=db.backref('posts', lazy=True))
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='post', lazy=True, cascade='all, delete-orphan')

    @property
    def score(self) -> int:
        return sum(v.value for v in self.votes) if self.votes else 0


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)  # +1 or -1

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_vote'),)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Helpers
HASHTAG_REGEX = re.compile(r"(?<!&)#(\w+)")
ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}


def extract_hashtags(text: str) -> set[str]:
    if not text:
        return set()
    return {m.group(1).lower() for m in HASHTAG_REGEX.finditer(text)}


def save_image(file_storage, dest_dir: Path, resize_max: int | None = 1600) -> str:
    filename = secure_filename(file_storage.filename)
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError('Unsupported image type')
    random_prefix = secrets.token_hex(8)
    filename = f"{random_prefix}_{filename}"
    filepath = dest_dir / filename
    image = Image.open(file_storage.stream)
    image = image.convert('RGB') if image.mode in ('P', 'RGBA') else image
    if resize_max:
        image.thumbnail((resize_max, resize_max))
    image.save(filepath)
    return f"/static/uploads/{'avatars' if dest_dir == UPLOAD_FOLDER_AVATARS else 'posts'}/{filename}"


# Routes

def register_routes(app: Flask):
    @app.route('/')
    def index():
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        q = request.args.get('q', '').strip()

        query = Post.query
        if q:
            like = f"%{q}%"
            query = query.join(User, Post.author).outerjoin(post_tags).outerjoin(Tag)
            query = query.filter(
                db.or_(
                    Post.title.ilike(like),
                    Post.content.ilike(like),
                    User.username.ilike(like),
                    Tag.name.ilike(like),
                )
            )
            query = query.distinct()

        posts = query.all()
        posts.sort(key=lambda p: (p.score, p.created_at), reverse=True)

        start = (page - 1) * per_page
        end = start + per_page
        page_posts = posts[start:end]
        
        # Calculate vote counts for each post
        for post in page_posts:
            post.upvotes = Vote.query.filter_by(post_id=post.id, value=1).count()
            post.downvotes = Vote.query.filter_by(post_id=post.id, value=-1).count()

        return render_template('index.html', posts=page_posts)

    @app.route('/api/posts')
    def api_posts():
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        q = request.args.get('q', '').strip()

        query = Post.query
        if q:
            like = f"%{q}%"
            query = query.join(User, Post.author).outerjoin(post_tags).outerjoin(Tag)
            query = query.filter(
                db.or_(
                    Post.title.ilike(like),
                    Post.content.ilike(like),
                    User.username.ilike(like),
                    Tag.name.ilike(like),
                )
            )
            query = query.distinct()

        posts = query.all()
        posts.sort(key=lambda p: (p.score, p.created_at), reverse=True)

        start = (page - 1) * per_page
        end = start + per_page
        page_items = posts[start:end]

        def serialize_post(p: Post):
            return {
                'id': p.id,
                'title': p.title,
                'content': p.content,
                'image_url': p.image_path,
                'author': p.author.username,
                'author_id': p.author.id,
                'tags': [t.name for t in p.tags],
                'created_at': p.created_at.isoformat() + 'Z',
                'updated_at': p.updated_at.isoformat() + 'Z',
                'score': p.score,
                'can_edit': current_user.is_authenticated and current_user.id == p.author_id,
            }

        return jsonify({
            'items': [serialize_post(p) for p in page_items],
            'has_more': end < len(posts),
        })

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            data = request.form
            username = data.get('username', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')

            # Server-side validations
            errors = {}
            if not re.fullmatch(r'[A-Za-z0-9_]{3,20}', username or ''):
                errors['username'] = '3-20 chars, letters/numbers/underscore'
            if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email or ''):
                errors['email'] = 'Invalid email'
            if len(password) < 6:
                errors['password'] = 'At least 6 characters'
            if User.query.filter_by(username=username).first():
                errors['username'] = 'Username already taken'
            if User.query.filter_by(email=email).first():
                errors['email'] = 'Email already registered'
            if errors:
                for k, v in errors.items():
                    flash(f"{k}: {v}", 'error')
                return render_template('register.html', form=data), 400

            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        return render_template('register.html')

    @app.get('/api/check_username')
    def check_username():
        username = request.args.get('username', '').strip()
        valid = bool(re.fullmatch(r'[A-Za-z0-9_]{3,20}', username))
        available = valid and not User.query.filter_by(username=username).first()
        return jsonify({'valid': valid, 'available': available})

    @app.get('/api/check_email')
    def check_email():
        email = request.args.get('email', '').strip().lower()
        valid = bool(re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email))
        available = valid and not User.query.filter_by(email=email).first()
        return jsonify({'valid': valid, 'available': available})

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username_or_email = request.form.get('username_or_email', '').strip()
            password = request.form.get('password', '')
            user = User.query.filter(
                db.or_(User.username == username_or_email, User.email == username_or_email.lower())
            ).first()
            if not user or not user.check_password(password):
                flash('Invalid credentials', 'error')
                return render_template('login.html'), 401
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html')

    @app.get('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/post/new', methods=['GET', 'POST'])
    @login_required
    def post_new():
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            tags_input = request.form.get('tags', '').strip()
            image = request.files.get('image')

            if not title or not content:
                flash('Title and content are required', 'error')
                return render_template('post_form.html', mode='new')

            image_url = None
            if image and image.filename:
                try:
                    image_url = save_image(image, UPLOAD_FOLDER_POSTS)
                except Exception as e:
                    flash(str(e), 'error')

            post = Post(title=title, content=content, image_path=image_url, author_id=current_user.id)

            # Process tags - remove # symbols and avoid duplicates
            tags = set()
            if tags_input:
                # Clean manually entered tags (remove # symbols and whitespace)
                manual_tags = set(filter(None, [t.strip().lower().lstrip('#') for t in tags_input.split(',')]))
                tags.update(manual_tags)
            
            # Extract hashtags from title and content (without # symbols)
            title_hashtags = extract_hashtags(title)
            content_hashtags = extract_hashtags(content)
            tags.update(title_hashtags)
            tags.update(content_hashtags)
            
            # Create or find existing tags
            for name in tags:
                if name:  # Ensure name is not empty
                    existing = Tag.query.filter_by(name=name).first()
                    if not existing:
                        existing = Tag(name=name)
                        db.session.add(existing)
                    post.tags.append(existing)

            db.session.add(post)
            db.session.commit()
            flash('Post created', 'success')
            return redirect(url_for('index'))
        return render_template('post_form.html', mode='new')

    @app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
    @login_required
    def post_edit(post_id: int):
        post = Post.query.get_or_404(post_id)
        if post.author_id != current_user.id:
            abort(403)
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            tags_input = request.form.get('tags', '').strip()
            image = request.files.get('image')

            if not title or not content:
                flash('Title and content are required', 'error')
                return render_template('post_form.html', mode='edit', post=post)

            if image and image.filename:
                try:
                    post.image_path = save_image(image, UPLOAD_FOLDER_POSTS)
                except Exception as e:
                    flash(str(e), 'error')

            post.title = title
            post.content = content

            # Update tags
            post.tags.clear()
            # Process tags - remove # symbols and avoid duplicates
            tags = set()
            if tags_input:
                # Clean manually entered tags (remove # symbols and whitespace)
                manual_tags = set(filter(None, [t.strip().lower().lstrip('#') for t in tags_input.split(',')]))
                tags.update(manual_tags)
            
            # Extract hashtags from title and content (without # symbols)
            title_hashtags = extract_hashtags(title)
            content_hashtags = extract_hashtags(content)
            tags.update(title_hashtags)
            tags.update(content_hashtags)
            
            # Create or find existing tags
            for name in tags:
                if name:  # Ensure name is not empty
                    existing = Tag.query.filter_by(name=name).first()
                    if not existing:
                        existing = Tag(name=name)
                        db.session.add(existing)
                    post.tags.append(existing)

            db.session.commit()
            flash('Post updated', 'success')
            return redirect(url_for('index'))
        return render_template('post_form.html', mode='edit', post=post)

    @app.post('/post/<int:post_id>/delete')
    @login_required
    def post_delete(post_id: int):
        post = Post.query.get_or_404(post_id)
        if post.author_id != current_user.id:
            abort(403)
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted', 'success')
        return redirect(url_for('index'))

    @app.post('/post/<int:post_id>/vote')
    @login_required
    def post_vote(post_id: int):
        post = Post.query.get_or_404(post_id)
        
        # Handle both form data and JSON
        if request.is_json:
            data = request.get_json()
            vote_type = data.get('vote_type')
            value = 1 if vote_type == 'up' else -1 if vote_type == 'down' else 0
        else:
            try:
                value = int(request.form.get('value'))
                if value not in (1, -1):
                    raise ValueError
            except Exception:
                return jsonify({'error': 'Invalid vote value'}), 400

        vote = Vote.query.filter_by(user_id=current_user.id, post_id=post.id).first()
        if vote and vote.value == value:
            # toggle off
            db.session.delete(vote)
        else:
            if not vote:
                vote = Vote(user_id=current_user.id, post_id=post.id, value=value)
                db.session.add(vote)
            else:
                vote.value = value
        db.session.commit()
        
        # Return updated vote counts
        upvotes = Vote.query.filter_by(post_id=post.id, value=1).count()
        downvotes = Vote.query.filter_by(post_id=post.id, value=-1).count()
        return jsonify({'upvotes': upvotes, 'downvotes': downvotes})

    @app.post('/post/comment')
    @login_required
    def post_comment_api():
        data = request.get_json()
        post_id = data.get('post_id')
        content = data.get('content', '').strip()
        
        if not post_id or not content:
            return jsonify({'error': 'Missing post_id or content'}), 400
            
        post = Post.query.get_or_404(post_id)
        comment = Comment(content=content, author_id=current_user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        return jsonify({'id': comment.id, 'content': comment.content, 'author': current_user.username, 'created_at': comment.created_at.isoformat() + 'Z'})

    @app.post('/post/<int:post_id>/comment')
    @login_required
    def post_comment(post_id: int):
        post = Post.query.get_or_404(post_id)
        content = request.form.get('content', '').strip()
        if not content:
            return jsonify({'error': 'Empty comment'}), 400
        comment = Comment(content=content, author_id=current_user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        return jsonify({'id': comment.id, 'content': comment.content, 'author': current_user.username, 'created_at': comment.created_at.isoformat() + 'Z'})

    @app.post('/upload/image')
    @login_required
    def upload_image():
        image = request.files.get('image')
        if not image or not image.filename:
            return jsonify({'error': 'No image provided'}), 400
        try:
            url = save_image(image, UPLOAD_FOLDER_POSTS)
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        return jsonify({'url': url})

    @app.route('/settings', methods=['GET', 'POST'])
    @login_required
    def settings():
        if request.method == 'POST':
            avatar = request.files.get('avatar')
            theme = request.form.get('theme')
            if avatar and avatar.filename:
                try:
                    url = save_image(avatar, UPLOAD_FOLDER_AVATARS, resize_max=512)
                    current_user.avatar_path = url
                except Exception as e:
                    flash(str(e), 'error')
            if theme in ('light', 'dark', 'system'):
                current_user.theme_preference = theme
            db.session.commit()
            flash('Settings updated', 'success')
            return redirect(url_for('settings'))
        return render_template('settings.html')

    @app.get('/api/user/theme')
    @login_required
    def get_user_theme():
        return jsonify({'theme': current_user.theme_preference})

    @app.get('/u/<int:user_id>')
    def profile(user_id: int):
        try:
            user = User.query.get_or_404(user_id)
            posts = Post.query.filter_by(author_id=user.id).order_by(Post.created_at.desc()).limit(20).all()
            
            # Calculate vote counts for each post
            for post in posts:
                post.upvotes = Vote.query.filter_by(post_id=post.id, value=1).count()
                post.downvotes = Vote.query.filter_by(post_id=post.id, value=-1).count()
                
            return render_template('profile.html', user=user, posts=posts)
        except Exception as e:
            # Log the error for debugging
            print(f"Error in profile route: {e}")
            flash('Error loading profile', 'error')
            return redirect(url_for('index'))


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
