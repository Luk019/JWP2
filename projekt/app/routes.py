from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Post, Comment, Like, User

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)


@main.route('/')
def index():
    posts = Post.query.all()
    user_likes = {like.post_id: like for like in Like.query.filter_by(user_id=current_user.id).all()} if current_user.is_authenticated else {}
    return render_template('index.html', posts=posts, user_likes=user_likes)


@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        content = request.form['content']
        comment = Comment(content=content, post_id=post.id, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('main.post', post_id=post.id))
    user_likes = {like.comment_id: like for like in Like.query.filter_by(user_id=current_user.id).all()} if current_user.is_authenticated else {}
    return render_template('post.html', post=post, user_likes=user_likes)


@main.route('/like/<int:entity_id>/<entity_type>/<action>')
@login_required
def like_action(entity_id, entity_type, action):
    like = None
    if entity_type == 'post':
        entity = Post.query.get_or_404(entity_id)
        like = Like.query.filter_by(user_id=current_user.id, post_id=entity_id).first()
    elif entity_type == 'comment':
        entity = Comment.query.get_or_404(entity_id)
        like = Like.query.filter_by(user_id=current_user.id, comment_id=entity_id).first()

    if like:
        if action == 'upvote' and not like.upvote:
            like.upvote = True
        elif action == 'downvote' and like.upvote:
            like.upvote = False
        else:
            db.session.delete(like)
            db.session.commit()
            if entity_type == 'post':
                return redirect(url_for('main.index'))
            else:
                return redirect(url_for('main.post', post_id=entity.post_id))
    else:
        new_like = Like(
            post_id=(entity_id if entity_type == 'post' else None),
            comment_id=(entity_id if entity_type == 'comment' else None),
            user_id=current_user.id,
            upvote=(action == 'upvote')
        )
        db.session.add(new_like)

    db.session.commit()
    if entity_type == 'post':
        print(f"Redirecting to index after like for post_id: {entity_id}")
        return redirect(url_for('main.index'))
    else:
        print(f"Redirecting to post after like for comment_id: {entity_id}")
        return redirect(url_for('main.post', post_id=entity.post_id))


@main.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = Post(title=title, content=content, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('add_post.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.is_blocked:
                flash('Your account is blocked. Contact the admin.')
                return redirect(url_for('auth.login'))
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid email or password')
    return render_template('login.html')



@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# Widok edycji postu
@main.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to edit this post.')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('Post updated successfully.')
        return redirect(url_for('main.post', post_id=post.id))
    return render_template('edit_post.html', post=post)


@main.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to delete this post.')
        return redirect(url_for('main.index'))
    for comment in post.comments:
        for like in comment.likes:
            db.session.delete(like)
        db.session.delete(comment)
    for like in post.likes:
        db.session.delete(like)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully.')
    return redirect(url_for('main.index'))


# Widok edycji komentarza
@main.route('/edit_comment/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to edit this comment.')
        return redirect(url_for('main.post', post_id=comment.post_id))
    if request.method == 'POST':
        comment.content = request.form['content']
        db.session.commit()
        flash('Comment updated successfully.')
        return redirect(url_for('main.post', post_id=comment.post_id))
    return render_template('edit_comment.html', comment=comment)


@main.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to delete this comment.')
        return redirect(url_for('main.post', post_id=comment.post_id))
    for like in comment.likes:
        db.session.delete(like)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully.')
    return redirect(url_for('main.post', post_id=comment.post_id))


@main.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You are not authorized to access this page.')
        return redirect(url_for('main.index'))
    users = User.query.all()
    posts = Post.query.all()
    return render_template('admin_dashboard.html', users=users, posts=posts)


@main.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('You are not authorized to access this page.')
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.is_admin = 'is_admin' in request.form
        db.session.commit()
        flash('User updated successfully.')
        return redirect(url_for('main.admin_dashboard'))
    return render_template('edit_user.html', user=user)


@main.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('You are not authorized to delete this user.')
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)

    # Usuwanie postów i powiązanych komentarzy oraz łapek
    for post in user.posts:
        for comment in post.comments:
            for like in comment.likes:
                db.session.delete(like)
            db.session.delete(comment)
        for like in post.likes:
            db.session.delete(like)
        db.session.delete(post)

    # Usuwanie komentarzy bezpośrednio powiązanych z użytkownikiem
    for comment in user.comments:
        for like in comment.likes:
            db.session.delete(like)
        db.session.delete(comment)

    db.session.delete(user)
    db.session.commit()
    flash('User and all associated posts and comments have been deleted successfully.')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/block_user/<int:user_id>', methods=['POST'])
@login_required
def block_user(user_id):
    if not current_user.is_admin:
        flash('You are not authorized to block this user.')
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)

    # Ukrywanie postów i komentarzy użytkownika
    db.session.query(Post).filter_by(user_id=user.id).update({"is_hidden": True})
    db.session.query(Comment).filter_by(user_id=user.id).update({"is_hidden": True})

    user.is_blocked = True  # Ustawienie atrybutu `is_blocked`
    db.session.commit()
    flash('User blocked and their posts/comments have been hidden.')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/unblock_user/<int:user_id>', methods=['POST'])
@login_required
def unblock_user(user_id):
    if not current_user.is_admin:
        flash('You are not authorized to unblock this user.')
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)

    # Odkrywanie postów i komentarzy użytkownika
    db.session.query(Post).filter_by(user_id=user.id).update({"is_hidden": False})
    db.session.query(Comment).filter_by(user_id=user.id).update({"is_hidden": False})

    user.is_blocked = False  # Ustawienie atrybutu `is_blocked` na False
    db.session.commit()
    flash('User unblocked and their posts/comments have been unhidden.')
    return redirect(url_for('main.admin_dashboard'))
