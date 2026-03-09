import qrcode
import io
from django.http import HttpResponse

def produce_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def get_whatsapp_link(phone, name, ticket_id):
    message = f"Hello {name}, your medicine at Que-Pharma is ready! Tracking link: https://que-pharma.up.railway.app/track/{ticket_id}/"
    return f"https://wa.me/{phone}?text={message.replace(' ', '%20')}"
