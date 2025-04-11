from flask import Blueprint, request, jsonify, render_template
from blockchain_utils.web3_interface import get_nfts_for_wallet, get_token_metadata

cert_routes = Blueprint("cert_routes", __name__)

@cert_routes.route("/dashboard")
def dashboard():
    return render_template("my_certificates.html")

@cert_routes.route("/my-certificates")
def my_certificates():
    wallet = request.args.get("wallet")
    if not wallet:
        return jsonify([])

    token_ids = get_nfts_for_wallet(wallet)
    data = []

    for token_id in token_ids:
        meta = get_token_metadata(token_id)
        data.append({
            "token_id": token_id,
            "job_title": meta.get("job_title", ""),
            "company": meta.get("company", ""),
            "start_date": meta.get("start_date", ""),
            "end_date": meta.get("end_date", ""),
            "skills": meta.get("skills", ""),
            "performance_rating": meta.get("performance_rating", "")
        })

    return jsonify(data)

@cert_routes.route("/certificate/<int:token_id>")
def view_certificate(token_id):
    metadata = get_token_metadata(token_id)
    return render_template("certificate_details.html", token_id=token_id, meta=metadata)
