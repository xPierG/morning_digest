import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

def send_digest_email(subject: str, html_content: str) -> bool:
    """
    Sends the Morning Digest email using SMTP with TLS.
    
    Args:
        subject (str): Email subject line
        html_content (str): HTML content of the email body
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    load_dotenv()
    
    # Load environment variables
    sender_email = os.getenv("EMAIL_SENDER_ADDRESS")
    sender_password = os.getenv("EMAIL_SENDER_APP_PASSWORD")
    recipient_email = os.getenv("EMAIL_RECIPIENT_ADDRESS")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    
    # Validate configuration
    if not all([sender_email, sender_password, recipient_email, smtp_server, smtp_port]):
        logger.error("Missing required email configuration in environment variables")
        return False
    
    # Validate SMTP port
    try:
        smtp_port = int(smtp_port)
    except ValueError:
        logger.error(f"Invalid SMTP_PORT value: {smtp_port}")
        return False
    
    try:
        # Create email message
        msg = MIMEText(html_content, 'html', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = formataddr((str(Header('Morning Digest AI', 'utf-8')), sender_email))
        msg['To'] = recipient_email
        
        logger.info(f"Sending email to: {recipient_email} with subject: {subject}")
        
        # Send via SMTP with TLS
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [recipient_email], msg.as_string())
            logger.info("Email sent successfully!")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        logger.error("Check EMAIL_SENDER_ADDRESS and EMAIL_SENDER_APP_PASSWORD")
        return False
    except Exception as e:
        logger.error(f"Failed to send email: {e}", exc_info=True)
        return False
