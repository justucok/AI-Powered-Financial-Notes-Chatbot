import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from backend.config import get_settings
except ModuleNotFoundError:
    from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def send_reset_email(to_email: str, reset_link: str) -> bool:
    """Mengirim email berisi link reset password menggunakan SMTP Gmail.
    Jika SMTP tidak dikonfigurasi, akan mencetak link ke log konsol.
    """
    if not settings.smtp_username or not settings.smtp_password:
        logger.warning("[DEMO FALLBACK] SMTP tidak dikonfigurasi. Link reset Anda:")
        logger.warning(">>> %s <<<", reset_link)
        return True

    # Setup email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Atur Ulang Kata Sandi Anda - Financial Notes Chatbot"
    msg["From"] = settings.smtp_username
    msg["To"] = to_email

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #0284c7;">Atur Ulang Kata Sandi Anda</h2>
        <p>Halo,</p>
        <p>Kami menerima permintaan untuk mengatur ulang kata sandi akun Anda. Silakan klik tombol di bawah ini untuk melanjutkan:</p>
        <p style="margin: 24px 0;">
          <a href="{reset_link}" style="background-color: #0284c7; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
            Atur Ulang Password
          </a>
        </p>
        <p>Tautan ini hanya dapat digunakan satu kali dan akan kedaluwarsa dalam 15 menit.</p>
        <p>Jika Anda tidak meminta ini, abaikan saja email ini.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin-top: 24px;">
        <p style="font-size: 12px; color: #777;">Financial Notes Chatbot AI</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(settings.smtp_username, to_email, msg.as_string())
        logger.info("Email reset password berhasil dikirim ke %s", to_email)
        return True
    except Exception as e:
        logger.error("Gagal mengirim email SMTP: %s", str(e))
        logger.warning("[FALLBACK] Link reset Anda: %s", reset_link)
        return False
