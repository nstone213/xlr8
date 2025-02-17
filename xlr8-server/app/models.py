from app import db
from datetime import datetime, timezone
from sqlalchemy.orm import validates

# Utility function
def register_temp_user(ip):
    tempUser = TempUser(ip_addr=ip)
    db.session.add(tempUser)
    db.session.commit()
    return tempUser

def load_des_image():
    with open('app/static/desmos.png', 'rb') as img_file:
        return img_file.read()

# Association tables
managed_users_table = db.Table(
    'managed_users',
    db.Column('manager_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('employee_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
)

user_org_table = db.Table(
    'user_org',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('org_id', db.Integer, db.ForeignKey('orgs.id', ondelete='CASCADE'), primary_key=True)
)

user_file_table = db.Table(
    'user_file',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('files.id', ondelete='CASCADE'), primary_key=True),
    db.Column('local_path', db.String(255))
)

file_orgs_table = db.Table(
    'file_org',
    db.Column('org_id', db.Integer, db.ForeignKey('orgs.id', ondelete='CASCADE'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('files.id', ondelete='CASCADE'), primary_key=True)
)

# User model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    birthday = db.Column(db.JSON, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    phoneNumber = db.Column(db.JSON, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    temporary = db.Column(db.Boolean, nullable=False)
    base_path = db.Column(db.String(255), nullable=True)

    filesOwned = db.relationship('File', backref='owning_user', cascade='all, delete-orphan')

    managed_users = db.relationship(
        'User',
        secondary=managed_users_table,
        primaryjoin=id == managed_users_table.c.manager_id,
        secondaryjoin=id == managed_users_table.c.employee_id,
        backref=db.backref('managers', lazy='dynamic'),
        lazy='dynamic'
    )

    orgs = db.relationship(
        'Org',
        secondary=user_org_table,
        back_populates='users'
    )

# Temporary users
class TempUser(db.Model):
    __tablename__ = 'tempusers'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_addr = db.Column(db.String, nullable=False)


# File model
class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    fileName = db.Column(db.String(50), nullable=False)
    path = db.Column(db.String(255), nullable=True)
    ext = db.Column(db.String(50), nullable=False)
    version = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    owning_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    orgs = db.relationship('Org', secondary=file_orgs_table, back_populates='files')
    users = db.relationship('User', secondary=user_file_table, backref='files')

    image = db.Column(db.LargeBinary, nullable=True)

    @validates('ext')
    def validate_ext(self, key, ext_value):
        # Automatically assign the image if the file has a "des" extension
        if ext_value == "des" and not self.image:
            self.image = load_des_image()
        return ext_value
    
    def assign_default_image(self):
        if self.ext == "des" and not self.image:
            self.image = load_des_image()

# Org model
class Org(db.Model):
    __tablename__ = 'orgs'

    id = db.Column(db.Integer, primary_key=True)
    orgName = db.Column(db.String(50), nullable=False, unique=True)
    users = db.relationship('User', secondary=user_org_table, back_populates='orgs')
    files = db.relationship('File', secondary=file_orgs_table, back_populates='orgs')
    signing_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    signing_user = db.relationship('User', foreign_keys=[signing_user_id])

# FileAccessLog model
class FileAccessLog(db.Model):
    __tablename__ = 'file_access_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    temp_user_id = db.Column(db.Integer, db.ForeignKey('tempusers.id', ondelete='CASCADE'), nullable=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id', ondelete='CASCADE'), nullable=True)
    accessed_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

    user = db.relationship('User', backref='file_access_logs')
    file = db.relationship('File', backref='file_access_logs')
    temp_user = db.relationship('TempUser', backref='file_access_logs')

ext_lookup_json = {
    "des": "serve_desmos.html",
    "docx": "test_google.html"
}
