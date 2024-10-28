# 第三方套件導入
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.comment import Comment

# 本地應用導入
from app import db
from app.models.post import Post

# 常數配置
POSTS_PER_PAGE = 10

# 創建文章藍圖
post_bp = Blueprint('post', __name__, url_prefix='/posts')


# 工具函數
def validate_post_data(title, content):
    """
    驗證文章數據
    :param title: 文章標題
    :param content: 文章內容
    :return: tuple(bool, str) 驗證結果和錯誤訊息
    """
    if not title or not title.strip():
        return False, '標題不能為空'
    if not content or not content.strip():
        return False, '內容不能為空'
    return True, None


def check_post_permission(post, user):
    """
    檢查用戶是否有權限操作文章
    :param post: 文章實例
    :param user: 用戶實例
    :return: bool 是否有權限
    """
    return post.author == user


def handle_db_operation(operation):
    """
    處理資料庫操作的裝飾器
    :param operation: 操作名稱
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                db.session.commit()
                flash(f'文章{operation}成功！', 'success')
                return result
            except Exception as e:
                db.session.rollback()
                flash(f'文章{operation}失敗: {str(e)}', 'danger')
                return redirect(url_for('post.index'))

        return wrapper

    return decorator


# 視圖函數
@post_bp.route('/')
def index():
    """文章列表頁"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=POSTS_PER_PAGE,
        error_out=False
    )
    return render_template('posts/index.html',
                           title='文章列表',
                           posts=posts)


@post_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """創建文章"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        # 驗證輸入
        if not title:
            flash('標題不能為空', 'danger')
            return redirect(url_for('post.create'))
        if not content:
            flash('內容不能為空', 'danger')
            return redirect(url_for('post.create'))

        try:
            # 創建文章
            post = Post(title=title, content=content, author=current_user)
            db.session.add(post)
            db.session.commit()  # 先提交以獲取 post.id

            flash('文章發布成功！', 'success')
            return redirect(url_for('post.show', id=post.id))
        except Exception as e:
            db.session.rollback()
            flash(f'文章發布失敗: {str(e)}', 'danger')
            return redirect(url_for('post.create'))

    return render_template('posts/create.html', title='發布文章')


@post_bp.route('/<int:id>')
def show(id):
    """顯示文章詳情"""
    post = Post.query.get_or_404(id)
    return render_template('posts/show.html',
                           title=post.title,
                           post=post)


@post_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """編輯文章"""
    post = Post.query.get_or_404(id)

    # 檢查權限
    if not check_post_permission(post, current_user):
        flash('你沒有權限編輯這篇文章', 'danger')
        return redirect(url_for('post.show', id=id))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        # 驗證輸入
        is_valid, error_message = validate_post_data(title, content)
        if not is_valid:
            flash(error_message, 'danger')
            return redirect(url_for('post.edit', id=id))

        # 更新文章
        @handle_db_operation('更新')
        def update_post():
            post.title = title
            post.content = content
            return redirect(url_for('post.show', id=id))

        return update_post()

    return render_template('posts/edit.html',
                           title='編輯文章',
                           post=post)


@post_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """刪除文章"""
    post = Post.query.get_or_404(id)

    # 檢查權限
    if not check_post_permission(post, current_user):
        flash('你沒有權限刪除這篇文章', 'danger')
        return redirect(url_for('post.show', id=id))

    # 刪除文章
    @handle_db_operation('刪除')
    def delete_post():
        db.session.delete(post)
        return redirect(url_for('post.index'))

    return delete_post()


@post_bp.route('/<int:post_id>/comments', methods=['POST'])
@login_required
def create_comment(post_id):
    """創建留言"""
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content', '').strip()
    parent_id = request.form.get('parent_id', type=int)

    if not content:
        flash('留言內容不能為空', 'danger')
        return redirect(url_for('post.show', id=post_id))

    comment = Comment(
        content=content,
        author=current_user,
        post=post,
        parent_id=parent_id
    )

    try:
        db.session.add(comment)
        db.session.commit()
        flash('留言成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('留言失敗', 'danger')

    return redirect(url_for('post.show', id=post_id))


@post_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """刪除留言"""
    comment = Comment.query.get_or_404(comment_id)

    if comment.author != current_user:
        return jsonify({'success': False, 'message': '無權限刪除此留言'}), 403

    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '刪除失敗'}), 500


@post_bp.route('/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    """切換按讚狀態"""
    post = Post.query.get_or_404(post_id)

    try:
        if current_user.is_liking(post):
            current_user.unlike_post(post)
            db.session.commit()
            return jsonify({
                'success': True,
                'liked': False,
                'count': post.like_count
            })
        else:
            current_user.like_post(post)
            db.session.commit()
            return jsonify({
                'success': True,
                'liked': True,
                'count': post.like_count
            })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失敗'}), 500
