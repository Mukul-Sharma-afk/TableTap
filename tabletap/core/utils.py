import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
from django.conf import settings


def generate_qr_code(table):

    # Part of the business logic to generate QR codes for tables so that customers can scan them

    data = f"https://{settings.ALLOWED_HOSTS[0]}/tabletap/menu/{table.id}/"

    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    filename = f"qr_codes/qr_table_{table.id}.png"
    table.qr_code.save(filename, ContentFile(buffer.getvalue()), save=True)
