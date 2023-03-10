import requests
from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from blog import app, db, login_manager
from blog.forms import UserForm, PostForm, LoginForm, SearchForm, CommentForm, FormChangePWD, EmailForm, \
    ResetPWForm, FormResetPWD, ContactForm, ProjectForm
from blog.models import Users, Posts, Comments, Projects

import os
import uuid as uuid
from PIL import Image

from blog.sendmail import send_mail


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    form = ContactForm()
    if form.validate_on_submit():
        user_email = form.email.data
        user_name = form.name.data
        user_message = form.message.data
        send_mail(sender=user_email,
                  recipients=["andy0427s@gmail.com"],
                  subject='Notice from website visitors',
                  template='contact_mail',
                  mailtype='html',
                  username=user_name,
                  message=user_message,
                  email=user_email)
        flash("Thank you for contacting us!", category="success")
        form.email.data = ""
        form.name.data = ""
        form.message.data = ""

    projects = Projects.query.order_by(Projects.date_created.desc())
    return render_template("index.html", form=form, projects=projects)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("404.html"), 500


@app.route('/user/add', methods=['GET', 'POST'])
def register():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, username=form.username.data, email=form.email.data,
                         password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()

            # Token generation
            token = user.create_token()

            # Email sending
            user_email = form.email.data
            send_mail(sender='andy0427s@gmail.com',
                      recipients=[user_email],
                      subject='Activate your account',
                      template='welcome',
                      mailtype='html',
                      user=user,
                      token=token)

        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        flash("Check Your Email and Activate Your Account!", category="success")

    return render_template("register.html",
                           name=name,
                           form=form)


@app.route('/user/add/verification', methods=['GET', 'POST'])
def resend_verification():
    form = EmailForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            token = user.create_token()
            user_email = form.email.data
            send_mail(sender='andy0427s@gmail.com',
                      recipients=[user_email],
                      subject='Activate your account',
                      template='welcome',
                      mailtype='html',
                      user=user,
                      token=token)
            form.email.data = ''
            flash("Check Your Email and Activate Your Account!", category="success")
        else:
            form.email.data = ''
            flash("Not found the valid account, please register your account first!", category="warning")
        return redirect(url_for("register"))
    return render_template("resend_email.html", form=form)


@app.route('/user_confirm/<token>')
def user_confirm(token):
    user = Users()
    user_id = user.confirm_token(token)
    if user_id:
        user = Users.query.filter_by(id=user_id).first()
        user.confirm = True
        db.session.add(user)
        db.session.commit()
        flash('Thank for your activation, you can log in now!', category='success')
        return redirect(url_for('login'))
    else:
        flash('Wrong Token, please send the registration mail again!', category='danger')
        return redirect(url_for('register'))


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']

        if request.files['profile_pic']:
            output_size = (512, 512)
            name_to_update.profile_pic = request.files['profile_pic']
            # Generate a unique/secure filename
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            # pic_name = str(uuid.uuid1()) + "_" + pic_filename
            with Image.open(name_to_update.profile_pic.stream) as i:
                i.thumbnail(output_size)
                i.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_filename))

            # Save the profile img to the static directory
            # basedir = os.path.abspath(os.path.dirname(__file__))

            # i.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            # Save secured filename in db
            name_to_update.profile_pic = pic_filename
            try:
                db.session.commit()
                flash("User Updated Successfully", category="success")
                return redirect(url_for('dashboard'))
                # return render_template("update.html",
                #                        form=form,
                #                        name_to_update=name_to_update,
                #                        id=id)
            except:
                flash("Error! Looks like there was a problem...try again!", category="danger")
                return render_template("update.html",
                                       form=form,
                                       name_to_update=name_to_update,
                                       id=id)
        else:
            db.session.commit()
            flash("User Updated Successfully", category="success")
            return redirect(url_for('dashboard'))
    else:
        return render_template("update.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id or current_user.id == 1:

        user_to_delete = Users.query.get_or_404(id)
        name = None
        form = UserForm()

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User Deleted Successfully!", category="success")

            return render_template("register.html",
                                   name=name,
                                   form=form)
        except:
            flash("Whoops! There was a problem deleting user, try again!", category="warning")
            return render_template("register.html",
                                   name=name,
                                   form=form)
    else:
        flash("Sorry, you can't delete that user!", category="danger")
        return redirect(url_for('dashboard'))


@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post_pic = form.post_pic.data

        if request.files['post_pic']:
            output_size = (1280, 1280)
            upload_pic = request.files['post_pic']
            post_pic_filename = secure_filename(upload_pic.filename)
            # post_pic_name = str(uuid.uuid1()) + "_" + post_pic_filename
            with Image.open(upload_pic.stream) as i:
                i.thumbnail(output_size)
                i.save(os.path.join(app.config['UPLOAD_FOLDER'], post_pic_filename))
                # post_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], post_pic_filename))
            post = Posts(title=form.title.data,
                         content=form.content.data,
                         poster_id=poster,
                         post_pic=post_pic_filename)
        else:
            post = Posts(title=form.title.data,
                         content=form.content.data,
                         poster_id=poster)
        form.title.data = ''
        form.content.data = ''
        form.post_pic.data = ''
        db.session.add(post)
        db.session.commit()
        flash("Blog Post Submitted Successfully!", category="success")
        posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=1, per_page=5)
        return render_template("posts.html", posts=posts, page=1)

    return render_template("add_post.html", form=form)


