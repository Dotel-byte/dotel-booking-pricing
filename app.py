from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

def calculate_dotel_pricing(dropoff_time, pickup_time):
    daycare_rate = 48
    half_day_rate = 24
    boarding_rate = 60
    extra_hour_rate = 7
    full_day_cutoff = 18  # 6 PM
    half_day_cutoff = 14  # 2 PM
    boarding_start = 14  # 2 PM
    boarding_end = 11  # 11 AM next day
    extra_hour_limit = 4  # Max extra hours allowed before charging full-day

    dropoff = datetime.datetime.strptime(dropoff_time, "%Y-%m-%dT%H:%M")
    pickup = datetime.datetime.strptime(pickup_time, "%Y-%m-%dT%H:%M")

    is_boarding = pickup.date() > dropoff.date() or pickup.hour >= boarding_end

    total_price = 0
    
    if dropoff.hour < half_day_cutoff:
        if pickup.date() == dropoff.date() and pickup.hour < half_day_cutoff:
            total_price = half_day_rate
        elif pickup.date() == dropoff.date() and pickup.hour >= half_day_cutoff:
            total_price = daycare_rate
        elif is_boarding:
            total_price = daycare_rate + boarding_rate
    elif dropoff.hour >= boarding_start:
        if is_boarding:
            total_price = boarding_rate

    if not is_boarding and pickup.date() == dropoff.date() and pickup.hour > full_day_cutoff:
        extra_hours = pickup.hour - full_day_cutoff
        if extra_hours <= extra_hour_limit:
            total_price += extra_hours * extra_hour_rate
        else:
            total_price += daycare_rate

    if is_boarding and pickup.hour > boarding_end:
        extra_hours = pickup.hour - boarding_end
        if extra_hours <= half_day_cutoff:
            total_price += half_day_rate
        else:
            total_price += daycare_rate

    return total_price

@app.route('/calculate-price', methods=['GET'])
def get_price():
    dropoff_time = request.args.get('dropoff_time')
    pickup_time = request.args.get('pickup_time')
    if not dropoff_time or not pickup_time:
        return jsonify({"error": "Missing required parameters"}), 400
    try:
        price = calculate_dotel_pricing(dropoff_time, pickup_time)
        return jsonify({"total_price": price})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
