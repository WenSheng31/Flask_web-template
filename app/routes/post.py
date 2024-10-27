from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.post import Post


post_bp = Blueprint('post', __name__, url_prefix='/posts')


@post_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('posts/index.html', title='文章列表', posts=posts)


@post_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title or not content:
            flash('標題和內容不能為空', 'danger')
            return redirect(url_for('post.create'))

        post = Post(title=title, content=content, author=current_user)
        db.session.add(post)
        try:
            db.session.commit()
            flash('文章發布成功！', 'success')
            return redirect(url_for('post.show', id=post.id))
        except Exception as e:
            db.session.rollback()
            flash('文章發布失敗', 'danger')

    return render_template('posts/create.html', title='發布文章')


@post_bp.route('/<int:id>')
def show(id):
    post = Post.query.get_or_404(id)
    return render_template('posts/show.html', title=post.title, post=post)


@post_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        flash('你沒有權限編輯這篇文章', 'danger')
        return redirect(url_for('post.show', id=id))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title or not content:
            flash('標題和內容不能為空', 'danger')
            return redirect(url_for('post.edit', id=id))

        post.title = title
        post.content = content
        try:
            db.session.commit()
            flash('文章更新成功！', 'success')
            return redirect(url_for('post.show', id=id))
        except Exception as e:
            db.session.rollback()
            flash('文章更新失敗', 'danger')

    return render_template('posts/edit.html', title='編輯文章', post=post)


@post_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        flash('你沒有權限刪除這篇文章', 'danger')
        return redirect(url_for('post.show', id=id))

    try:
        db.session.delete(post)
        db.session.commit()
        flash('文章已刪除', 'success')
        return redirect(url_for('post.index'))
    except Exception as e:
        db.session.rollback()
        flash('刪除失敗', 'danger')
        return redirect(url_for('post.show', id=id))
