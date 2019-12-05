"""Database models."""
from .db import db
from flask_login import UserMixin
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, current_user, login_required, roles_required, utils
import datetime

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('Users.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('Roles.id')))

accounts_users = db.Table('accounts_users',
        db.Column('account_id', db.Integer(), db.ForeignKey('Accounts.id')),
        db.Column('user_id', db.Integer(), db.ForeignKey('Users.id')))

projects_users = db.Table('projects_users',
        db.Column('project_id', db.Integer(), db.ForeignKey('Projects.id')),
        db.Column('user_id', db.Integer(), db.ForeignKey('Users.id')))

tags_files = db.Table('tags_files',
    db.Column('tag_id', db.Integer, db.ForeignKey('Tags.id'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('Files.id'), primary_key=True)
)

archives_files = db.Table('archives_files',
    db.Column('file_id', db.Integer, db.ForeignKey('Files.id'), primary_key=True),
    db.Column('archive_id', db.Integer, db.ForeignKey('Archives.id'), primary_key=True)
)




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

    # many to one
    account_id = db.Column(db.Integer, db.ForeignKey('Accounts.id'))
    account = db.relationship("Account", foreign_keys=[account_id])

    # many to one
    #project_id = db.Column(db.Integer, db.ForeignKey('Projects.id'))
    #project = db.relationship("Project", foreign_keys=[project_id])


    # one to one
    profile = db.relationship("Profile", uselist=False, back_populates="user", foreign_keys='Profile.user_id')

    # many to many
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('Users', lazy='dynamic'))
    accounts = db.relationship('Account', secondary=accounts_users, backref=db.backref('Users', lazy='dynamic'))
    projects = db.relationship('Project', secondary=projects_users, backref=db.backref('Users', lazy='dynamic'))

    # one to many
    notifications = db.relationship('Notification', back_populates="user", foreign_keys='Notification.user_id')

    files_created = db.relationship('File', back_populates="creator")
    archives_created = db.relationship('Archive', back_populates="creator")
    projects_created = db.relationship('Project', back_populates="creator")
    profiles_created = db.relationship('Profile', back_populates="creator", foreign_keys='Profile.creator_id')
    notifications_created = db.relationship('Notification', back_populates="creator", foreign_keys='Notification.creator_id')
    message_templates_created = db.relationship('MessageTemplate', back_populates="creator")


class Account(db.Model):
    __tablename__ = 'Accounts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    users = db.relationship('User', back_populates="account")
    projects = db.relationship('Project', back_populates="account")
    message_templates = db.relationship('MessageTemplate', back_populates="account")
    profiles = db.relationship('Profile', back_populates="account")


class Profile(db.Model):
    __tablename__ = 'Profiles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    bio = db.Column(db.String(255))
    address1 = db.Column(db.String(255))
    address2 = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    zip = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    user = db.relationship('User', back_populates="profile", foreign_keys='Profile.user_id')
    account_id = db.Column(db.Integer, db.ForeignKey('Accounts.id'))
    account = db.relationship("Account")
    creator_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    creator = db.relationship('User', back_populates="profiles_created", foreign_keys='Profile.creator_id')


class Project(db.Model):
    __tablename__ = 'Projects'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    duedate = db.Column(db.DateTime())
    account_id = db.Column(db.Integer, db.ForeignKey('Accounts.id'))
    account = db.relationship("Account")
    creator_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    creator = db.relationship('User', back_populates='projects_created')

    # one to many
    files = db.relationship('File', back_populates="project")
    archives = db.relationship('Archive', back_populates="project")
    notifications = db.relationship('Notification', back_populates="project")
    # many to many
    users = db.relationship('User', secondary=projects_users, backref=db.backref('Projects', lazy='dynamic'))


class File(db.Model):
    __tablename__ = 'Files'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    path = db.Column(db.String(255))
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    tags = db.relationship('Tag', secondary=tags_files, lazy='subquery', backref=db.backref('Files', lazy=True))
    s3_key = db.Column(db.String(255))
    s3_url = db.Column(db.String(255))
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    creator_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    creator = db.relationship('User', back_populates='files_created', foreign_keys=[creator_id])
    project_id = db.Column(db.Integer, db.ForeignKey('Projects.id'))
    project = db.relationship('Project', back_populates='files', foreign_keys=[project_id])

class Archive(db.Model):
    __tablename__ = 'Archives'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(255))
    name = db.Column(db.String(255))
    path = db.Column(db.String(255))
    link = db.Column(db.String(255))
    #recipient_name = db.Column(db.String(255))
    #recipient_email = db.Column(db.String(255))
    files = db.relationship('File', secondary=archives_files, lazy='subquery', backref=db.backref('Archives', lazy=True))
    status_name = db.Column(db.String(255), db.ForeignKey('Statuses.name'))
    status = db.relationship("Status")
    downloads = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    creator_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    creator = db.relationship('User', back_populates='archives_created', foreign_keys=[creator_id])
    project_id = db.Column(db.Integer, db.ForeignKey('Projects.id'))
    project = db.relationship('Project', back_populates='archives', foreign_keys=[project_id])


class Notification(db.Model):
    __tablename__ = 'Notifications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    user = db.relationship('User', back_populates="notifications", foreign_keys='Notification.user_id')
    message_template_id = db.Column(db.Integer, db.ForeignKey('MessageTemplates.id'))
    message_template = db.relationship('MessageTemplate', back_populates='notifications', foreign_keys=[message_template_id])
    status_name = db.Column(db.String(255), db.ForeignKey('Statuses.name'))
    status = db.relationship("Status")
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    project_id = db.Column(db.Integer, db.ForeignKey('Projects.id'))
    project = db.relationship("Project")
    creator_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    creator = db.relationship('User', back_populates='notifications_created', foreign_keys='Notification.creator_id')


class Status(db.Model):
    __tablename__ = 'Statuses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))


class MessageTemplate(db.Model):
    __tablename__ = 'MessageTemplates'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    subject = db.Column(db.String(255))
    message = db.Column(db.UnicodeText())
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    account_id = db.Column(db.Integer, db.ForeignKey('Accounts.id'))
    account = db.relationship('Account', back_populates='message_templates', foreign_keys=[account_id])
    notifications = db.relationship('Notification', back_populates="message_template")
    creator_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    creator = db.relationship('User', back_populates='message_templates_created', foreign_keys=[creator_id])


class Tag(db.Model):
    __tablename__ = 'Tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))
    weight = db.Column(db.Integer(), default=0)
    tag_group_name = db.Column(db.String(255), db.ForeignKey('TagGroups.name'))
    tag_group = db.relationship("TagGroup", back_populates="tags")
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)


class TagGroup(db.Model):
    __tablename__ = 'TagGroups'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))
    weight = db.Column(db.Integer(), default=0)
    tags = db.relationship("Tag", back_populates="tag_group")
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
