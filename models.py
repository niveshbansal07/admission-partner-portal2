from extensions import db
from decimal import Decimal
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(db.Model):
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    mobile = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='admin')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Partner(db.Model):
    __tablename__ = "partner"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    mobile = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    shop_name = db.Column(db.String(150))
    profession = db.Column(db.String(100))
    email = db.Column(db.String(255))
    status = db.Column(
    db.Enum('active', 'inactive', 'blocked', name='partner_status'),
    default='active',
    nullable=False
)   

    bank_name = db.Column(db.String(100))
    account_holder_name = db.Column(db.String(100))
    account_number = db.Column(db.String(30))
    ifsc_code = db.Column(db.String(20))
    bank_proof = db.Column(db.String(255))
    bank_details_locked = db.Column(db.Boolean, default=False)

    aadhar_number = db.Column(db.String(12))
    aadhar_doc = db.Column(db.String(255))
    pan_number = db.Column(db.String(10))
    pan_doc = db.Column(db.String(255))
    documents_verified = db.Column(db.Boolean, default=False)

    leads = db.relationship('Lead', backref='partner', lazy=True)
    payments = db.relationship('Payment', backref='partner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Lead(db.Model):
    __tablename__ = "leads"   

    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(150), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255))
    current_status = db.Column(db.String(255))
    address = db.Column(db.String(500))
    status = db.Column(
        db.Enum('Pending', 'In-Process', 'Converted', 'Not Converted', name='lead_status_enum'),
        default='Pending',
        nullable=False
    )
    payment_term = db.Column(
        db.Enum('Cash', 'Online', 'Other', name='payment_term_enum'),
        default=None,
        nullable=True
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey('courses.id', ondelete='SET NULL'),
        nullable=True
    )

    remark = db.Column(db.Text, nullable=True)
    remark_updated_at = db.Column(db.DateTime, nullable=True)  

    course = db.relationship('Course', backref='leads')
    partner_id = db.Column(db.Integer, db.ForeignKey('partner.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    payment = db.relationship('Payment', backref='lead', uselist=False)


class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partner.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    amount = db.Column(db.Float, default=0)
    released = db.Column(db.Boolean, default=False)
    release_date = db.Column(db.DateTime)

class Employee(db.Model):
    __tablename__ = "employee"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    mobile = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255))
    password_hash = db.Column(db.String(255), nullable=False)
    status = db.Column(
    db.Enum('active', 'inactive', 'blocked', name='partner_status'),
    default='active',
    nullable=False
)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(5, 2), default=Decimal("0.00"))
    real_price = db.Column(db.Numeric(10, 2), nullable=False)

    status = db.Column(
        db.Enum("active", "inactive", name="course_status"),
        default="active",
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def apply_discount(self):
        discount_amount = (self.price * self.discount) / Decimal("100")
        self.real_price = self.price - discount_amount