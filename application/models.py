"""Database models."""
from .db import db
from flask_login import UserMixin
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, current_user, login_required, roles_required, utils
import datetime

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('Users.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('Roles.id')))


class Role(db.Model, RoleMixin):
    __tablename__ = 'Roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    # If we were using Python 2.7, this would be __unicode__ instead.

    def __unicode__ (self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    account_id = db.Column(db.Integer, db.ForeignKey('Accounts.id'))
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('Users', lazy='dynamic'))
    profile = db.relationship('Profile', uselist=False, back_populates="user")
    files = db.relationship('File', back_populates="user")
    account = db.relationship("Account")


class Account(db.Model):
    __tablename__ = 'Accounts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    users = db.relationship('User', back_populates="account")
    projects = db.relationship('Project', back_populates="account")
    messages = db.relationship('Message', back_populates="account")


class Project(db.Model):
    __tablename__ = 'Projects'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    account_id = db.Column(db.Integer, db.ForeignKey('Accounts.id'))
    account = db.relationship("Account")
    files = db.relationship('File', back_populates="project")


class Profile(db.Model):
    __tablename__ = 'Profiles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255))
    bio = db.Column(db.String(255))
    name = db.Column(db.String(255))
    address1 = db.Column(db.String(255))
    address2 = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    zip = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    user = db.relationship('User', back_populates='profile')


tags_files = db.Table('tags_files',
    db.Column('tag_id', db.Integer, db.ForeignKey('Tags.id'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('Files.id'), primary_key=True)
)


class File(db.Model):
    __tablename__ = 'Files'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    path = db.Column(db.String(255))
    title = db.Column(db.String(255))
    desc = db.Column(db.UnicodeText())
    tags = db.relationship('Tag', secondary=tags_files, lazy='subquery', backref=db.backref('Files', lazy=True))
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    s3_key = db.Column(db.String(255))
    s3_url = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    user = db.relationship('User', back_populates='files')
    project_id = db.Column(db.Integer, db.ForeignKey('Projects.id'))
    project = db.relationship('Project', back_populates='files')


class Tag(db.Model):
    __tablename__ = 'Tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    tag_id = db.Column(db.String(255))
    weight = db.Column(db.Integer())
    tag_group_id = db.Column(db.Integer, db.ForeignKey('TagGroups.id'))
    tag_group = db.relationship("TagGroup", back_populates="tags")
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)


class TagGroup(db.Model):
    __tablename__ = 'TagGroups'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    tag_id = db.Column(db.String(255))
    weight = db.Column(db.Integer())
    tags = db.relationship("Tag", back_populates="tag_group")
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)


archives_files = db.Table('archives_files',
    db.Column('file_id', db.Integer, db.ForeignKey('Files.id'), primary_key=True),
    db.Column('archive_id', db.Integer, db.ForeignKey('Archives.id'), primary_key=True)
)


class Archive(db.Model):
    __tablename__ = 'Archives'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(255))
    name = db.Column(db.String(255))
    path = db.Column(db.String(255))
    link = db.Column(db.String(255))
    recipient_name = db.Column(db.String(255))
    recipient_email = db.Column(db.String(255))
    files = db.relationship('File', secondary=archives_files, lazy='subquery', backref=db.backref('Archives', lazy=True))
    archive_status_id = db.Column(db.Integer, db.ForeignKey('ArchiveStatuses.id'))
    archive_status = db.relationship("ArchiveStatus", back_populates="archives")
    notification_status_id = db.Column(db.Integer, db.ForeignKey('NotificationStatuses.id'))
    notification_status = db.relationship("NotificationStatus", back_populates="archives")
    downloads = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)


class ArchiveStatus(db.Model):
    __tablename__ = 'ArchiveStatuses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    tag_id = db.Column(db.String(255))
    archives = db.relationship("Archive", back_populates="archive_status")


class NotificationStatus(db.Model):
    __tablename__ = 'NotificationStatuses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    tag_id = db.Column(db.String(255))
    archives = db.relationship("Archive", back_populates="notification_status")


class Message(db.Model):
    __tablename__ = 'Messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    subject = db.Column(db.String(255))
    message = db.Column(db.UnicodeText())
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    account_id = db.Column(db.Integer, db.ForeignKey('Accounts.id'))
    account = db.relationship('Account', back_populates='messages')