@app.route('/posts', methods=['GET', 'POST'])
@app.route('/posts/page/<int:page>', methods=['GET', 'POST'])
def posts(page=1):
    form1 = EmailForm()
    if form1.validate_on_submit():
        user_email = form1.email.data
        send_mail(sender='andy0427s@gmail.com',
                  recipients=[user_email],
                  subject='Thank for subscribe our newsletter',
                  template='subscribe_mail',
                  mailtype='html')
        form1.email.data = ''

    posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("posts.html", posts=posts, page=page, form1=form1)


@app.route('/posts/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Posts.query.get_or_404(id)
    form = CommentForm()
    comments = post.comments.order_by(Comments.date_posted)
    if form.validate_on_submit():
        comment = Comments(body=form.body.data,
                           post=post,
                           author=current_user._get_current_object())
        form.body.data = ''
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been published.", category="success")

    return render_template('post.html', post=post, form=form, comments=comments, id=id)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post_pic = form.post_pic.data

        if request.files['post_pic']:
            post_pic_filename = secure_filename(post_pic.filename)
            post_pic_name = str(uuid.uuid1()) + "_" + post_pic_filename
            post_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], post_pic_name))
            post.post_pic = post_pic_name

        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated!", category="success")
        return redirect(url_for('post', id=post.id))

    if current_user.id == post.poster_id or current_user.id == 1:
        form.title.data = post.title
        form.content.data = post.content
        return render_template('edit_post.html', form=form, id=post.id)
    else:
        flash("You Aren't Authorized To Edit that Post", category="danger")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id or id == 1:

        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash('Blog Post Was Deleted!', category="success")
            posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=1, per_page=5)
            return render_template("posts.html", posts=posts, page=1)

        except:
            flash("Whoops! There was a problem, please try again!", category="warning")
            posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=1, per_page=5)
            return render_template("posts.html", posts=posts, page=1)
    else:
        flash("You Aren't Authorized To Delete That Post!", category="danger")
        posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=1, per_page=5)
        return render_template("posts.html", posts=posts, page=1)


