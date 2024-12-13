from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps
import random
from firebase_admin import credentials, initialize_app, firestore
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import os

app = Flask(__name__)

cred = credentials.Certificate("/Users/dianmaheru/Documents/be_budaya/budayakita-690e5dcb36ab.json")
initialize_app(cred, {"projectId": "budayakita"})
db = firestore.Client(database="budayakitadb")

SECRET_KEY = "secret_key_jwt"

OTP_EXPIRATION = 300

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "budayakita18@gmail.com"
EMAIL_PASSWORD = "cxlc dhyn zmwf nhmb"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token tidak ditemukan"}), 403

        try:
            if token.startswith("Bearer "):
                token = token.split(" ")[1]

            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = db.collection("users").document(data["email"]).get()
            if not current_user.exists:
                raise Exception("User tidak ditemukan")
        except Exception as e:
            return jsonify({"error": "Token tidak valid", "message": str(e)}), 403

        return f(current_user.to_dict(), *args, **kwargs)
    return decorated

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def send_email(to_email, subject, body):
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_ADDRESS
        message["To"] = to_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, message.as_string())
        print(f"Email berhasil dikirim ke {to_email}")
    except Exception as e:
        print(f"Error saat mengirim email: {str(e)}")

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    full_name = data.get('full_name')
    password = data.get('password')

    if not email or not full_name or not password:
        return jsonify({"error": "Semua data harus diisi"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Format email tidak valid"}), 400

    user_ref = db.collection("users").document(email)
    if user_ref.get().exists:
        return jsonify({"error": "Email sudah terdaftar"}), 400

    otp = random.randint(100000, 999999)

    db.collection("temp_registrations").document(email).set({
        "email": email,
        "full_name": full_name,
        "password": password,
        "otp": otp,
        "otp_created_at": datetime.datetime.utcnow().isoformat()
    })

    subject = "OTP Anda untuk Registrasi"
    body = f"Halo {full_name},\n\nKode OTP Anda adalah {otp}. Kode ini berlaku selama {OTP_EXPIRATION // 60} menit.\n\nTerima kasih."
    send_email(email, subject, body)

    return jsonify({"message": "OTP telah dikirim ke email"}), 200

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        return jsonify({"error": "Email dan OTP harus diisi"}), 400

    temp_user_ref = db.collection("temp_registrations").document(email)
    temp_user = temp_user_ref.get()
    if not temp_user.exists:
        return jsonify({"error": "OTP tidak valid atau kadaluarsa"}), 400

    temp_user_data = temp_user.to_dict()
    otp_created_at = datetime.datetime.fromisoformat(temp_user_data["otp_created_at"])

    if (datetime.datetime.utcnow() - otp_created_at).total_seconds() > OTP_EXPIRATION:
        temp_user_ref.delete()
        return jsonify({"error": "OTP telah kadaluarsa"}), 400

    if str(temp_user_data["otp"]) != str(otp):
        return jsonify({"error": "OTP tidak valid"}), 400

    db.collection("users").document(email).set({
        "email": email,
        "password": temp_user_data["password"],
        "full_name": temp_user_data["full_name"],
        "created_at": datetime.datetime.utcnow().isoformat()
    })
    temp_user_ref.delete()

    return jsonify({"message": "Akun berhasil dibuat"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email dan password harus diisi"}), 400

    user_ref = db.collection("users").document(email)
    user = user_ref.get()

    if not user.exists:
        return jsonify({"error": "User tidak ditemukan"}), 404

    user_data = user.to_dict()

    if user_data["password"] != password:
        return jsonify({"error": "Password salah"}), 401

    token = jwt.encode({
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"message": "Login berhasil", "token": token}), 200


@app.route('/getall_budaya', methods=['GET'])
def get_all_budaya():
    try:
        batik_ref = db.collection('batik_collection')
        batik_docs = batik_ref.stream()

        results = []
        for doc in batik_docs:
            data = doc.to_dict()
            results.append({
                'label': data.get('label'),
                'description': data.get('description'),
                'image_url': data.get('file_path'),
            })

        # Jika tidak ada data
        if not results:
            return jsonify({"message": "No data found"}), 404

        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/details', methods=['GET'])
def get_label_details():
    try:
        # Ambil parameter file_name dari query string
        file_name = request.args.get('file_name', '').lower()

        if not file_name:
            return jsonify({"error": "Parameter 'file_name' is required"}), 400

        # Query Firestore berdasarkan file_name
        collection_name = "batik_collection"
        batik_ref = db.collection(collection_name)
        query = batik_ref.stream()
        details = None
        for doc in query:
            data = doc.to_dict()
            if data.get('file_name', '').lower() == file_name:
                details = data
                break

        # Jika data tidak ditemukan
        if not details:
            return jsonify({"message": f"No details found for the file name '{file_name}'"}), 404

        # Kembalikan data label, deskripsi, dan URL gambar
        return jsonify({
            "label": details.get('label'),
            "description": details.get('description'),
            "image_url": details.get('file_path')
        }), 200
    except Exception as e:
        # Tangani error dan tampilkan pesan error
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  
    app.run(host="0.0.0.0", port=port)
