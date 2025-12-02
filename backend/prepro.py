import mimetypes
import cv2
# from pdf2image import convert_from_path
# from PyPDF2 import PdfReader
import os 
import pypdfium2 as pdfium

class FileHandler:
    
    def __init__(self, filepath):
        self.filepath = filepath
    
    #ตรวจสอบนามสกุลของไฟล์เพื่อระบุว่าเป็นไฟล์ประเภทใด (PDF, Image, หรืออื่นๆ)
    def check_file_type(self):
        mime_type, _ = mimetypes.guess_type(self.filepath)  # ใช้ mimetypes เดาประเภทของไฟล์จากที่อยู่ไฟล์
        if mime_type == "application/pdf":  # ถ้าประเภทที่เดาได้คือ PDF
            return "pdf"  # คืนค่าเป็นสตริง "pdf"
        elif mime_type and mime_type.startswith("image/"):  # ถ้าประเภทที่เดาได้ขึ้นต้นด้วย "image/" (เช่น image/jpeg, image/png)
            return "image"  # คืนค่าเป็นสตริง "image"
        else:  # ถ้าไม่ใช่ทั้งสองอย่างข้างบน
            return "unknown"  # คืนค่าเป็นสตริง "unknown"
        
        # ฟังก์ชันนับหน้าจาก PDF
    # def count_pages(self):
    #     reader = PdfReader(self.filepath)
    #     return len(reader.pages)
    
    # def pdf_to_images(self, dpi=300):
    #     return convert_from_path(self.filepath, dpi=dpi)
    
    def pdf_first_page_to_image(self, output_dir="output", dpi=250):
        """
        แปลงหน้าแรกของ PDF เป็นไฟล์รูป แล้วคืน path กลับไป
        (แก้ไขให้ใช้ pypdfium2 เพื่อรองรับ Render)
        """
        os.makedirs(output_dir, exist_ok=True)

        # ✅ โค้ดใหม่: ใช้ pypdfium2 อ่าน PDF
        pdf = pdfium.PdfDocument(self.filepath)
        
        # เลือกหน้าแรก (index 0)
        page = pdf[0]
        
        # คำนวณ scale เพื่อให้ได้ DPI ตามต้องการ (Default PDF คือ 72 dpi)
        scale = dpi / 72
        
        # Render เป็นภาพ
        bitmap = page.render(scale=scale)
        pil_image = bitmap.to_pil()
        
        # บันทึกไฟล์
        img_path = os.path.join(output_dir, "page1_from_pdf.jpg")
        pil_image.save(img_path, "JPEG")
        
        # ปิดไฟล์ PDF เพื่อคืน Ram
        pdf.close() 
        
        return img_path
    
class ImageProcessor:
    
    @staticmethod
    def preprocess_image(input_path, output_path):
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"❌ ไม่สามารถโหลดภาพจาก: {input_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Resize 2x (Upscale)
        # resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        resized = gray

        # Adaptive Threshold
        thresh = cv2.adaptiveThreshold(
            resized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Invert image
        inverted = cv2.bitwise_not(thresh)

        # Save result
        cv2.imwrite(output_path, inverted)