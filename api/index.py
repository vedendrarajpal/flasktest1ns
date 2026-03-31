from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__, template_folder='templates')
CORS(app)

# ─── Config from environment variables ───────────────────────────────────────
GMAIL_USER = os.environ.get("GMAIL_USER")   # your Gmail address
GMAIL_PASS = os.environ.get("GMAIL_PASS")   # your 16-char App Password


# ─── Routes ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/send", methods=["POST"])
def send():
    try:
        data       = request.get_json()
        name       = data.get("name", "").strip()
        email      = data.get("email", "").strip()
        phone      = data.get("phone", "").strip()
        message    = data.get("message", "").strip()

        if not all([name, email, message]):
            return jsonify({"success": False, "error": "Name, email and message are required."}), 400

        # ── Build email ──────────────────────────────────────────────────────
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Portfolio Contact: {name}"
        msg["From"]    = GMAIL_USER
        msg["To"]      = GMAIL_USER          # sends to yourself

        html_body = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:32px;background:#0d0d0d;color:#f0f0f0;border-radius:12px;">
          <h2 style="color:#c8f04d;margin-bottom:4px;">New Message from Portfolio</h2>
          <hr style="border:1px solid #2a2a2a;margin:16px 0;">
          <p><strong style="color:#888;">Name:</strong>&nbsp; {name}</p>
          <p><strong style="color:#888;">Email:</strong>&nbsp; {email}</p>
          <p><strong style="color:#888;">Phone:</strong>&nbsp; {phone if phone else '—'}</p>
          <p><strong style="color:#888;">Message:</strong></p>
          <p style="background:#1a1a1a;padding:16px;border-radius:8px;border-left:3px solid #c8f04d;">{message}</p>
        </div>
        """

        msg.attach(MIMEText(html_body, "html"))

        # ── Send via Gmail SMTP ──────────────────────────────────────────────
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())

        return jsonify({"success": True})

    except smtplib.SMTPAuthenticationError:
        return jsonify({"success": False, "error": "Gmail authentication failed. Check GMAIL_USER and GMAIL_PASS env vars."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ─── Entry point (Render uses gunicorn, this is for local dev) ────────────────
if __name__ == "__main__":
    app.run(debug=True)
