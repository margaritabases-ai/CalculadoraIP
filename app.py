import os
from dataclasses import asdict
from flask import Flask, render_template, request, jsonify
from core.calculators import calculate_cidr, calculate_vlsm

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/cidr", methods=["POST"])
def api_cidr():
    data = request.get_json(silent=True) or {}
    ip_input = data.get("ip", "")
    mask_input = data.get("mask", "")
    try:
        result = calculate_cidr(ip_input, mask_input)
        return jsonify({"ok": True, "data": result}), 200
    except ValueError as err:
        return jsonify({"ok": False, "error": str(err)}), 400


@app.route("/api/vlsm", methods=["POST"])
def api_vlsm():
    data = request.get_json(silent=True) or {}
    base_cidr = data.get("base_cidr", "")
    raw_subnets = data.get("subnets", [])

    try:
        requirements = []
        for item in raw_subnets:
            name = str(item.get("name", "")).strip() or "Subred"
            hosts_val = item.get("hosts")
            if isinstance(hosts_val, bool) or not str(hosts_val).strip().isdigit():
                raise ValueError(f"Cantidad de hosts inválida en '{name}': '{hosts_val}'")
            requirements.append((name, int(hosts_val)))

        result = calculate_vlsm(base_cidr, requirements)
        result["allocations"] = [asdict(a) for a in result["allocations"]]
        return jsonify({"ok": True, "data": result}), 200
    except ValueError as err:
        return jsonify({"ok": False, "error": str(err)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)