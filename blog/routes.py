from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from blog import app, db, login_manager
from blog.forms import UserForm, NameForm, PostForm, LoginForm, SearchForm, CommentForm
from blog.models import Users, Posts, Comments

import os
import uuid as uuid


@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")


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
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        flash("User Registered Successfully!", category="success")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("register.html",
                           name=name,
                           form=form,
                           our_users=our_users)


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
            name_to_update.profile_pic = request.files['profile_pic']
            # Generate a unique/secure filename
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            # Save the profile img to the static directory
            # basedir = os.path.abspath(os.path.dirname(__file__))
            name_to_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
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
            our_users = Users.query.order_by(Users.date_added)
            return render_template("register.html",
                                   name=name,
                                   form=form,
                                   our_users=our_users)
        except:
            flash("Whoops! There was a problem deleting user, try again!", category="warning")
            return render_template("register.html",
                                   name=name,
                                   form=form,
                                   our_users=our_users)
    else:
        flash("Sorry, you can't delete that user!", category="danger")
        return redirect(url_for('dashboard'))


@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster)
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        db.session.add(post)
        db.session.commit()
        flash("Blog Post Submitted Successfully!", category="success")

    return render_template("add_post.html", form=form)


# @app.route('/posts')
# def posts():
#     posts = Posts.query.order_by(Posts.date_posted)
#     return render_template("posts.html", posts=posts)

@app.route('/posts')
@app.route('/posts/page/<int:page>')
def posts(page=1):
    posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("posts.html", posts=posts, page=page)


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

    return render_template('post.html', post=post, form=form, comments=comments)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
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
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)

        except:
            flash("Whoops! There was a problem, please try again!", category="warning")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    else:
        flash("You Aren't Authorized To Delete That Post!", category="danger")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


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

    if current_user.id == comment.author_id or current_user == 1:
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
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Login Successfully!', category="success")
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong Password - Try Again!', category="danger")
        else:
            flash('The User Doesn\'t Exist! - Try Again...', category="danger")
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You Have Been Logged Out! Thanks For Using Our Service~ ', category="success")
    return redirect(url_for('login'))


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
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
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
