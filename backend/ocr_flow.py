import re
import os
from typhoon_ocr import ocr_document
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader
from collections import defaultdict
from prepro import ImageProcessor

class OCRService:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            api_key="TYPHOON_OCR_API_KEY",
            base_url="base_url_typhoon"
        )

    def run_ocr(self, image_path):
        return ocr_document(
            pdf_or_image_path=image_path,
            task_type="default",
            page_num=1
        )
        
class TransactionExtractor:
    def __init__(self, ocr_service, output_dir="output", dpi=300):
        self.ocr_service = ocr_service
        self.data = defaultdict(list)
        self.output_dir = output_dir
        self.dpi = dpi
        os.makedirs(self.output_dir, exist_ok=True)

    # def process_document(self, file_handler):
    #     file_type = file_handler.check_file_type()

    #     # if file_type == "pdf":
    #     #     images = file_handler.pdf_to_images(dpi=self.dpi)
    #     # elif file_type == "image":
    #     #     images = [file_handler.filepath]
    #     # else:
    #     #     raise ValueError("ไฟล์ไม่รองรับ")
    #     # print(images)
        
    #     if file_type == "pdf":
    #     # ✅ ใช้หน้าแรกของ PDF แปลงเป็นรูป แล้วใส่ลง list
    #         first_image = file_handler.pdf_first_page_to_image(
    #             output_dir=self.output_dir,
    #             dpi=self.dpi
    #         )
    #         images = [first_image]

    #     elif file_type == "image":
    #         # รูปธรรมดา ก็ใส่เป็น list 1 รูป
    #         images = [file_handler.filepath]

    #     else:
    #         return {"ok": False, "error": "ไม่รองรับไฟล์นี้"}
        
    #     print(images)

    def process_document(self, file_handler):
        file_type = file_handler.check_file_type()

        # รองรับเฉพาะ pdf กับ image
        if file_type not in ("pdf", "image"):
            return {"ok": False, "error": "ไม่รองรับไฟล์นี้"}

        self.data.clear()

        try:
            # ---------- กรณี PDF ----------
            if file_type == "pdf":
                try:
                    # 1) แปลง "หน้าแรก" ของ PDF เป็นรูป
                    base_image = file_handler.pdf_first_page_to_image(
                        output_dir=self.output_dir,
                        dpi=self.dpi  # 300 ตาม __init__
                    )

                    # 2) preprocess รูปให้คมขึ้น (ขาวดำ + ขยาย + adaptive)
                    pre_path = os.path.join(
                        self.output_dir,
                        f"pre_{os.path.basename(base_image)}"
                    )
                    ImageProcessor.preprocess_image(base_image, pre_path)

                    ocr_input = pre_path
                    print(f">>> PDF mode: use preprocessed image {ocr_input}")

                except Exception as e:
                    # ถ้าแปลง PDF → รูป ไม่ได้บน Render (เช่น poppler ไม่มี)
                    print(f"⚠️ แปลง PDF เป็นรูปไม่สำเร็จ, fallback ส่งไฟล์ PDF ตรง ๆ: {e}")
                    ocr_input = file_handler.filepath  # อย่างน้อยยังอ่านได้

            # ---------- กรณี IMAGE ----------
            else:  # file_type == "image"
                input_path = file_handler.filepath
                pre_path = os.path.join(
                    self.output_dir,
                    f"pre_{os.path.basename(input_path)}"
                )
                # ทำขาวดำ + ขยาย + adaptive threshold ตาม class ImageProcessor ที่มึงให้มา
                ImageProcessor.preprocess_image(input_path, pre_path)
                ocr_input = pre_path
                print(f">>> IMAGE mode: use preprocessed image {ocr_input}")

            # ---------- เรียก Typhoon OCR ----------
            markdown = self.ocr_service.run_ocr(ocr_input)

            # เก็บผลไว้ใน page_1 (ตอนนี้ทำทีละหน้าเดียว)
            self.data["page_1"].append(markdown)

        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดขณะ OCR: {e}")
            return {"ok": False, "error": f"OCR error: {e}"}

        return self.data


        

        # for i, img in enumerate(images):
        #     try:
        #         if file_type == "pdf":
        #             img_path = os.path.join(
        #                 self.output_dir,
        #                 f"{os.path.splitext(os.path.basename(file_handler.filepath))[0]}_page_{i+1}.png"
        #             )
        #             img.save(img_path, "PNG")                     
        #         else:
        #             ext = os.path.splitext(file_handler.filepath)[1].lower()
        #             img_path = os.path.join(
        #                 self.output_dir,
        #                 f"{os.path.splitext(os.path.basename(file_handler.filepath))[0]}{ext}"
        #             )
        #             if file_handler.filepath != img_path:
        #                 import shutil
        #                 shutil.copy(file_handler.filepath, img_path)

                    

        #         ImageProcessor.preprocess_image(img_path, img_path)
        #         markdown = self.ocr_service.run_ocr(img_path)
        #     #    # --- ย้ายการพิมพ์มาไว้ตรงนี้ ---
        #     #     # พิมพ์ผลลัพธ์หลังจากที่ try ทำงานสำเร็จ
        #     #     print(f"--- OCR Result for Page {i+1} ---")
        #     #     print(markdown)
        #     #     print("---------------------------------")
                
        #     #     # (สำคัญ) ถึงแม้เราจะยังไม่ประมวลผลต่อ
        #     #     # เราควรจะเก็บผลลัพธ์ไว้ใน self.data ก่อน
        #     #     # เพื่อให้ฟังก์ชันคืนค่าที่ถูกต้องกลับไป
        #     #     # อาจจะใช้เลขหน้าเป็น Key ชั่วคราว
        #         self.data[f"page_{i+1}"].append(markdown)


        #     # ใช้ except ไว้สำหรับแจ้ง Error เท่านั้น
        #     except Exception as e:
        #         print(f"❌ เกิดข้อผิดพลาดร้ายแรงขณะประมวลผลหน้า {i+1}: {e}")
        #         # traceback.print_exc() # หากต้องการดูรายละเอียด Error แบบเต็ม ให้ import traceback แล้วเปิดใช้บรรทัดนี้

        # # คืนค่า self.data ตามโครงสร้างเดิม
        # return self.data