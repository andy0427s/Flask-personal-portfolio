from datetime import datetime
from blog import db


class BaseModel(db.Model):
    __abstract__ = True
    add_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Category(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    icon = db.Column(db.String(128), nullable=True)
    post = db.relationship('Post', backref='category', lazy=True)

    def __repr__(self):
        return '<Category %r>' % self.name


# Many-to-Many helper table
tags = db.Table('tags',
                db.Column('tag.id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
                db.Column('post.id', db.Integer, db.ForeignKey('post.id'), primary_key=True))


class Post(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    desc = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    tags = db.relationship('Tag', secondary=tags, lazy='subquery', backref=db.backref('post', lazy=True))

    def __repr__(self):
        return '<Post %r>' % self.title


class Tag(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)

    def __repr__(self):
        return self.name
