"""
Que-Pharma Utility Functions
General purpose helpers for generating QR codes and dynamic communication links.
"""

import qrcode
import io
from django.http import HttpResponse

def produce_qr_code(url):
    """
    Generates a QR Code image as bytes for a given URL.
    Used for creating scannable physical tickets for patients.
    """
    # Initialize the QR code engine
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)

    # Generate the high-contrast image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the image to an in-memory buffer to avoid disk I/O overhead
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def get_whatsapp_link(phone, name, ticket_id):
    """
    Constructs a pre-filled WhatsApp API link for patient notifications.
    Includes the patient's name and a direct link to their tracking page.
    """
    message = f"Hello {name}, your medicine at Que-Pharma is ready! Tracking link: https://que-pharma.up.railway.app/track/{ticket_id}/"
    return f"https://wa.me/{phone}?text={message.replace(' ', '%20')}"
