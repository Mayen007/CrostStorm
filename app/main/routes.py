from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_babel import _, get_locale
from flask_login import current_user, login_required, logout_user
from langdetect import detect, LangDetectException

from app import db
from app.auth import user_bp
# from app.main import bp
from app.main.forms import EditProfileForm, EmptyForm, PostForm, MessageForm, ReplyForm
from app.main.forms import SearchForm
from app.models import User, Post, Message, Notification
from app.translate import translate


@user_bp.route('/', methods=['GET', 'POST'])
@user_bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ''
        post = Post(body=form.post.data, author=current_user,
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('user_bp.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    next_url = url_for('user_bp.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user_bp.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', user=current_user, title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@user_bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@user_bp.route('/user/<username>')
@login_required
def user(username):
    form = EmptyForm()
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('user_bp.user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', user=current_user, title=_('Edit Profile'),
                           form=form)


@user_bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('user_bp.index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('user_bp.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are now following %(username)s!', username=username))
        return redirect(url_for('user_bp.user', username=username))
    else:
        return redirect(url_for('user_bp.index'))


@user_bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('user_bp.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('user_bp.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You have unfollowed %(username)s.', username=username))
        return redirect(url_for('user_bp.user', username=username))
    else:
        return redirect(url_for('user_bp.index'))


@user_bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})


@user_bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('user_bp.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('user_bp.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('user_bp.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), user=current_user, posts=posts,
                           next_url=next_url, prev_url=prev_url)


@user_bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@user_bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash(_('Your message has been sent.'))
        return redirect(url_for('user_bp.user', username=recipient))
    return render_template('send_message.html', title=_('Send Message'),
                           form=form, recipient=recipient, user=current_user)


@user_bp.route('/check_account', methods=['GET'])
@login_required
def check_account():
    # Get the expected user or identify it in your system
    expected_user = get_expected_user()  # This function should get the expected user

    if current_user != expected_user:
        # User is signed in but not as the expected user
        return render_template('check_account.html', expected_user=expected_user)

    # If the current user matches the expected user, proceed to the next page
    return redirect(url_for('next_page'))


@user_bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'],
            error_out=False)
    next_url = url_for('user_bp.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('user_bp.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)


# handling user re-login
@user_bp.route('/relogin', methods=['POST'])
@login_required
def relogin():
    logout_user()  # Log out the current user
    return redirect(url_for('user_bp.login'))  # Redirect the user to the login page


@user_bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    return render_template('user_popup.html', user=user, form=form)


@user_bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])


@user_bp.route('/reply_message/<int:message_id>', methods=['GET', 'POST'])
@login_required
def reply_message(message_id):
    message = Message.query.get_or_404(message_id)
    form = ReplyForm()

    if form.validate_on_submit():
        reply = Message(author=current_user, recipient=message.author,
                        body=form.reply_content.data, parent_message=message)
        db.session.add(reply)
        db.session.commit()
        flash('Your reply has been sent.')
        return redirect(url_for('user_bp.messages'))

    return render_template('reply.html', title='Reply', form=form, original_message=message)