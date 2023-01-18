import requests
from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from blog import app, db, login_manager
from blog.forms import UserForm, NameForm, PostForm, LoginForm, SearchForm, CommentForm, FormChangePWD, EmailForm, \
    ResetPWForm, FormResetPWD, ContactForm
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
                  recipients=["andylee22011528@gmail.com"],
                  subject='Notice from website visitors',
                  template='contact_mail',
                  mailtype='html',
                  username=user_name,
                  message=user_message,
                  email=user_email)
        flash("goodas", category="success")
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
    if id == current_user.id:

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
        posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=1, per_page=5)
        return render_template("posts.html", posts=posts, page=1)

    return render_template("add_post.html", form=form)


# @app.route('/posts')
# def posts():
#     posts = Posts.query.order_by(Posts.date_posted)
#     return render_template("posts.html", posts=posts)

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
    return render_template('dashboard.html')


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
        return render_template("admin.html")
    else:
        flash("Sorry, you have to be Admin to access this page", category="danger")
        return redirect(url_for('dashboard'))


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


