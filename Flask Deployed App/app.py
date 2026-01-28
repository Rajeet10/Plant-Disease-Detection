import os
import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# ==============================
# LOAD CSV FILES
# ==============================
disease_info = pd.read_csv("disease_info.csv", encoding="cp1252")
supplement_info = pd.read_csv("supplement_info.csv", encoding="cp1252")

# ==============================
# LOAD YOUR KERAS MODEL
# ==============================
MODEL_PATH = "plant_disease_model.h5"   # your saved model
IMG_SIZE = (180, 180)                   # training size

model = load_model(MODEL_PATH)


# ==============================
# PREDICTION FUNCTION
# ==============================
def prediction(image_path: str) -> int:
    """
    Load image, resize to 180x180, feed into model, return class index (0..38).
    IMPORTANT: your model already has layers.Rescaling(1./255),
    so here we pass raw 0–255 RGB values (no extra /255).
    """
    img = image.load_img(image_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)            # (180, 180, 3)
    img_array = np.expand_dims(img_array, axis=0)  # (1, 180, 180, 3)

    preds = model.predict(img_array)               # (1, 39)
    index = int(np.argmax(preds[0]))
    return index


# ==============================
# FLASK SETUP
# ==============================
app = Flask(__name__)

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ==============================
# ROUTES
# ==============================
@app.route("/")
def home_page():
    return render_template("home.html")


@app.route("/contact")
def contact():
    return render_template("contact-us.html")


@app.route("/index")
def ai_engine_page():
    return render_template("index.html")


@app.route("/mobile-device")
def mobile_device_detected_page():
    return render_template("mobile-device.html")


@app.route("/submit", methods=["POST"])
def submit():
    # file input name in index.html is "image"
    image_file = request.files["image"]
    filename = image_file.filename

    # Save uploaded image to static/uploads
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image_file.save(file_path)

    # Predict class index
    pred = prediction(file_path)

    # Get info from CSV (same index)
    title = disease_info["disease_name"][pred]
    desc = disease_info["description"][pred]
    prevent = disease_info["Possible Steps"][pred]
    image_url = disease_info["image_url"][pred]

    sname = supplement_info["supplement name"][pred]
    simage = supplement_info["supplement image"][pred]
    buy_link = supplement_info["buy link"][pred]

    # Render result page
    return render_template(
        "submit.html",
        title=title,
        desc=desc,
        prevent=prevent,
        pred=pred,
        image_url=image_url,
        sname=sname,
        simage=simage,
        buy_link=buy_link,
    )


@app.route("/market")
def market():
    return render_template(
        "market.html",
        supplement_image=list(supplement_info["supplement image"]),
        supplement_name=list(supplement_info["supplement name"]),
        disease=list(disease_info["disease_name"]),
        buy=list(supplement_info["buy link"]),
    )


if __name__ == "__main__":
    app.run(debug=True)
