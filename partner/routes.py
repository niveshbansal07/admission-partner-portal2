from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_jwt_extended import get_jwt_identity
from models import Lead, Payment, Partner
from extensions import db
from auth.routes import role_required
from decimal import Decimal
import os
from werkzeug.utils import secure_filename


partner_bp = Blueprint("partner", __name__, template_folder="templates/partner")

@partner_bp.route("/dashboard")
@role_required("partner")
def dashboard():
    partner_id = get_jwt_identity()
    partner = Partner.query.get(partner_id)

    if partner.status != "active":
        flash("Your account is blocked by Admin", "error")
        return redirect(url_for("auth.logout"))
    
    leads = Lead.query.filter_by(partner_id=partner_id).all()
    total_revenue = 0

    for l in leads:
        # default values (blank)
        l.course_name = ""
        l.course_price = ""
        l.partner_revenue = ""

        if l.status == "Converted" and l.course:
            l.course_name = l.course.title
            l.course_price = l.course.price
            l.partner_revenue = (l.course.price * Decimal("0.25")).quantize(Decimal("0.01"))
            total_revenue += l.partner_revenue

    return render_template(
        "dashboard.html",
        partner_name=partner.name,
        leads=leads,
        total_payment=round(total_revenue, 2)
    )

@partner_bp.route("/create_lead", methods=["GET", "POST"])
@role_required("partner")
def create_lead():
    partner_id = get_jwt_identity()
    partner = Partner.query.get(partner_id)
    partner_name = partner.name
    
    if request.method == "POST":
        student_name=request.form['student_name'],
        mobile=request.form['mobile'],
        email=request.form['email'],
        current_status=request.form['current_status'],
        address=request.form['address'],
        partner_id=partner_id
    

        existing_lead = Lead.query.filter_by(mobile=mobile).first()
        if existing_lead:
            flash("Mobile number already exists!", "danger")
            return redirect(url_for("partner.create_lead"))
        
        lead = Lead(student_name=student_name, mobile=mobile, email=email, current_status=current_status, address=address, partner_id=partner_id)
        
        try:
            db.session.add(lead)
            db.session.commit()
            flash("Lead created successfully", "success")
            return redirect(url_for("partner.dashboard"))
        except:
            db.session.rollback()
            flash("Duplicate entry detected!", "danger")
            return redirect(url_for("partner.create_lead"))
    return render_template("create_lead.html", partner_name=partner_name)

@partner_bp.route("/payment")
@role_required("partner")
def payments_page():
    partner_id = get_jwt_identity()
    partner = Partner.query.get(partner_id)
    partner_name = partner.name
    return render_template("payment.html", partner_name=partner_name)

@partner_bp.route("/api/payment")
@role_required("partner")
def payments_api():
    partner_id = get_jwt_identity() 

    payments = (
        db.session.query(Payment, Lead)
        .join(Lead, Payment.lead_id == Lead.id)
        .filter(Payment.partner_id == partner_id)
        .all()
    )

    data = []
    for p, l in payments:
        data.append({
            "student_name": l.student_name,
            "lead_id": l.id,
            "amount": p.amount,
            "status": "Released" if p.released else "Pending",
            "release_date": p.release_date.strftime("%Y-%m-%d") if p.release_date else None
        })

    return jsonify(data)


# UPLOAD_FOLDER = "static/uploads/bank_proofs"

# @partner_bp.route("/profile", methods=["GET", "POST"])
# @role_required("partner")
# def update_profile():
#     partner_id = get_jwt_identity()
#     partner = Partner.query.get_or_404(partner_id)
#     partner_name = partner.name

#     if request.method == "POST":
#         # ---------------- BASIC PROFILE ----------------
#         partner.name = request.form.get("name")
#         partner.shop_name = request.form.get("shop_name")
#         partner.profession = request.form.get("profession")
#         partner.email = request.form.get("email")

#          # ---------------- BANK DETAILS (ONLY ONCE) ----------------
#         if not partner.bank_details_locked:
#             bank_name = request.form.get("bank_name")
#             acc_holder = request.form.get("account_holder_name")
#             acc_number = request.form.get("account_number")
#             ifsc = request.form.get("ifsc_code")
#             bank_proof = request.files.get("bank_proof")