@app.route('/user/post/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def user_post_edit(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    id = current_user.id
    page_post = request.args.get('page_post', 1, type=int)
    pagination_post = Posts.query.filter_by(poster_id=id).order_by(Posts.date_posted).paginate(page=page_post,
                                                                                               per_page=5)
    posts = pagination_post.items

    page_comment = request.args.get('page_comment', 1, type=int)
    pagination_comment = Comments.query.filter_by(author_id=id).order_by(Comments.date_posted).paginate(
        page=page_comment,
        per_page=5)
    comments = pagination_comment.items

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post_pic = form.post_pic.data

        if request.files['post_pic']:
            post_pic_filename = secure_filename(post_pic.filename)
            post_pic_name = str(uuid.uuid1()) + "_" + post_pic_filename
            post_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], post_pic_name))
            post.post_pic = post_pic_name

        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated!", category="success")
        return redirect(url_for('dashboard', _anchor='personal_post',
                                posts=posts,
                                comments=comments,
                                pagination_comment=pagination_comment,
                                pagination_post=pagination_post))

    if current_user.id == post.poster_id or current_user.id == 1:
        form.title.data = post.title
        form.content.data = post.content
        return render_template('user_post_edit.html', form=form, id=post.id,
                               posts=posts,
                               comments=comments,
                               pagination_post=pagination_post,
                               pagination_comment=pagination_comment
                               )
    else:
        flash("You Aren't Authorized To Edit that Post", category="danger")
        return redirect(url_for('dashboard', _anchor='personal_post',
                                posts=posts,
                                comments=comments,
                                pagination_comment=pagination_comment,
                                pagination_post=pagination_post))


