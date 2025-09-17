from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///energy.db'
db = SQLAlchemy(app)

# Database Models
class Appliance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    power = db.Column(db.Float, nullable=False)  # in Watts

class Usage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appliance_id = db.Column(db.Integer, db.ForeignKey('appliance.id'))
    hours_used = db.Column(db.Float, nullable=False)

# Energy saving tips
tips = [
    "💡 Use LED bulbs instead of CFL to save up to 80% energy.",
    "🌀 Set AC temperature to 24°C to save 15% energy.",
    "🔌 Turn off appliances in standby mode to save 10% electricity.",
    "🌞 Use natural light during daytime instead of electric lights."
]

# ---------------- Routes ----------------

@app.route('/')
def index():
    appliances = Appliance.query.all()
    return render_template('index.html', appliances=appliances)

@app.route('/calculate', methods=['POST'])
def calculate():
    appliance_id = request.form.get("appliance")
    hours = float(request.form.get("hours"))

    appliance = Appliance.query.get(appliance_id)
    energy_kwh = (appliance.power * hours) / 1000
    cost = energy_kwh * 8  # Assuming ₹8 per kWh

    # Save usage
    new_usage = Usage(appliance_id=appliance.id, hours_used=hours)
    db.session.add(new_usage)
    db.session.commit()

    return render_template("result.html", appliance=appliance, hours=hours, energy=energy_kwh, cost=cost, tip=tips)

@app.route('/dashboard')
def dashboard():
    usage_records = Usage.query.all()
    labels = []
    values = []
    usage_data = []

    for record in usage_records:
        appliance = Appliance.query.get(record.appliance_id)
        energy_kwh = (appliance.power * record.hours_used) / 1000
        cost = energy_kwh * 8  # ₹8 per kWh

        labels.append(appliance.name)
        values.append(round(energy_kwh, 2))

        usage_data.append({
            "appliance": appliance.name,
            "hours": record.hours_used,
            "energy": energy_kwh,
            "cost": cost
        })

    return render_template("dashboard.html", labels=labels, values=values, usage_data=usage_data)

# ---------------- Run ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Pre-load appliances if not exists
        if Appliance.query.count() == 0:
            appliances_list = [
                ("Fan", 75),
                ("LED Bulb", 10),
                ("Tube Light", 40),
                ("Television", 120),
                ("Refrigerator", 150),
                ("Air Conditioner", 1500),
                ("Washing Machine", 500),
                ("Heater", 120)
            ]
            for name, power in appliances_list:
                db.session.add(Appliance(name=name, power=power))
            db.session.commit()
    app.run(debug=True)
