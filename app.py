import os
from flask import Flask, render_template, request, redirect
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from config import *

app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mail = Mail(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def job_form():
    if request.method == "POST":

        fullname = request.form.get("fullname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        position = request.form.get("position")
        file = request.files.get("cv")

        # Validation
        if not fullname or not email or not phone or not position:
            return "Missing required fields", 400

        if not file or not allowed_file(file.filename):
            return "Invalid file type (PDF, DOC, DOCX only)", 400

        # Save the uploaded CV
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Email to HR
        msg = Message(
            subject=f"New Job Application – {fullname}",
            sender='marwen.khalifa@etonhouse.com.sa',       # IMPORTANT
            recipients=[HR_EMAIL],
            body=f"""
A new job application has been submitted.

Full Name: {fullname}
Email: {email}
Phone: {phone}
Position Applied For: {position}

The applicant's CV is attached.
"""
        )

        # Attach the file
        with app.open_resource(filepath) as fp:
            msg.attach(filename, "application/octet-stream", fp.read())

        # Send email
        mail.send(msg)

        return redirect("/success")

    return render_template("apply.html")


@app.route("/success")
def success():
    return render_template("success.html")


# Create uploads folder if missing
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


if __name__ == "__main__":
    app.run(debug=True)
