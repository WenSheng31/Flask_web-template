from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.services import PostService, CommentService, LikeService


post_bp = Blueprint('post', __name__, url_prefix='/posts')


@post_bp.route('/')
def index():
    """文章列表"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q')

    if search_query:
        pagination = PostService.search_posts(search_query, page=page)
    else:
        pagination = PostService.get_posts_page(page=page)

    return render_template('posts/index.html',
                           title='文章列表',
                           posts=pagination,
                           search_query=search_query)


@post_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """創建文章"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        post, error = PostService.create_post(
            user_id=current_user.id,
            title=title,
            content=content
        )

        if error:
            flash(error, 'danger')
            return redirect(url_for('post.create'))

        flash('文章發布成功！', 'success')
        return redirect(url_for('post.show', id=post.id))

    return render_template('posts/create.html', title='發布文章')


@post_bp.route('/<int:id>')
def show(id):
    """顯示文章詳情"""
    post = PostService.get_post_by_id(id)
    if not post:
        flash('文章不存在', 'danger')
        return redirect(url_for('post.index'))

    return render_template('posts/show.html',
                           title=post.title,
                           post=post)


@post_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """編輯文章"""
    post = PostService.get_post_by_id(id)
    if not post or post.user_id != current_user.id:
        flash('無權限編輯此文章', 'danger')
        return redirect(url_for('post.index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        success, error = PostService.update_post(
            post_id=id,
            title=title,
            content=content
        )

        if not success:
            flash(error, 'danger')
            return redirect(url_for('post.edit', id=id))

        flash('文章已更新', 'success')
        return redirect(url_for('post.show', id=id))

    return render_template('posts/edit.html',
                           title='編輯文章',
                           post=post)


@post_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """刪除文章"""
    post = PostService.get_post_by_id(id)
    if not post or post.user_id != current_user.id:
        flash('無權限刪除此文章', 'danger')
        return redirect(url_for('post.index'))

    success, error = PostService.delete_post(id)
    if not success:
        flash(error, 'danger')
        return redirect(url_for('post.show', id=id))

    flash('文章已刪除', 'success')
    return redirect(url_for('post.index'))


@post_bp.route('/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    """切換按讚狀態"""
    success, is_liked, count = LikeService.toggle_like(
        user_id=current_user.id,
        post_id=post_id
    )

    if success:
        return jsonify({
            'success': True,
            'liked': is_liked,
            'count': count
        })
    return jsonify({'success': False, 'message': '操作失敗'}), 500


@post_bp.route('/<int:post_id>/comments', methods=['POST'])
@login_required
def create_comment(post_id):
    """創建留言"""
    content = request.form.get('content', '').strip()
    parent_id = request.form.get('parent_id', type=int)

    success, error = CommentService.create_comment(
        user_id=current_user.id,
        post_id=post_id,
        content=content,
        parent_id=parent_id
    )

    if success:
        flash('留言成功', 'success')
    else:
        flash(f'留言失敗: {error}', 'danger')

    return redirect(url_for('post.show', id=post_id))


@post_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """刪除留言"""
    comment = CommentService.get_comment_by_id(comment_id)
    if not comment:
        return jsonify({'success': False, 'message': '留言不存在'}), 404

    if comment.user_id != current_user.id:
        return jsonify({'success': False, 'message': '無權限刪除此留言'}), 403

    success, error = CommentService.delete_comment(comment_id)
    if success:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': error}), 500