#             if bank_name and acc_number and bank_proof:
#                 filename = secure_filename(bank_proof.filename)
#                 os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#                 file_path = os.path.join(UPLOAD_FOLDER, filename)
#                 bank_proof.save(file_path)

#                 partner.bank_name = bank_name
#                 partner.account_holder_name = acc_holder
#                 partner.account_number = acc_number
#                 partner.ifsc_code = ifsc
#                 partner.bank_proof = file_path
#                 partner.bank_details_locked = True

#         # ---------------- DOCUMENT UPLOAD ----------------
#         aadhar_number = request.form.get("aadhar_number")
#         pan_number = request.form.get("pan_number")

#         aadhar_file = request.files.get("aadhar_doc")
#         pan_file = request.files.get("pan_doc")

#         DOC_FOLDER = os.path.join(UPLOAD_FOLDER, "documents")
#         os.makedirs(DOC_FOLDER, exist_ok=True)

#         if aadhar_file:
#             aadhar_filename = secure_filename(aadhar_file.filename)
#             aadhar_path = os.path.join(DOC_FOLDER, aadhar_filename)
#             aadhar_file.save(aadhar_path)

#             partner.aadhar_number = aadhar_number
#             partner.aadhar_doc = aadhar_path

#         if pan_file:
#             pan_filename = secure_filename(pan_file.filename)
#             pan_path = os.path.join(DOC_FOLDER, pan_filename)
#             pan_file.save(pan_path)

#             partner.pan_number = pan_number
#             partner.pan_doc = pan_path


#         db.session.commit()
#         flash("Profile updated successfully", "success")
#         return redirect(url_for("partner.update_profile"))

#     return render_template("profile.html", partner=partner, partner_name=partner_name)


UPLOAD_FOLDER = "static/uploads/bank_proofs"

@partner_bp.route("/profile", methods=["GET", "POST"])
@role_required("partner")
def update_profile():
    partner_id = get_jwt_identity()
    partner = Partner.query.get_or_404(partner_id)
    partner_name = partner.name

    if request.method == "POST":

        # ---------------- BASIC PROFILE ----------------
        partner.name = request.form.get("name")
        partner.shop_name = request.form.get("shop_name")
        partner.profession = request.form.get("profession")
        partner.email = request.form.get("email")

        # ---------------- BANK DETAILS (ONLY ONCE) ----------------
        if not partner.bank_details_locked:
            bank_name = request.form.get("bank_name")
            acc_holder = request.form.get("account_holder_name")
            acc_number = request.form.get("account_number")
            ifsc = request.form.get("ifsc_code")
            bank_proof = request.files.get("bank_proof")

            if bank_name and acc_number and bank_proof:
                filename = secure_filename(bank_proof.filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)

                file_path = os.path.join(UPLOAD_FOLDER, filename)
                bank_proof.save(file_path)

                partner.bank_name = bank_name
                partner.account_holder_name = acc_holder
                partner.account_number = acc_number
                partner.ifsc_code = ifsc
                partner.bank_proof = file_path
                partner.bank_details_locked = True

        # ---------------- DOCUMENT UPLOAD ----------------
        aadhar_number = request.form.get("aadhar_number")
        pan_number = request.form.get("pan_number")

        aadhar_file = request.files.get("aadhar_doc")
        pan_file = request.files.get("pan_doc")

        DOC_FOLDER = os.path.join(UPLOAD_FOLDER, "documents")
        os.makedirs(DOC_FOLDER, exist_ok=True)

        if aadhar_number and aadhar_file:
            aadhar_filename = secure_filename(aadhar_file.filename)
            aadhar_path = os.path.join(DOC_FOLDER, aadhar_filename)
            aadhar_file.save(aadhar_path)

            partner.aadhar_number = aadhar_number
            partner.aadhar_doc = aadhar_path

        if pan_file and pan_file:
            pan_filename = secure_filename(pan_file.filename)
            pan_path = os.path.join(DOC_FOLDER, pan_filename)
            pan_file.save(pan_path)

            partner.pan_number = pan_number
            partner.pan_doc = pan_path

        db.session.commit()
        flash("Profile updated successfully", "success")
        return redirect(url_for("partner.update_profile"))

    return render_template(
        "profile.html",
        partner=partner,
        partner_name=partner_name
    )
