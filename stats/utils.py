import os
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.units import mm as unit_mm
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def generate_thermal_receipt(sale):
    """
    Generates a thermal receipt PDF (80mm width) for a sale.
    Includes sale details and a QR code.
    """
    buffer = BytesIO()
    
    # 80mm width, height depends on content. Let's start with 150mm.
    width = 80 * unit_mm
    height = 200 * unit_mm
    p = canvas.Canvas(buffer, pagesize=(width, height))
    
    # Start drawing from top
    curr_y = height - 10 * unit_mm
    
    # Header
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width / 2, curr_y, "STORE - SMART BOSHQARUV")
    curr_y -= 6 * unit_mm
    
    p.setFont("Helvetica", 8)
    p.drawCentredString(width / 2, curr_y, f"Filial: {sale.branch.name}")
    curr_y -= 8 * unit_mm
    
    p.line(5 * unit_mm, curr_y, width - 5 * unit_mm, curr_y)
    curr_y -= 6 * unit_mm
    
    # Sale Info
    p.setFont("Helvetica-Bold", 9)
    p.drawString(10 * unit_mm, curr_y, f"ID: #{sale.id}")
    p.drawRightString(width - 10 * unit_mm, curr_y, f"Sana: {sale.created_at}")
    curr_y -= 10 * unit_mm
    
    p.setFont("Helvetica", 9)
    p.drawString(10 * unit_mm, curr_y, f"Mijoz: {sale.client.name}")
    curr_y -= 6 * unit_mm
    p.drawString(10 * unit_mm, curr_y, f"Xodim: {sale.user.first_name}")
    curr_y -= 10 * unit_mm
    
    # Items Table Header
    p.line(10 * unit_mm, curr_y, width - 10 * unit_mm, curr_y)
    curr_y -= 5 * unit_mm
    p.setFont("Helvetica-Bold", 8)
    p.drawString(10 * unit_mm, curr_y, "MAHSULOT")
    p.drawRightString(width - 10 * unit_mm, curr_y, "SMI/NARX")
    curr_y -= 5 * unit_mm
    p.line(10 * unit_mm, curr_y, width - 10 * unit_mm, curr_y)
    curr_y -= 6 * unit_mm
    
    # Item row
    p.setFont("Helvetica", 8)
    p.drawString(10 * unit_mm, curr_y, sale.product.name[:30])
    p.drawRightString(width - 10 * unit_mm, curr_y, f"{sale.quantity} x {int(sale.product.price):,}")
    curr_y -= 10 * unit_mm
    
    p.line(10 * unit_mm, curr_y, width - 10 * unit_mm, curr_y)
    curr_y -= 8 * unit_mm
    
    # Totals
    p.setFont("Helvetica-Bold", 10)
    p.drawString(10 * unit_mm, curr_y, "JAMI:")
    p.drawRightString(width - 10 * unit_mm, curr_y, f"{int(sale.total_price):,} so'm")
    curr_y -= 6 * unit_mm
    
    p.setFont("Helvetica", 9)
    p.drawString(10 * unit_mm, curr_y, "To'landi:")
    p.drawRightString(width - 10 * unit_mm, curr_y, f"{int(sale.paid_price):,} so'm")
    curr_y -= 5 * unit_mm
    
    if sale.debt_price > 0:
        p.setFont("Helvetica-Bold", 9)
        p.drawString(10 * unit_mm, curr_y, "Qarz:")
        p.drawRightString(width - 10 * unit_mm, curr_y, f"{int(sale.debt_price):,} so'm")
        curr_y -= 10 * unit_mm
    else:
        curr_y -= 5 * unit_mm
        
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(width / 2, curr_y, "Xaridingiz uchun rahmat!")
    curr_y -= 15 * unit_mm
    
    # QR Code
    qr = qrcode.QRCode(version=1, box_size=3, border=1)
    qr_data = f"SaleID: {sale.id} | Amount: {sale.total_price} | Branch: {sale.branch.name}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR to a temporary path or handle in memory
    qr_buffer = BytesIO()
    img_qr.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    from reportlab.lib.utils import ImageReader
    qr_img_reader = ImageReader(qr_buffer)
    p.drawImage(qr_img_reader, (width - 30 * unit_mm) / 2, curr_y - 20 * unit_mm, width=30*unit_mm, height=30*unit_mm)
    
    curr_y -= 35 * unit_mm
    p.setFont("Helvetica", 7)
    p.drawCentredString(width / 2, curr_y, "BekMax kompaniyasi tomonidan taqdim etildi")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer
