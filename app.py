from flask import Flask, render_template, request, jsonify
import mysql.connector
import random
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)

# ----------------- DB Connection -----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="new_schema"
)
cursor = db.cursor(dictionary=True)

# ----------------- Load ML Model -----------------
with open("stacked_meta_model.pkl", "rb") as f:
    model = pickle.load(f)

# ----------------- Routes -----------------
@app.route("/")
def home():
    return render_template("index.html")  # Your homepage

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "fill":
            # Fetch a random row from inputs table
            cursor.execute("SELECT * FROM inputs ORDER BY RAND() LIMIT 1")
            row = cursor.fetchone()
            return jsonify(row)

        elif action == "predict":
            # Collect form inputs
            inputs = []
            for i in range(1, 56):  # 55 properties
                val = request.form.get(f"property{i}")
                inputs.append(float(val))

            inputs = np.array(inputs).reshape(1, -1)

            # Store input in DB
            insert_query = "INSERT INTO inputs (" + ",".join([f"Property{i}" for i in range(1, 56)]) + ") VALUES (" + ",".join(["%s"]*55) + ")"
            cursor.execute(insert_query, tuple(inputs.flatten().tolist()))
            db.commit()
            input_id = cursor.lastrowid

            # Predict outputs
            preds = model.predict(inputs)
            preds = preds.flatten()

            # Round to 3 decimals for neatness
            preds = np.round(preds, 3)

            # Store outputs in DB
            output_query = "INSERT INTO outputs (id," + ",".join([f"BlendProperty{i}" for i in range(1, 11)]) + ") VALUES (" + ",".join(["%s"]*11) + ")"
            cursor.execute(output_query, (input_id, *preds.tolist()))
            db.commit()

            # Return JSON for frontend
            return jsonify({
                "status": "success",
                "predictions": {f"BlendProperty{i+1}": preds[i] for i in range(10)}
            })

    return render_template("predict.html")  # The prediction form page

@app.route("/predict", methods=["POST"])
def predict():
    # Collect inputs from form (55 values)
    input_data = [float(request.form[f"property{i}"]) for i in range(1, 56)]
    
    # Reshape for model
    input_array = np.array(input_data).reshape(1, -1)
    
    # Predict blend properties
    preds = model.predict(input_array)[0]   # preds is 10 values
    
    # Insert into outputs table
    cursor = db.cursor()
    sql = """
        INSERT INTO outputs (
            BlendProperty1, BlendProperty2, BlendProperty3, BlendProperty4, BlendProperty5,
            BlendProperty6, BlendProperty7, BlendProperty8, BlendProperty9, BlendProperty10
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, tuple(preds))
    db.commit()
    
    return render_template("predict.html", prediction=preds)

if __name__ == "__main__":
    app.run(debug=True)
