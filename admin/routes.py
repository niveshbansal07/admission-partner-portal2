from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import Partner, Lead, Payment, Admin, Employee, Course
from extensions import db
from sqlalchemy.exc import IntegrityError
from auth.routes import role_required
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func
from datetime import datetime
from decimal import Decimal

admin_bp = Blueprint("admin", __name__, template_folder="templates/admin")

@admin_bp.route("/panel")
@role_required("admin")
def panel():
    admin_id = get_jwt_identity()
    admin_name = Admin.query.get(admin_id).name

    total_partners = Partner.query.count()
    total_leads = Lead.query.count()
    total_converted = Lead.query.filter_by(status="Converted").count()
    pending_payments = Payment.query.filter_by(released=False).count()
    return render_template("panel.html",
                           total_partners=total_partners,
                           total_leads=total_leads,
                           total_converted=total_converted,
                           pending_payments=pending_payments,
                           admin_name=admin_name
)

@admin_bp.route("/partners")
@role_required("admin")
def partners():
    partners = Partner.query.all()

    # partner-wise total leads
    total_leads = (
        db.session.query(
            Lead.partner_id,
            func.count(Lead.id).label("total")
        )
        .group_by(Lead.partner_id)
        .all()
    )

    # partner-wise converted leads
    converted_leads = (
        db.session.query(
            Lead.partner_id,
            func.count(Lead.id).label("converted")
        )
        .filter(Lead.status == "converted")
        .group_by(Lead.partner_id)
        .all()
    )

    # dict bana lo easy access ke liye
    total_leads_dict = {p: c for p, c in total_leads}
    converted_dict = {p: c for p, c in converted_leads}

    admin_id = get_jwt_identity()
    admin_name = Admin.query.get(admin_id).name

    return render_template("partners.html", partners=partners, total_leads= total_leads_dict, converted=converted_dict, admin_name=admin_name)

@admin_bp.route("/partners/<int:partner_id>/status", methods=["POST"])
@role_required("admin")
def update_partner_status(partner_id):
    status = request.form.get("status")

    if status not in ["active", "inactive", "blocked"]:
        flash("Invalid status selected!", "error")
        return redirect(url_for("admin.partners"))

    partner = Partner.query.get_or_404(partner_id)
    partner.status = status
    db.session.commit()

    flash(f"Partner status updated to {status.upper()}", "success")
    return redirect(url_for("admin.partners"))

@admin_bp.route("/create_partner", methods=["GET", "POST"])
@role_required("admin")
def create_partner():
    admin_id = get_jwt_identity()
    admin_name = Admin.query.get(admin_id).name
    if request.method == "POST":
        name = request.form['name']
        mobile = request.form['mobile']
        password = request.form['password']

        existing_partner = Partner.query.filter_by(mobile=mobile).first()
        if existing_partner:
            flash("Mobile number already exists!", "danger")
            return redirect(url_for("admin.create_partner"))
        
        partner = Partner(name=name, mobile=mobile)
        partner.set_password(password)

        try:
            db.session.add(partner)
            db.session.commit()
            flash("Partner created successfully", "success")
            return redirect(url_for("admin.partners"))
        except:
            db.session.rollback()
            flash("Duplicate entry detected!", "danger")
            return redirect(url_for("admin.create_partner"))
    return render_template("create_partner.html", admin_name=admin_name)

@admin_bp.route("/leads")
@role_required("admin")
def leads():
    admin_id = get_jwt_identity()
    admin_name = Admin.query.get(admin_id).name
    leads = Lead.query.all()
    courses = Course.query.all()
    return render_template("leads.html", leads=leads, courses=courses, admin_name=admin_name)

@admin_bp.route("/update_lead/<int:lead_id>", methods=["POST"])
@role_required("admin")
def update_lead(lead_id):
    new_status = request.form.get("status")
    payment_term = request.form.get("payment_term")
    course_id = request.form.get('course_id')

    lead = Lead.query.get_or_404(lead_id)

    if new_status:
        if lead.status in ["Converted", "Not Converted"] and new_status != lead.status:
            flash("Lead status already finalized and cannot be changed.", "warning")
            return redirect(url_for("admin.leads"))
        lead.status = new_status

    # COURSE + PAYMENT ONLY IF CONVERTED
    if lead.status == "Converted":

        if course_id:
            lead.course_id = int(course_id)

        if payment_term:
            if payment_term not in ["Cash", "Online", "Other"]:
                flash("Invalid payment method.", "error")
                return redirect(url_for("admin.leads"))
            lead.payment_term = payment_term

    db.session.commit()
    flash("Lead updated successfully.", "success")
    return redirect(url_for("admin.leads"))


