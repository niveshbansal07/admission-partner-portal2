from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Lead, Payment, Partner, Admin
from extensions import db

report_bp = Blueprint("report", __name__, template_folder="templates/report")


@report_bp.route("/admin", methods=["GET"])
@jwt_required()
def admin_reports_page():
    admin_id = get_jwt_identity()
    admin_name = Admin.query.get(admin_id).name
    return render_template("admin_reports.html", admin_name=admin_name)

@report_bp.route("/admin/api/reports", methods=["GET"])
@jwt_required()
def admin_reports_api():
    total_leads = Lead.query.count()

    converted = Lead.query.filter_by(
        status="converted"
    ).count()

    payment_pending = db.session.query(
        db.func.sum(Payment.amount)
    ).filter_by(
        released=False
    ).scalar() or 0

    return {
        "total_leads": total_leads,
        "converted": converted,
        "payment_pending": payment_pending
    }

@report_bp.route("/partner", methods=["GET"])
@jwt_required()
def partner_reports():
    partner_id = get_jwt_identity()
    partner = Partner.query.get(partner_id)
    partner_name = partner.name
    return render_template("partner_reports.html", partner_name=partner_name)

@report_bp.route("/partner/api/reports", methods=["GET"])
@jwt_required()
def partner_reports_api():
    partner_id = get_jwt_identity()

    total_leads = Lead.query.filter_by(partner_id=partner_id).count()
    converted = Lead.query.filter_by(
        partner_id=partner_id,
        status="converted"
    ).count()

    payment_released = db.session.query(
        db.func.sum(Payment.amount)
    ).filter_by(
        partner_id=partner_id,
        released=True
    ).scalar() or 0

    payment_pending = db.session.query(
        db.func.sum(Payment.amount)
    ).filter_by(
        partner_id=partner_id,
        released=False
    ).scalar() or 0

    return jsonify({
        "total_leads": total_leads,
        "converted": converted,
        "payment_released": payment_released,
        "payment_pending": payment_pending
    })
