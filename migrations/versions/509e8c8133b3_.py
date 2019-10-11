"""empty message

Revision ID: 509e8c8133b3
Revises:
Create Date: 2019-10-07 23:28:20.254429

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '509e8c8133b3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    messages_table = op.create_table('Messages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('subject', sa.String(length=255), nullable=True),
    sa.Column('message', sa.UnicodeText(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.bulk_insert(messages_table, [
        {'id':1,'subject':'Downloads Ready','message':'Your downloads are ready. Download using the link below:',},
    ])
    notification_statuses_table = op.create_table('NotificationStatuses',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('tag_id', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.bulk_insert(notification_statuses_table, [
        {'id':1,'name':'Waiting','tag_id':'waiting',},
        {'id':2,'name':'In Progress','tag_id':'in-progress',},
        {'id':3,'name':'Sent','tag_id':'sent',},
        {'id':4,'name':'Error','tag_id':'error',},
    ])
    archive_statuses_table = op.create_table('ArchiveStatuses',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('tag_id', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.bulk_insert(archive_statuses_table, [
        {'id':1,'name':'Waiting','tag_id':'waiting',},
        {'id':2,'name':'In Progress','tag_id':'in-progress',},
        {'id':3,'name':'Complete','tag_id':'complete',},
        {'id':4,'name':'Error','tag_id':'error',},
    ])
    roles_table = op.create_table('Roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.bulk_insert(roles_table, [
        {'id':1,'name':'admin','description':'Administrator',},
        {'id':2,'name':'end-user','description':'End user',},
    ])
    op.create_table('TagGroups',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('tag_id', sa.String(length=255), nullable=True),
    sa.Column('weight', sa.Integer(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('Files',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('path', sa.String(length=255), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('desc', sa.UnicodeText(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('s3_key', sa.String(length=255), nullable=True),
    sa.Column('s3_url', sa.String(length=255), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['Users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Archives',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('uuid', sa.String(length=255), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('path', sa.String(length=255), nullable=True),
    sa.Column('link', sa.String(length=255), nullable=True),
    sa.Column('recipient_name', sa.String(length=255), nullable=True),
    sa.Column('recipient_email', sa.String(length=255), nullable=True),
    sa.Column('archive_status_id', sa.Integer(), nullable=True),
    sa.Column('notification_status_id', sa.Integer(), nullable=True),
    sa.Column('downloads', sa.Integer(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['notification_status_id'], ['NotificationStatuses.id'], ),
    sa.ForeignKeyConstraint(['archive_status_id'], ['ArchiveStatuses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Profiles',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=255), nullable=True),
    sa.Column('bio', sa.String(length=255), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('address1', sa.String(length=255), nullable=True),
    sa.Column('address2', sa.String(length=255), nullable=True),
    sa.Column('city', sa.String(length=255), nullable=True),
    sa.Column('state', sa.String(length=255), nullable=True),
    sa.Column('zip', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=255), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['Users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Tags',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('tag_id', sa.String(length=255), nullable=True),
    sa.Column('weight', sa.Integer(), nullable=True),
    sa.Column('tag_group_id', sa.Integer(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['tag_group_id'], ['TagGroups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles_users',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['Roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['Users.id'], )
    )
    op.create_table('archives_files',
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.Column('archive_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['Files.id'], ),
    sa.ForeignKeyConstraint(['archive_id'], ['Archives.id'], ),
    sa.PrimaryKeyConstraint('file_id', 'archive_id')
    )
    op.create_table('tags_files',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['Files.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['Tags.id'], ),
    sa.PrimaryKeyConstraint('tag_id', 'file_id')
    )
    # ### end Alembic commands ###



def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tags_files')
    op.drop_table('archives_files')
    op.drop_table('roles_users')
    op.drop_table('Tags')
    op.drop_table('Profiles')
    op.drop_table('Archives')
    op.drop_table('Users')
    op.drop_table('TagGroups')
    op.drop_table('Roles')
    op.drop_table('ArchiveStatuses')
    op.drop_table('NotificationStatuses')
    op.drop_table('Messages')
    op.drop_table('Files')
    # ### end Alembic commands ###
