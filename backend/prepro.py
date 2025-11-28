import mimetypes
import cv2
from pdf2image import convert_from_path
from PyPDF2 import PdfReader

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
    def count_pages(self):
        reader = PdfReader(self.filepath)
        return len(reader.pages)
    
    def pdf_to_images(self, dpi=300):
        return convert_from_path(self.filepath, dpi=dpi)
    
class ImageProcessor:
    
    @staticmethod
    def preprocess_image(input_path, output_path):
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"❌ ไม่สามารถโหลดภาพจาก: {input_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Resize 2x (Upscale)
        resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Adaptive Threshold
        thresh = cv2.adaptiveThreshold(
            resized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Invert image
        inverted = cv2.bitwise_not(thresh)

        # Save result
        cv2.imwrite(output_path, inverted)