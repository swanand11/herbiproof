from flask import Flask, request, jsonify
from db import DatabaseManager

app = Flask(__name__)
db = DatabaseManager()


# ---------- GET Endpoints (first 10 entries) ----------
@app.route("/kyc", methods=["GET"])
def get_kyc():
    rows = db.execute_query("SELECT * FROM KYC LIMIT 10")
    return jsonify(rows)


@app.route("/farmers", methods=["GET"])
def get_farmers():
    rows = db.execute_query("SELECT * FROM Farmers LIMIT 10")
    return jsonify(rows)


@app.route("/consumers", methods=["GET"])
def get_consumers():
    rows = db.execute_query("SELECT * FROM Consumers LIMIT 10")
    return jsonify(rows)


@app.route("/aggregators", methods=["GET"])
def get_aggregators():
    rows = db.execute_query("SELECT * FROM Aggregators LIMIT 10")
    return jsonify(rows)


@app.route("/manufacturers", methods=["GET"])
def get_manufacturers():
    rows = db.execute_query("SELECT * FROM Manufacturer LIMIT 10")
    return jsonify(rows)


@app.route("/batches", methods=["GET"])
def get_batches():
    rows = db.execute_query("SELECT * FROM Batch LIMIT 10")
    return jsonify(rows)


@app.route("/inspections", methods=["GET"])
def get_inspections():
    rows = db.execute_query("SELECT * FROM Inspection LIMIT 10")
    return jsonify(rows)


@app.route("/orders", methods=["GET"])
def get_orders():
    rows = db.execute_query("SELECT * FROM Orders LIMIT 10")
    return jsonify(rows)


@app.route("/ratings", methods=["GET"])
def get_ratings():
    rows = db.execute_query("SELECT * FROM Ratings LIMIT 10")
    return jsonify(rows)


# ---------- POST Endpoints (insert records) ----------
@app.route("/kyc", methods=["POST"])
def create_kyc():
    data = request.json
    success = db.create_kyc(data["kyc_id"], data["document_number"])
    return jsonify({"success": success})


@app.route("/farmers", methods=["POST"])
def create_farmer():
    data = request.json
    success = db.create_farmer(
        data["farmer_id"],
        data["name"],
        data.get("location", ""),
        data.get("contact_number", ""),
        data["kyc_id"],
    )
    return jsonify({"success": success})


@app.route("/consumers", methods=["POST"])
def create_consumer():
    data = request.json
    success = db.create_consumer(
        data["consumer_id"], data["consumer_name"], data.get("verification", "Pending")
    )
    return jsonify({"success": success})


@app.route("/batches", methods=["POST"])
def create_batch():
    data = request.json
    success = db.create_batch(
        data["batch_id"], data["type"], data.get("geotag", ""), data["farmer_id"]
    )
    return jsonify({"success": success})


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.json
    success = db.create_order(
        data["order_id"],
        data["order_from"],
        data["from_id"],
        data["receiver"],
        data["receiver_id"],
        data["batch_id"],
        data["quantity"],
        data["price"],
    )
    return jsonify({"success": success})


@app.route("/ratings", methods=["POST"])
def create_rating():
    data = request.json
    success = db.create_rating(
        data["rating_id"], data["consumer_id"], data["farmer_id"], data["rating"]
    )
    return jsonify({"success": success})


if __name__ == "__main__":
    app.run(debug=True)