@app.route('/user/post/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def user_post_delete(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    page_post = request.args.get('page_post', 1, type=int)
    pagination_post = Posts.query.filter_by(poster_id=id).order_by(Posts.date_posted).paginate(page=page_post,
                                                                                               per_page=5)
    posts = pagination_post.items

    page_comment = request.args.get('page_comment', 1, type=int)
    pagination_comment = Comments.query.filter_by(author_id=id).order_by(Comments.date_posted).paginate(
        page=page_comment,
        per_page=5)
    comments = pagination_comment.items

    if id == post_to_delete.poster.id or id == 1:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash('Blog Post Was Deleted!', category="success")
            return redirect(url_for('dashboard', _anchor='personal_post',
                                    posts=posts,
                                    pagination_comment=pagination_comment,
                                    pagination_post=pagination_post))

        except:
            flash("Whoops! There was a problem, please try again!", category="warning")
            return redirect(url_for('dashboard', _anchor='personal_post',
                                    posts=posts,
                                    pagination_comment=pagination_comment,
                                    pagination_post=pagination_post))
    else:
        flash("You Aren't Authorized To Delete That Post!", category="danger")
        return redirect(url_for('dashboard', _anchor='personal_post',
                                posts=posts,
                                pagination_comment=pagination_comment,
                                pagination_post=pagination_post))


@app.route('/comments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_comment(id):
    comment = Comments.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment.body = form.body.data
        db.session.add(comment)
        db.session.commit()
        flash("Comment Has Been Updated", category="success")
        return redirect(url_for('post', id=comment.post_id))

    if current_user.id == comment.author_id or current_user.id == 1:
        form.body.data = comment.body
        return render_template('edit_comment.html', form=form, id=comment.post_id)

    else:
        flash("You Aren't Authorized To Edit that comment", category="danger")
        return redirect(url_for('post', id=comment.post_id))


@app.route('/comments/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_comment(id):
    comment_to_delete = Comments.query.get_or_404(id)
    id = current_user.id
    post_id = comment_to_delete.post_id
    if id == comment_to_delete.author_id or id == 1:

        try:
            db.session.delete(comment_to_delete)
            db.session.commit()
            flash('Comment Was Deleted!', category="success")
            return redirect(url_for('post', id=post_id))

        except:
            flash("Whoops! There was a problem, please try again!", category="warning")
            return redirect(url_for('post', id=post_id))
    else:
        flash("You Aren't Authorized To Delete That Post!", category="danger")
        return redirect(url_for('post', id=post_id))


@app.route('/user/comment/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def user_comment_edit(id):
    comment = Comments.query.get_or_404(id)
    form = CommentForm()
    page_post = request.args.get('page_post', 1, type=int)
    pagination_post = Posts.query.filter_by(poster_id=id).order_by(Posts.date_posted).paginate(page=page_post,
                                                                                               per_page=5)
    posts = pagination_post.items
    page_comment = request.args.get('page_comment', 1, type=int)
    pagination_comment = Comments.query.filter_by(author_id=id).order_by(Comments.date_posted).paginate(
        page=page_comment,
        per_page=5)
    comments = pagination_comment.items

    if form.validate_on_submit():
        comment.body = form.body.data
        db.session.add(comment)
        db.session.commit()
        flash("Comment Has Been Updated", category="success")
        return redirect(url_for('dashboard',
                                id=comment.post_id,
                                _anchor='personal_comment',
                                posts=posts,
                                comments=comments,
                                pagination_comment=pagination_comment,
                                pagination_post=pagination_post
                                ))

    if current_user.id == comment.author_id or current_user.id == 1:
        form.body.data = comment.body
        return render_template('user_comment_edit.html',
                               form=form,
                               id=comment.post_id,
                               _anchor='personal_comment',
                               posts=posts,
                               comments=comments,
                               pagination_comment=pagination_comment,
                               pagination_post=pagination_post
                               )

    else:
        flash("You Aren't Authorized To Edit that comment", category="danger")
        return redirect(url_for('dashboard',
                                id=comment.post_id,
                                _anchor='personal_comment',
                                posts=posts,
                                comments=comments,
                                pagination_comment=pagination_comment,
                                pagination_post=pagination_post
                                ))


@app.route('/user/comment/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def user_comment_delete(id):
    comment_to_delete = Comments.query.get_or_404(id)
    id = current_user.id
    post_id = comment_to_delete.post_id
    if id == comment_to_delete.author_id or id == 1:

        try:
            db.session.delete(comment_to_delete)
            db.session.commit()
            flash('Comment Was Deleted!', category="success")
            return redirect(url_for('dashboard', _anchor='personal_comment', id=post_id))

        except:
            flash("Whoops! There was a problem, please try again!", category="warning")
            return redirect(url_for('dashboard', id=post_id))
    else:
        flash("You Aren't Authorized To Delete That Post!", category="danger")
        return redirect(url_for('dashboard', id=post_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if user.confirm:
                if check_password_hash(user.password_hash, form.password.data):
                    login_user(user)
                    flash('Login Successfully!', category="success")
                    return redirect(url_for('dashboard'))
                else:
                    flash('Wrong Password - Try Again!', category="danger")
            else:
                flash('Sorry, your account does not be activated, please activate your account first!',
                      category="warning")
                return redirect(url_for('register'))
        else:
            flash("The User Doesn't Exist! - Try Again...", category="danger")
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You Have Been Logged Out! Thanks For Using Our Service~ ', category="success")
    return redirect(url_for('login'))


@app.route('/login/reset/password/', methods=['GET', 'POST'])
def resend_reset():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    form = ResetPWForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            token = user.create_token()
            user_email = form.email.data
            send_mail(sender='andy0427s@gmail.com',
                      recipients=[user_email],
                      subject='Reset Your Password',
                      template='reset_mail',
                      mailtype='html',
                      user=user,
                      token=token)
            form.email.data = ''
            flash("Check your email and follow the instruction to reset your password!", category="success")
        else:
            form.email.data = ''
            flash("Not found the valid account, please register your account first!", category="warning")
        return redirect(url_for("login"))
    return render_template("reset_password_email.html", form=form)


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = FormChangePWD()
    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.password_old.data):
            hashed_pw = generate_password_hash(form.password_new.data, "sha256")
            current_user.password_hash = hashed_pw
            db.session.add(current_user)
            db.session.commit()
            flash('You Have Already Change Your Password, Please Login Again.', category="success")
            return redirect(url_for('login'))
    return render_template('change_password.html', form=form)


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    form = FormResetPWD()
    if form.validate_on_submit():
        user = Users()
        user_id = user.confirm_token(token)
        if user_id:
            user = Users.query.filter_by(id=user_id).first()
            if user:
                hashed_pw = generate_password_hash(form.password_new.data, "sha256")
                user.password_hash = hashed_pw
                db.session.commit()
                flash('Reset Your Password Successfully, please log in again!', category='success')
                return redirect(url_for('login'))
            else:
                flash('Not found the user', category='warning')
                return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    id = current_user.id
    page_post = request.args.get('page_post', 1, type=int)
    pagination_post = Posts.query.filter_by(poster_id=id).order_by(Posts.date_posted).paginate(page=page_post,
                                                                                               per_page=5)
    posts = pagination_post.items

    page_comment = request.args.get('page_comment', 1, type=int)
    pagination_comment = Comments.query.filter_by(author_id=id).order_by(Comments.date_posted).paginate(
        page=page_comment,
        per_page=5)
    comments = pagination_comment.items

    return render_template('dashboard.html',
                           posts=posts,
                           pagination_post=pagination_post,
                           comments=comments,
                           pagination_comment=pagination_comment)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data
        posts = posts.filter(Posts.title.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html",
                               form=form,
                               searched=post.searched,
                               posts=posts)


@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1:
        users = Users.query.count()
        projects = Projects.query.count()
        posts = Posts.query.count()
        comments = Comments.query.count()

        return render_template("admin.html",
                               users=users,
                               projects=projects,
                               posts=posts,
                               comments=comments)
    else:
        flash("Sorry, you have to be Admin to access this page", category="danger")
        return redirect(url_for('dashboard'))


@app.route('/admin/user')
@login_required
def admin_user():
    id = current_user.id
    if id == 1:
        page = request.args.get('page', 1, type=int)
        pagination = Users.query.order_by(Users.date_added).paginate(page=page, per_page=10)
        users = pagination.items
        return render_template("admin_user.html", users=users, pagination=pagination)
    else:
        flash("Sorry, you have to be Admin to access this page", category="danger")
        return redirect(url_for('dashboard'))


@app.route('/admin/user/add', methods=['GET', 'POST'])
@login_required
def admin_user_add():
    form = UserForm()
    print(form.errors)
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, username=form.username.data, email=form.email.data,
                         password_hash=hashed_pw, confirm=True, about_author=form.about_author.data)
            db.session.add(user)
            db.session.commit()

        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''
        form.about_author.data = ''

        flash("Successfully add the user!", category="success")
        return redirect(url_for('admin_user'))
    print(form.errors)
    return render_template("admin_user_add.html", form=form)


@app.route('/admin/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_user_edit(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']

        if request.files['profile_pic']:
            output_size = (512, 512)
            name_to_update.profile_pic = request.files['profile_pic']
            # Generate a unique/secure filename
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            with Image.open(name_to_update.profile_pic.stream) as i:
                i.thumbnail(output_size)
                i.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

            # Save the profile img to the static directory
            # basedir = os.path.abspath(os.path.dirname(__file__))

            # i.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            # Save secured filename in db
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                flash("User Updated Successfully", category="success")
                return redirect(url_for('admin_user'))
                # return render_template("update.html",
                #                        form=form,
                #                        name_to_update=name_to_update,
                #                        id=id)
            except:
                flash("Error! Looks like there was a problem...try again!", category="danger")
                return redirect(url_for('admin_user'))
        else:
            db.session.commit()
            flash("User Updated Successfully", category="success")
            return redirect(url_for('admin_user'))
    else:
        return render_template("admin_user_form.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)


@app.route('/admin/user/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_user_delete(id):
    if current_user.id == 1:
        user_to_delete = Users.query.get_or_404(id)
        form = UserForm()

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User Deleted Successfully!", category="success")
            return redirect(url_for('admin_user'))

        except:
            flash("Whoops! There was a problem deleting user, try again!", category="warning")
            return redirect(url_for('admin_user'))
    else:
        flash("Sorry, you can't delete that user!", category="danger")
        return redirect(url_for('admin_user'))


@app.route('/admin/project')
@login_required
def admin_project():
    id = current_user.id
    if id == 1:
        page = request.args.get('page', 1, type=int)
        pagination = Projects.query.order_by(Projects.id).paginate(page=page, per_page=10)
        projects = pagination.items
        return render_template("admin_project.html", projects=projects, pagination=pagination)
    else:
        flash("Sorry, you have to be Admin to access this page", category="danger")
        return redirect(url_for('dashboard'))


@app.route('/admin/project/add', methods=['GET', 'POST'])
@login_required
def admin_project_add():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Projects(title=form.title.data,
                           content=form.content.data,
                           date_created=form.date_created.data,
                           img=form.img_path.data)
        form.title.data = ''
        form.content.data = ''
        form.date_created.data = ''
        form.img_path.data = ''
        db.session.add(project)
        db.session.commit()
        flash("Your project has been created.", category="success")
        return redirect(url_for('admin_project'))

    return render_template('admin_project_add.html', form=form)


@app.route('/admin/project/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_project_edit(id):
    form = ProjectForm()
    project = Projects.query.get_or_404(id)
    print(form.errors)
    if form.validate_on_submit():
        project.title = form.title.data
        project.content = form.content.data
        project.img = form.img_path.data
        db.session.add(project)
        db.session.commit()
        flash("Project Has Been Updated!", category="success")
        return redirect(url_for('admin_project'))

    print(form.errors)

    if current_user.id == 1:
        form.title.data = project.title
        form.content.data = project.content
        form.img_path.data = project.img
        return render_template('admin_project_edit.html',
                               form=form,
                               project=project)
    else:
        flash("You Aren't Authorized To Edit that Post", category="danger")
        return redirect(url_for('admin_project'))


@app.route('/admin/project/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_project_delete(id):
    if current_user.id == 1:
        form = ProjectForm()
        project = Projects.query.get_or_404(id)

        try:
            db.session.delete(project)
            db.session.commit()
            flash("User Deleted Successfully!", category="success")
            return redirect(url_for('admin_project'))

        except:
            flash("Whoops! There was a problem deleting user, try again!", category="warning")
            return redirect(url_for('admin_project'))
    else:
        flash("Sorry, you can't delete that user!", category="danger")
        return redirect(url_for('admin_project'))


@app.route('/admin/post')
@login_required
def admin_post():
    id = current_user.id
    if id == 1:
        page = request.args.get('page', 1, type=int)
        pagination = Posts.query.order_by(Posts.date_posted).paginate(page=page, per_page=10)
        posts = pagination.items
        return render_template("admin_post.html", posts=posts, pagination=pagination)
    else:
        flash("Sorry, you have to be Admin to access this page", category="danger")
        return redirect(url_for('dashboard'))


@app.route('/admin/post/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_post_edit(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post_pic = form.post_pic.data

        if request.files['post_pic']:
            post_pic_filename = secure_filename(post_pic.filename)
            post_pic_name = str(uuid.uuid1()) + "_" + post_pic_filename
            post_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], post_pic_name))
            post.post_pic = post_pic_name

        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated!", category="success")
        return redirect(url_for('admin_post'))

    if current_user.id == 1:
        form.title.data = post.title
        form.content.data = post.content
        return render_template('admin_post_form.html',
                               form=form,
                               id=post.id)
    else:
        flash("You Aren't Authorized To Edit that Post", category="danger")
        return redirect(url_for('admin_post'))


@app.route('/admin/post/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_post_delete(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == 1:

        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash('Blog Post Was Deleted!', category="success")
            return redirect(url_for('admin_post'))

        except:
            flash("Whoops! There was a problem, please try again!", category="warning")
            return redirect(url_for('admin_post'))
    else:
        flash("You Aren't Authorized To Delete That Post!", category="danger")
        return redirect(url_for('admin_post'))


@app.route('/admin/post/add', methods=['GET', 'POST'])
@login_required
def admin_post_add():
    form = PostForm()
    if form.validate_on_submit():
        poster = form.poster_id.data
        post_pic = form.post_pic.data

        if request.files['post_pic']:
            post_pic_filename = secure_filename(post_pic.filename)
            post_pic_name = str(uuid.uuid1()) + "_" + post_pic_filename
            post_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], post_pic_name))
            post = Posts(title=form.title.data,
                         content=form.content.data,
                         poster_id=poster,
                         post_pic=post_pic_name)
        else:
            post = Posts(title=form.title.data,
                         content=form.content.data,
                         poster_id=poster)
        form.title.data = ''
        form.content.data = ''
        form.post_pic.data = ''
        db.session.add(post)
        db.session.commit()
        flash("Blog Post Submitted Successfully!", category="success")
        return redirect(url_for('admin_post'))

    return render_template("admin_post_add.html", form=form)


@app.route('/admin/comment')
@login_required
def admin_comment():
    id = current_user.id
    if id == 1:
        page = request.args.get('page', 1, type=int)
        pagination = Comments.query.order_by(Comments.date_posted).paginate(page=page, per_page=10)
        comments = pagination.items
        return render_template("admin_comment.html", comments=comments, pagination=pagination)
    else:
        flash("Sorry, you have to be Admin to access this page", category="danger")
        return redirect(url_for('dashboard'))


@app.route('/admin/comment/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_comment_edit(id):
    comment = Comments.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment.body = form.body.data
        db.session.add(comment)
        db.session.commit()
        flash("Comment Has Been Updated", category="success")
        return redirect(url_for('admin_comment'))

    if current_user.id == 1:
        form.body.data = comment.body
        return render_template('admin_comment_form.html', form=form, id=comment.post_id)

    else:
        flash("You Aren't Authorized To Edit that comment", category="danger")
        return redirect(url_for('admin_comment'))


@app.route('/admin/comment/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_comment_delete(id):
    comment_to_delete = Comments.query.get_or_404(id)
    id = current_user.id
    post_id = comment_to_delete.post_id
    if id == 1:

        try:
            db.session.delete(comment_to_delete)
            db.session.commit()
            flash('Comment Was Deleted!', category="success")
            return redirect(url_for('admin_comment'))

        except:
            flash("Whoops! There was a problem, please try again!", category="warning")
            return redirect(url_for('admin_comment'))
    else:
        flash("You Aren't Authorized To Delete That Post!", category="danger")
        return redirect(url_for('admin_comment'))


@app.route('/admin/comment/add', methods=['GET', 'POST'])
@login_required
def admin_comment_add():
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comments(body=form.body.data,
                           author_id=form.author_id.data,
                           post_id=form.post_id.data)
        form.body.data = ''
        form.author_id.data = ''
        form.post_id.data = ''
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been published.", category="success")
        return redirect(url_for('admin_comment'))

    return render_template('admin_comment_add.html', form=form)


@app.route('/previous-page/<int:id>', methods=['GET', 'POST'])
def switch_prev_page(id):
    pre_post = Posts.query.filter(Posts.id < id).order_by(Posts.id.desc()).first()
    if pre_post:
        return redirect(url_for('post', id=pre_post.id))
    else:
        return redirect(url_for('post', id=id))


@app.route('/next-page/<int:id>', methods=['GET', 'POST'])
def switch_next_page(id):
    next_post = Posts.query.filter(Posts.id > id).order_by(Posts.id.asc()).first()
    if next_post:
        return redirect(url_for('post', id=next_post.id))
    else:
        return redirect(url_for('post', id=id))
