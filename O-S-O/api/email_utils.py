from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import datetime
import json
import redis
import random

# Redis connection for OTP and rate limiting
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def send_otp_email(email, otp, phone=None):
    subject = "🔐 Your Memento Verification Code"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [email]

    # Plain text fallback
    text_content = f"""
    Memento Chat Verification
    
    Your verification code is: {otp}
    
    This code will expire in 2 minutes.
    
    Phone: {phone}
    
    If you didn't request this code, please ignore this email.
    
    - Memento Team
    """

    # Beautiful HTML email
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Memento Verification</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #075E54 0%, #128C7E 50%, #25D366 100%);
                padding: 40px 20px;
                min-height: 100vh;
            }}
            
            .container {{
                max-width: 500px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            
            .header {{
                background: linear-gradient(135deg, #075E54 0%, #128C7E 100%);
                padding: 40px 30px;
                text-align: center;
                color: white;
            }}
            
            .logo {{
                font-size: 48px;
                margin-bottom: 15px;
            }}
            
            .title {{
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 8px;
                letter-spacing: -0.5px;
            }}
            
            .subtitle {{
                font-size: 16px;
                font-weight: 400;
                opacity: 0.9;
                line-height: 1.5;
            }}
            
            .content {{
                padding: 40px 30px;
                background: #ffffff;
            }}
            
            .otp-container {{
                text-align: center;
                margin: 30px 0;
            }}
            
            .otp-label {{
                font-size: 14px;
                color: #666;
                margin-bottom: 15px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .otp-code {{
                font-size: 42px;
                font-weight: 700;
                color: #075E54;
                letter-spacing: 8px;
                background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                padding: 10px;
                margin: 15px 0;
            }}
            
            .info-box {{
                background: #f8f9fa;
                border-radius: 12px;
                padding: 20px;
                margin: 25px 0;
                border-left: 4px solid #25D366;
            }}
            
            .info-item {{
                display: flex;
                align-items: center;
                margin-bottom: 8px;
                font-size: 14px;
                color: #555;
            }}
            
            .info-item:last-child {{
                margin-bottom: 0;
            }}
            
            .info-icon {{
                margin-right: 10px;
                font-size: 16px;
            }}
            
            .timer-warning {{
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                margin: 20px 0;
            }}
            
            .timer {{
                color: #e74c3c;
                font-weight: 600;
                font-size: 14px;
            }}
            
            .security-note {{
                background: #e8f5e8;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                margin: 20px 0;
                border: 1px solid #25D366;
            }}
            
            .security-text {{
                color: #27ae60;
                font-size: 13px;
                font-weight: 500;
            }}
            
            .footer {{
                background: #f8f9fa;
                padding: 25px 30px;
                text-align: center;
                border-top: 1px solid #e9ecef;
            }}
            
            .footer-text {{
                color: #666;
                font-size: 12px;
                line-height: 1.6;
            }}
            
            .button {{
                display: inline-block;
                background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
                color: white;
                padding: 14px 35px;
                text-decoration: none;
                border-radius: 25px;
                font-weight: 600;
                font-size: 15px;
                margin: 10px 0;
                border: none;
                cursor: pointer;
            }}
            
            .divider {{
                height: 1px;
                background: linear-gradient(90deg, transparent 0%, #e0e0e0 50%, transparent 100%);
                margin: 25px 0;
            }}
            
            @media (max-width: 480px) {{
                body {{
                    padding: 20px 15px;
                }}
                
                .container {{
                    border-radius: 15px;
                }}
                
                .header {{
                    padding: 30px 20px;
                }}
                
                .content {{
                    padding: 30px 20px;
                }}
                
                .otp-code {{
                    font-size: 36px;
                    letter-spacing: 6px;
                }}
                
                .title {{
                    font-size: 24px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header">
            <img src='../assets/memento_logo.png' alt="Memento Logo" width="72" height="72" style="border-radius: 20px; margin-bottom: 15px;">
                <h1 class="title">Memento Chat</h1>
                <p class="subtitle">Secure messaging with streaks & social features</p>
            </div>
            
            <!-- Content -->
            <div class="content">
                <h2 style="color: #333; text-align: center; margin-bottom: 10px; font-weight: 600;">
                    Verify Your Account
                </h2>
                <p style="color: #666; text-align: center; font-size: 15px; line-height: 1.5;">
                    Enter this verification code in the Memento app to complete your registration
                </p>
                
                <!-- OTP Code -->
                <div class="otp-container">
                    <div class="otp-label">Verification Code</div>
                    <div class="otp-code">{otp}</div>
                    <div style="color: #888; font-size: 13px; margin-top: 5px;">
                        6-digit code • Expires in 2 minutes
                    </div>
                </div>
                
                <!-- Timer Warning -->
                <div class="timer-warning">
                    <div style="font-size: 14px; color: #856404; margin-bottom: 5px;">
                        ⏰ Time Sensitive
                    </div>
                    <div class="timer">
                        This code will expire automatically for your security
                    </div>
                </div>
                
                <!-- Account Info -->
                <div class="info-box">
                    <div class="info-item">
                        <span class="info-icon">📧</span>
                        <strong>Email:</strong> {email}
                    </div>
                    {f'<div class="info-item"><span class="info-icon">📱</span><strong>Phone:</strong> {phone}</div>' if phone else ''}
                    <div class="info-item">
                        <span class="info-icon">🕐</span>
                        <strong>Requested:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    </div>
                </div>
                
                <!-- Security Note -->
                <div class="security-note">
                    <div class="security-text">
                        🔒 Your security is our priority. This code was generated for your account only.
                    </div>
                </div>
                
                <div class="divider"></div>
                
                <!-- Help Text -->
                <div style="text-align: center; color: #666; font-size: 13px; line-height: 1.6;">
                    <p>If you didn't request this code, please ignore this email or contact support if you're concerned about your account's security.</p>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <div class="footer-text">
                    <strong>Memento Chat Team</strong><br>
                    Building connections, preserving moments<br>
                    <div style="margin-top: 8px; color: #999;">
                        This is an automated message. Please do not reply to this email.
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Create and send email
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    
    # Add some headers for better email client rendering
    msg.extra_headers = {
        'X-Priority': '1',
        'X-MSMail-Priority': 'High',
        'Importance': 'High'
    }
    
    try:
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def check_rate_limit(email, max_attempts=3, window_seconds=300):
    """Check if user has exceeded rate limit for OTP requests"""
    key = f"rate_limit:{email}"
    current_count = redis_client.get(key)
    
    if current_count and int(current_count) >= max_attempts:
        return False, "Too many OTP requests. Please try again in 5 minutes."
    
    # Increment counter or set with expiry
    if current_count:
        redis_client.incr(key)
    else:
        redis_client.setex(key, window_seconds, 1)
    
    return True, None

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp_with_rate_limit(email, phone=None):
    """Main function to send OTP with rate limiting"""
    
    # Check rate limit
    allowed, error_message = check_rate_limit(email)
    if not allowed:
        return {'error': error_message}, 429
    
    # Generate OTP
    otp = generate_otp()
    
    # Store OTP in Redis (2 minutes expiry to match email)
    redis_client.setex(f'otp:{email}', 120, otp)
    
    # Store phone temporarily if provided
    if phone:
        redis_client.setex(f'phone:{email}', 120, phone)
    
    # Send email
    email_sent = send_otp_email(email, otp, phone)
    
    if email_sent:
        return {
            'message': 'OTP sent successfully',
            'rate_limit_info': {
                'max_attempts': 3,
                'window_minutes': 5,
                'otp_expiry_minutes': 2
            }
        }, 200
    else:
        return {'error': 'Failed to send OTP email'}, 500

def verify_otp(email, submitted_otp):
    """Verify the submitted OTP"""
    stored_otp = redis_client.get(f'otp:{email}')
    
    if not stored_otp:
        return {'error': 'OTP expired or not found'}, 400
    
    if stored_otp.decode() != submitted_otp:
        return {'error': 'Invalid OTP'}, 400
    
    # OTP is valid, delete it
    redis_client.delete(f'otp:{email}')
    redis_client.delete(f'phone:{email}')
    

    return {'message': 'OTP verified successfully'}, 200
