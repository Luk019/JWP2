from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Post, Comment, Like, User

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)


@main.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        content = request.form['content']
        comment = Comment(content=content, post_id=post.id, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('main.post', post_id=post.id))
    return render_template('post.html', post=post)


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
                print(f"Deleted like for post_id: {entity_id}")
                return redirect(url_for('main.index'))
            else:
                print(f"Deleted like for comment_id: {entity_id}")
                return redirect(url_for('main.post', post_id=entity.post_id))
    else:
        new_like = Like(
            post_id=(entity_id if entity_type == 'post' else None),
            comment_id=(entity_id if entity_type == 'comment' else None),
            user_id=current_user.id,
            upvote=(action == 'upvote')
        )
        db.session.add(new_like)
        print(
            f"Added new like: post_id={new_like.post_id}, comment_id={new_like.comment_id}, user_id={new_like.user_id}, upvote={new_like.upvote}")

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
            login_user(user)
            return redirect(url_for('main.index'))
        else:
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
    if post.user_id != current_user.id:
        flash('You are not authorized to edit this post.')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('Post updated successfully.')
        return redirect(url_for('main.post', post_id=post.id))
    return render_template('edit_post.html', post=post)


# Widok usunięcia postu
@main.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('You are not authorized to delete this post.')
        return redirect(url_for('main.index'))
    # Usuwanie wszystkich komentarzy i łapek związanych z postem
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
    if comment.user_id != current_user.id:
        flash('You are not authorized to edit this comment.')
        return redirect(url_for('main.post', post_id=comment.post_id))
    if request.method == 'POST':
        comment.content = request.form['content']
        db.session.commit()
        flash('Comment updated successfully.')
        return redirect(url_for('main.post', post_id=comment.post_id))
    return render_template('edit_comment.html', comment=comment)


# Widok usunięcia komentarza
@main.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        flash('You are not authorized to delete this comment.')
        return redirect(url_for('main.post', post_id=comment.post_id))
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully.')
    return redirect(url_for('main.post', post_id=comment.post_id))
