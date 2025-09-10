import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# IMPORTANT: In a production environment, set specific origins (e.g., your domain: "https://www.yourdomain.com")
CORS(app) # Enables Cross-Origin Resource Sharing

# Email configuration from environment variables
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))


@app.route('/')
def home():
    return "InGrowwth Innovations Backend is running!"

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    if request.method == 'POST':
        try:
            data = request.json

            name = data.get('name')
            email = data.get('email')
            subject = data.get('subject')
            message = data.get('message')
            # phone variable removed here

            # Basic validation
            if not all([name, email, subject, message]):
                return jsonify({'success': False, 'message': 'All required fields (Name, Email, Subject, Message) are missing.'}), 400

            # --- 1. Send Email to Company (RECEIVER_EMAIL) ---
            company_email_sent = False
            if SENDER_EMAIL and SENDER_PASSWORD and RECEIVER_EMAIL:
                msg_to_company = MIMEMultipart()
                msg_to_company['From'] = SENDER_EMAIL
                msg_to_company['To'] = RECEIVER_EMAIL
                msg_to_company['Subject'] = f"New Contact Form Submission: {subject}"

                body_to_company = f"""
                Hello InGrowwth Innovations Team,

                You have received a new message from your website contact form:

                Name: {name}
                Email: {email}
                Subject: {subject}
                Message:
                {message}

                ---
                This message was sent from your website.
                """
                msg_to_company.attach(MIMEText(body_to_company, 'plain'))

                try:
                    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                        server.starttls()
                        server.login(SENDER_EMAIL, SENDER_PASSWORD)
                        server.send_message(msg_to_company)
                    print(f"Email sent to company ({RECEIVER_EMAIL}) successfully from {email}.")
                    company_email_sent = True
                except smtplib.SMTPAuthenticationError:
                    print("SMTP Auth Error for company email. Check SENDER_EMAIL/PASSWORD.")
                except Exception as e:
                    print(f"Failed to send email to company: {e}")
            else:
                print("Company email sending skipped: SENDER_EMAIL, SENDER_PASSWORD or RECEIVER_EMAIL not configured.")
            
            # --- 2. Send Confirmation Email to Client (CLIENT'S Email) ---
            client_email_sent = False
            if SENDER_EMAIL and SENDER_PASSWORD and email: # Client email is required
                msg_to_client = MIMEMultipart()
                msg_to_client['From'] = SENDER_EMAIL
                msg_to_client['To'] = email # Send to client's email
                msg_to_client['Subject'] = f"Inquiry Received: {subject} - InGrowwth Innovations"

                body_to_client = f"""
                Dear {name},

                Thank you for contacting InGrowwth Innovations! We have successfully received your inquiry:

                Subject: {subject}
                Message:
                {message}

                We appreciate you reaching out and will review your message promptly. Our team will contact you very soon, typically within 24-48 business hours.

                In the meantime, feel free to explore more about our services on our website.

                Best regards,

                The Team at InGrowwth Innovations
                [Your Website Link, e.g., https://www.ingrowwthinnovations.com]
                [Your Phone Number, e.g., +1 (234) 567-890 - Remove this line if you don't collect phone numbers at all]
                """
                msg_to_client.attach(MIMEText(body_to_client, 'plain'))

                try:
                    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                        server.starttls()
                        server.login(SENDER_EMAIL, SENDER_PASSWORD)
                        server.send_message(msg_to_client)
                    print(f"Confirmation email sent to client ({email}) successfully.")
                    client_email_sent = True
                except Exception as e:
                    print(f"Failed to send confirmation email to client: {e}")
            else:
                print("Client confirmation email skipped: SENDER_EMAIL, SENDER_PASSWORD or client email not available.")


            # Determine overall success message
            response_message = "Your inquiry has been submitted successfully!"
            if company_email_sent and client_email_sent:
                response_message += " You'll receive a confirmation email shortly."
            elif company_email_sent:
                response_message += " We will contact you very soon."
            else:
                response_message = "Your inquiry was received, but there was an issue sending confirmation. We will contact you soon."


            return jsonify({'success': True, 'message': response_message}), 200

        except Exception as e:
            print(f"Error processing request: {e}")
            return jsonify({'success': False, 'message': f'An unexpected error occurred on the server: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)