@admin_bp.route("/payments")
@role_required("admin")
def payments():
    payments = Payment.query.all()
    admin_id = get_jwt_identity()
    admin_name = Admin.query.get(admin_id).name
    return render_template("payments.html", payments=payments, admin_name=admin_name)


@admin_bp.route("/create_admin", methods=["GET", "POST"])
# @role_required("admin")
def create_admin():
    if request.method == "POST":
        name = request.form['name']
        mobile = request.form['mobile']
        email = request.form['email']
        password = request.form['password']

        existing_admin = Admin.query.filter(
    (Admin.mobile == mobile) | (Admin.email == email)
).first()
        
        if existing_admin:
            if existing_admin.mobile == mobile:
                flash("Mobile number already exists!", "danger")
            else:
                flash("Email already exists!", "danger")
            return redirect(url_for("admin.create_admin"))

        admin = Admin(name=name, mobile=mobile, email=email)
        admin.set_password(password)

        try:
            db.session.add(admin)
            db.session.commit()
            flash("Admin created successfully", "success")
            return redirect(url_for("admin.panel"))
        except IntegrityError:
            db.session.rollback()
            flash("Duplicate entry detected!", "danger")
            return redirect(url_for("admin.create_admin"))
    return render_template("create_admin.html")

@admin_bp.route("/employees")
@role_required("admin")
def employees():
    employees = Employee.query.all()
    admin_id = get_jwt_identity()
    admin_name = Admin.query.get(admin_id).name
    return render_template("employees.html", employees=employees, admin_name=admin_name)

@admin_bp.route("/create_employee", methods=["GET", "POST"])
@role_required("admin")
def create_employee():
    admin_id = get_jwt_identity()
    admin_name = Admin.query.get(admin_id).name
    if request.method == "POST":
        name = request.form['name']
        mobile = request.form['mobile']
        password = request.form['password']

        existing_employee = Employee.query.filter_by(mobile=mobile).first()
        if existing_employee:
            flash("Mobile number already exists!", "danger")
            return redirect(url_for("admin.create_employee"))
        
        employee = Employee(name=name, mobile=mobile)
        employee.set_password(password)

        try:
            db.session.add(employee)
            db.session.commit()
            flash("Employee created successfully", "success")
            return redirect(url_for("admin.employees"))
        except:
            db.session.rollback()
            flash("Duplicate entry detected!", "danger")
            return redirect(url_for("admin.create_employee"))
    return render_template("create_employee.html", admin_name=admin_name)

@admin_bp.route("/employees/<int:employee_id>/status", methods=["POST"])
@role_required("admin")
def update_employee_status(employee_id):
    status = request.form.get("status")

    if status not in ["active", "inactive", "blocked"]:
        flash("Invalid status selected!", "error")
        return redirect(url_for("admin.employees"))

    employee = Employee.query.get_or_404(employee_id)
    employee.status = status
    db.session.commit()

    flash(f"Employee status updated to {status.upper()}", "success")
    return redirect(url_for("admin.employees"))

@admin_bp.route("/courses")
@role_required("admin")
def courses():
    courses = Course.query.all()
    admin_id = get_jwt_identity()
    admin_name = Admin.query.get(admin_id).name
    return render_template("courses.html", courses=courses, admin_name=admin_name)

@admin_bp.route("/create_course", methods=["GET", "POST"])
@role_required("admin")
def create_course():
    admin_id = get_jwt_identity()
    admin_name = Admin.query.get(admin_id).name

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        price = float(request.form.get("price"))

        course = Course(
            title=title,
            description=description,
            price=price,
            discount=Decimal("0.00"),
            real_price=price, 
            status="active"
        )

        db.session.add(course)
        db.session.commit()

        flash("Course created successfully", "success")
        return redirect(url_for("admin.courses"))

    return render_template("create_course.html", admin_name=admin_name)

@admin_bp.route("/course/<int:id>/update", methods=["POST"])
@role_required("admin")
def update_course(id):
    course = Course.query.get_or_404(id)

    discount = Decimal(request.form.get("discount", 0))
    status = request.form.get("status")

    course.discount = discount
    course.status = status
    course.apply_discount()

    db.session.commit()
    flash("Course updated successfully", "success")

    return redirect(url_for("admin.courses"))

