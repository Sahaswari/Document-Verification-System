"""
PDF Certificate Generator for G.C.E O/L and A/L Certificates
Sri Lanka Department of Examinations Standard Format
"""
import os
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
import hashlib

# Try to import pdf2image for PNG generation
try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("Warning: pdf2image not available. PNG generation disabled.")


class CertificatePDFGenerator:
    """Generate official G.C.E certificates in PDF format"""
    
    def __init__(self, output_dir: str = "certificates"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for certificate"""
        self.styles.add(ParagraphStyle(
            name='CertTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a365d')
        ))
        
        self.styles.add(ParagraphStyle(
            name='CertSubTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2c5282')
        ))
        
        self.styles.add(ParagraphStyle(
            name='CertBody',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CertInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=4,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CertSmall',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            spaceAfter=2,
            fontName='Helvetica',
            textColor=colors.HexColor('#4a5568')
        ))
    
    def generate_certificate(
        self,
        student_data: dict,
        result_data: dict,
        certificate_data: dict
    ) -> tuple:
        """
        Generate G.C.E Certificate PDF and PNG image
        Returns: (pdf_bytes, document_hash, filepath, image_hash, image_path)
        """
        exam_type = result_data.get('exam_type', 'OL')
        exam_year = result_data.get('exam_year', datetime.now().year)
        index_number = student_data.get('index_number', '')
        
        filename = f"GCE_{exam_type}_{exam_year}_{index_number}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF buffer
        buffer = BytesIO()
        
        # Create canvas
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Draw certificate content
        self._draw_header(c, width, height, exam_type)
        self._draw_student_info(c, width, height, student_data, result_data)
        self._draw_results_table(c, width, height, result_data)
        self._draw_footer(c, width, height, certificate_data)
        self._draw_qr_code(c, width, height, certificate_data)
        self._draw_security_features(c, width, height, certificate_data)
        
        c.save()
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Calculate PDF document hash
        document_hash = hashlib.sha256(pdf_bytes).hexdigest()
        
        # Save PDF to file
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)
        
        # Generate PNG image and calculate its hash
        image_hash = None
        image_path = None
        
        if PDF2IMAGE_AVAILABLE:
            try:
                image_hash, image_path = self._generate_certificate_image(
                    pdf_bytes, exam_type, exam_year, index_number
                )
            except Exception as e:
                print(f"Warning: Failed to generate PNG image: {e}")
        
        return pdf_bytes, document_hash, filepath, image_hash, image_path
    
    def _generate_certificate_image(self, pdf_bytes: bytes, exam_type: str, 
                                    exam_year: int, index_number: str) -> tuple:
        """
        Convert PDF to PNG image and calculate hash
        Returns: (image_hash, image_path)
        """
        # Convert PDF to image (300 DPI for high quality)
        images = convert_from_bytes(pdf_bytes, dpi=300)
        
        if not images:
            return None, None
        
        # Get the first page (certificate is single page)
        img = images[0]
        
        # Generate filename
        image_filename = f"GCE_{exam_type}_{exam_year}_{index_number}.png"
        image_path = os.path.join(self.output_dir, image_filename)
        
        # Save image to bytes for hashing
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG', optimize=True)
        img_bytes = img_buffer.getvalue()
        img_buffer.close()
        
        # Calculate image hash
        image_hash = hashlib.sha256(img_bytes).hexdigest()
        
        # Save image to file
        with open(image_path, 'wb') as f:
            f.write(img_bytes)
        
        return image_hash, image_path
        
        # Save to file
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)
        
        return pdf_bytes, document_hash, filepath
    
    def _draw_header(self, c, width, height, exam_type):
        """Draw certificate header with government emblem and titles"""
        # Background color for header
        c.setFillColor(colors.HexColor('#f7fafc'))
        c.rect(0, height - 180, width, 180, fill=True, stroke=False)
        
        # Sri Lanka Government Header
        c.setFillColor(colors.HexColor('#1a365d'))
        c.setFont('Helvetica-Bold', 12)
        c.drawCentredString(width/2, height - 40, "ශ්‍රී ලංකා ප්‍රජාතාන්ත්‍රික සමාජවාදී ජනරජය")
        
        c.setFont('Helvetica-Bold', 11)
        c.drawCentredString(width/2, height - 55, "DEMOCRATIC SOCIALIST REPUBLIC OF SRI LANKA")
        
        # Department of Examinations
        c.setFont('Helvetica-Bold', 14)
        c.setFillColor(colors.HexColor('#2c5282'))
        c.drawCentredString(width/2, height - 80, "DEPARTMENT OF EXAMINATIONS")
        
        c.setFont('Helvetica', 10)
        c.setFillColor(colors.HexColor('#4a5568'))
        c.drawCentredString(width/2, height - 95, "විභාග දෙපාර්තමේන්තුව | தேர்வுத் திணைக்களம்")
        
        # Certificate Title
        c.setFillColor(colors.HexColor('#1a365d'))
        c.setFont('Helvetica-Bold', 16)
        
        if exam_type == "OL":
            title = "G.C.E. ORDINARY LEVEL EXAMINATION"
            title_si = "අ.පො.ස. සාමාන්‍ය පෙළ විභාගය"
        else:
            title = "G.C.E. ADVANCED LEVEL EXAMINATION"
            title_si = "අ.පො.ස. උසස් පෙළ විභාගය"
        
        c.drawCentredString(width/2, height - 125, title)
        c.setFont('Helvetica', 11)
        c.drawCentredString(width/2, height - 142, title_si)
        
        # Statement of Results
        c.setFont('Helvetica-Bold', 13)
        c.setFillColor(colors.HexColor('#c53030'))
        c.drawCentredString(width/2, height - 165, "STATEMENT OF RESULTS")
        
        # Decorative line
        c.setStrokeColor(colors.HexColor('#2c5282'))
        c.setLineWidth(2)
        c.line(50, height - 175, width - 50, height - 175)
    
    def _draw_student_info(self, c, width, height, student_data, result_data):
        """Draw student information section"""
        y_start = height - 210
        left_margin = 60
        
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(colors.HexColor('#1a365d'))
        
        # Info pairs
        info_items = [
            ("Index Number / අංක අංකය:", student_data.get('index_number', 'N/A')),
            ("Name / නම:", student_data.get('full_name', 'N/A')),
            ("NIC Number / ජා.හැ.අ:", student_data.get('nic_number', 'N/A')),
            ("School / පාසල:", student_data.get('school_name', 'N/A')),
            ("District / දිස්ත්‍රික්කය:", student_data.get('district', 'N/A')),
            ("Examination Year / විභාග වර්ෂය:", str(result_data.get('exam_year', 'N/A'))),
            ("Medium / මාධ්‍යය:", student_data.get('medium', 'Sinhala')),
        ]
        
        if result_data.get('exam_type') == 'AL' and result_data.get('stream'):
            info_items.append(("Stream / විෂය ධාරාව:", result_data.get('stream', 'N/A')))
        
        y = y_start
        for label, value in info_items:
            c.setFont('Helvetica-Bold', 9)
            c.setFillColor(colors.HexColor('#4a5568'))
            c.drawString(left_margin, y, label)
            
            c.setFont('Helvetica', 10)
            c.setFillColor(colors.HexColor('#1a365d'))
            c.drawString(left_margin + 160, y, str(value))
            y -= 16
    
    def _draw_results_table(self, c, width, height, result_data):
        """Draw examination results table"""
        y_start = height - 380
        
        # Table header
        c.setFont('Helvetica-Bold', 11)
        c.setFillColor(colors.HexColor('#1a365d'))
        c.drawCentredString(width/2, y_start + 20, "EXAMINATION RESULTS")
        
        # Prepare table data
        subjects = result_data.get('subjects', [])
        table_data = [['No.', 'Subject Code', 'Subject Name', 'Grade']]
        
        for i, subject in enumerate(subjects, 1):
            table_data.append([
                str(i),
                subject.get('subject_code', ''),
                subject.get('subject_name', ''),
                subject.get('grade', '')
            ])
        
        # Create table
        col_widths = [30, 80, 250, 60]
        table = Table(table_data, colWidths=col_widths)
        
        # Style table
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        # Calculate table position
        table_width = sum(col_widths)
        table_x = (width - table_width) / 2
        table_height = len(table_data) * 20 + 10
        
        table.wrapOn(c, width, height)
        table.drawOn(c, table_x, y_start - table_height)
        
        # Summary
        y_summary = y_start - table_height - 30
        passes = sum(1 for s in subjects if s.get('grade') in ['A', 'B', 'C', 'S'])
        
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(colors.HexColor('#1a365d'))
        c.drawString(60, y_summary, f"Total Subjects: {len(subjects)}")
        c.drawString(200, y_summary, f"Passes: {passes}")
        
        if result_data.get('exam_type') == 'AL':
            if result_data.get('z_score'):
                c.drawString(300, y_summary, f"Z-Score: {result_data.get('z_score'):.4f}")
            if result_data.get('district_rank'):
                c.drawString(60, y_summary - 15, f"District Rank: {result_data.get('district_rank')}")
            if result_data.get('island_rank'):
                c.drawString(200, y_summary - 15, f"Island Rank: {result_data.get('island_rank')}")
    
    def _draw_footer(self, c, width, height, certificate_data):
        """Draw certificate footer with authentication"""
        y_start = 150
        
        # Certification statement
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.HexColor('#4a5568'))
        c.drawCentredString(width/2, y_start, 
            "This is to certify that the above results are authentic and have been")
        c.drawCentredString(width/2, y_start - 12, 
            "verified by the Department of Examinations, Sri Lanka.")
        
        # Signature section
        c.setStrokeColor(colors.HexColor('#2c5282'))
        c.line(60, y_start - 60, 200, y_start - 60)
        c.line(width - 200, y_start - 60, width - 60, y_start - 60)
        
        c.setFont('Helvetica', 8)
        c.drawCentredString(130, y_start - 72, "Authorized Signatory")
        c.drawCentredString(width - 130, y_start - 72, "Commissioner of Examinations")
        
        # Issue date
        c.setFont('Helvetica', 8)
        issued_at = certificate_data.get('issued_at', datetime.now().isoformat())
        if isinstance(issued_at, str):
            try:
                issued_date = datetime.fromisoformat(issued_at).strftime("%d %B %Y")
            except:
                issued_date = issued_at
        else:
            issued_date = issued_at.strftime("%d %B %Y")
        
        c.drawCentredString(width/2, y_start - 90, f"Issued on: {issued_date}")
        
        # Certificate ID and verification code
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(colors.HexColor('#c53030'))
        verification_code = certificate_data.get('verification_code', 'PENDING')
        c.drawCentredString(width/2, y_start - 105, f"Verification Code: {verification_code}")
    
    def _draw_qr_code(self, c, width, height, certificate_data):
        """Draw QR code for verification"""
        qr_data = f"https://verify.doenets.lk/cert/{certificate_data.get('certificate_id', '')}"
        
        # Create QR code
        qr_code = qr.QrCodeWidget(qr_data)
        qr_code.barWidth = 80
        qr_code.barHeight = 80
        
        d = Drawing(90, 90)
        d.add(qr_code)
        
        renderPDF.draw(d, c, width - 110, 30)
        
        c.setFont('Helvetica', 6)
        c.setFillColor(colors.HexColor('#4a5568'))
        c.drawCentredString(width - 65, 25, "Scan to Verify")
    
    def _draw_security_features(self, c, width, height, certificate_data):
        """Draw security features (borders and hash)"""
        # Document hash (bottom)
        c.setFont('Helvetica', 6)
        c.setFillColor(colors.HexColor('#a0aec0'))
        doc_hash = certificate_data.get('document_hash', 'Hash not generated')
        c.drawCentredString(width/2, 15, f"Document Hash: {doc_hash}")
        
        # Border
        c.setStrokeColor(colors.HexColor('#2c5282'))
        c.setLineWidth(3)
        c.rect(20, 20, width - 40, height - 40, fill=False, stroke=True)
        
        c.setStrokeColor(colors.HexColor('#c53030'))
        c.setLineWidth(1)
        c.rect(25, 25, width - 50, height - 50, fill=False, stroke=True)
