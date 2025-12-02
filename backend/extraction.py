import os, re, json
from openai import OpenAI
from dotenv import load_dotenv
from json.decoder import JSONDecodeError
from google import genai


class InvoiceExtractor:
    def __init__(self, markdown):
        load_dotenv()
        self.client = OpenAI(
            api_key= os.getenv("TYPHOON_OCR_API_KEY"),
            base_url= os.getenv("base_url_typhoon")
        )
        self.markdown = markdown
        self.invoice_type = self.detect_invoice_type()  # ตรวจชนิดก่อน


        
    def detect_invoice_type(self) -> str:
        text = self.markdown
        if "ใบกำกับภาษีแบบเต็ม" in text:
            print("✅ เป็นใบภาษีแบบเต็ม")
            return "Full Invoice"
        elif "ใบกำกับภาษีแบบย่อ" in text:
            print("✅ เป็นใบกำกับภาษีแบบย่อ")
            return "Simple Invoice"
    # เพิ่มกติกาทั่วไป
        elif "ใบกำกับภาษี" in text:
            print("✅ พบคำว่า ใบกำกับภาษี (ไม่ระบุแบบเต็ม/แบบย่อ)")
            return "Invoice (unspecified)"
        elif "ใบเสร็จรับเงิน" in text or "บิลเงินสด" in text:
            print("✅ พบคำว่า ใบเสร็จรับเงิน/บิลเงินสด")
            return "Receipt"
        else:
            print("ไม่ใช่ใบภาษีแบบเต็มหรือใบกำกับภาษีแบบย่อ")
            return "Unknown"


        
    def bulid_prompt(self) -> str:
        markdown_short = self.markdown
        if len(markdown_short) > 10000:
            markdown_short = markdown_short[:10000]
    
        return f"""
    ต่อไปนี้คือข้อมูลจากใบเสร็จหรือใบกำกับภาษีที่ผ่านการทำ OCR แล้ว:

    {markdown_short}

    กรุณาวิเคราะห์ข้อความทั้งหมดและดึงข้อมูลสำคัญต่อไปนี้ออกมาในรูปแบบ JSON ห้ามมีการเปลี่ยนแปลงข้อมูลหรือเพิ่มข้อมูลใด ๆ นอกเหนือจากที่ระบุไว้ด้านล่าง:

    - "title": เป็นชื่อหัวเรื่องของเอกสาร เเละเราจะไม่เอาคำว่า ("iTAX","# iTAX") ถ้าเจอสองคำนี้เปลื่อนเป็นใบกำกับภาษี ,ให้ดึง "หัวเรื่องเต็ม" ทั้งบรรทัดบน ๆ 
    ถ้าหัวเรื่องถูกตัดเป็นหลายบรรทัดต่อกัน (เช่น "ใบคำขอหนังสือรับรองการชำระเบี้ย" และบรรทัดถัดไปคือ "ประกันสุขภาพบิดามารดา") 
    ให้ต่อข้อความทั้งหมดเข้าด้วยกันเป็นประโยคเดียว เช่น ใบคำขอหนังสือรับรองการชำระเบี้ยประกันสุขภาพบิดามารดา" ห้ามดึงมาแค่บรรทัดแรก
    - "title_tax_invoice": หัวเรื่องถ้ามีคำว่า "ใบกำกับภาษี" หรือ "ใบกำกับภาษีอย่างย่อ" หรือ "ใบกำกับภาษีแบบเต็ม" หรือ "ใบกำกับภาษี" หรือ "ใบเสร็จรับเงิน "ให้ดึงหัวข้อนี้มา (ถ้ามี)
    - "invoice_type": {self.invoice_type} ,หัวข้อนนี้ไม่ต้องเปลี่ยนแปลง ใช้ตามค่าตัวแปล
    - "seller": ชื่อผู้ขาย (ชื่อบริษัทหรือบุคคล)
    - "seller_address": ที่อยู่ผู้ขาย (แยกเป็น number(เลขที่), street(ส่วนมากจะตามหลังถนนหรืออักษรย่อ ถ.), subdistrict(ส่วนมากจะตามหลังตำบลหรืออักษรย่อ ต.), district (ส่วนมากจะตามหลังคำว่าอำเภอหรืออักษรย่อ อ.), province, postal_code)
    - "province_seller": จังหวัดของผู้ขาย (ถ้ามี)
    - "buyer": ชื่อผู้ซื้อเเละนามสุกล เเละส่วนมากหลังคำว่าลงชื่อ เเละ อยู่หลังคำว่าผู้มีเงินได้ (ต้องไม่มีคำว่ามารดาหรือบิดาอยู่ข้างหน้า)
    - "buyer_address": ที่อยู่ผู้ซื้อ (แยกเป็น number, street, subdistrict, district, province, postal_code) 
    - "tax_id_buyer": เลขประจำตัวผู้เสียภาษี หรือ เลขทะเบียนบริษัท ของผู้ซื้อ(ต้องมีครบ 13 หลัก เท่านั้น)
    - "tax_id_seller": เลขประจำตัวผู้เสียภาษี หรือ เลขทะเบียนบริษัท ของผู้ขาย (ต้องมีครบ 13 หลัก เท่านั้น) 
    - "date": วันที่ออกใบเสร็จ (แยกเป็น day month year ใช้ปี พ.ศ. เท่านั้น เเละ ค่า day จะอยู่หน้า mouth เสมอ)
    - "invoice_no": เลขที่ใบเสร็จ / เลขที่ใบกำกับ (ถ้ามี)
    - "items": รายการสินค้า (name, quantity, unit_price, total_price ต่อรายการ)
    - "vat": ภาษีมูลค่าเพิ่ม (ถ้ามี)
    - "total": ยอดรวมสุทธิทั้งหมดที่ลดหย่อนภาษีได้
    - "amount_text": จำนวนเงินตัวอักษร (เช่น "=ห้าร้อยบาทถ้วน=")
    - "warranty_period": ระยะเวลารับประกัน เอาแค่ตัวเลข(ถ้ามี)
    - "issuer_brand": คำ/โลโก้แบรนด์ที่อยู่ "ส่วนหัวกระดาษ" เช่น "iTAX","# iTAX" "LOTUS", "MAKRO" (ห้ามใส่ "ใบเสร็จรับเงิน/ใบกำกับภาษี", วันที่, เลขที่เอกสาร; ถ้าไม่มีให้เป็น null)
    - "user_year": ขออายุของผู้ซื้อ
    - "employee_name": ชื่อ–นามสกุลของลูกจ้างหรือผู้ถูกเลิกจ้าง (เช่น ชื่อในวงเล็บก่อนคำว่า "(ลูกจ้าง)" หรือชื่อที่อยู่ใกล้คำว่า "ฝ่ายลูกจ้าง" ) ถ้าเจอคำว่า(ลูกจ้าง)ตามหลังให้ใส่ชื่อที่อนยู่ข้างหน้าเลย เเละ ห้ามมีคำว่านายจ้างอยู่ใกล้ๆ
    - "ssf_deduction_amount": ถ้าเอกสารเป็นหนังสือรับรองการซื้อหน่วยลงทุนในกองทุนรวมเพื่อการออม (SSF) ให้ดึง "จำนวนเงินที่ซื้อในปีภาษี" โดยใช้หลักดังนี้: ถ้ามีแถวที่ชื่อว่า "ซื้อระหว่างปี" หรือ "เงินลงทุน" ให้ใช้จำนวนเงินในแถวนั้น
    ถ้าไม่มี ให้มองหาข้อความที่มีความหมายว่า "จำนวนเงินที่ซื้อในปีภาษี" หรือ "จำนวนเงินที่นำไปลดหย่อนภาษีได้"
    - "rmf_deduction_amount": ถ้าเอกสารเป็นหนังสือรับรองการซื้อหน่วยลงทุนในกองทุนรวมเพื่อการออม (RMF) ให้ดึง "จำนวนเงินที่ซื้อในปีภาษี" โดยใช้หลักดังนี้: ถ้ามีแถวที่ชื่อว่า "ซื้อระหว่างปี" หรือ "เงินลงทุน" ให้ใช้จำนวนเงินในแถวนั้น
    ถ้าไม่มี ให้มองหาข้อความที่มีความหมายว่า "จำนวนเงินที่ซื้อในปีภาษี" หรือ "จำนวนเงินที่นำไปลดหย่อนภาษีได้"

    หากข้อมูลบางส่วนไม่มี ให้ใส่เป็น null หรือเว้นว่างได้ เช่น "buyer": null
    หัวข้อใน JSON จะเป็นตามที่กำหนดไว้ เท่านั้น

    ตอบกลับเป็น JSON เท่านั้น โดยไม่มีคำอธิบายอื่นเพิ่มเติม
    """
       
    @staticmethod
    def _safe_json_loads(text: str) -> dict:
        try:
            return json.loads(text)
        except JSONDecodeError:
            m = re.search(r"\{.*\}", text, re.DOTALL)
            if m:
                return json.loads(m.group())
            raise
        
    def typhoon_extract(self) -> dict:
        prompt = self.bulid_prompt()
        resp = self.client.chat.completions.create(
            model="typhoon-v2.1-12b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1024,
        )
        raw = resp.choices[0].message.content

        fixed = re.sub(
            r'(?<=:\s)(\d{1,3}(?:,\d{3})+(?:\.\d+)?)(?=,|\n|\})',
            lambda m: m.group(1).replace(',', ''),
            raw
        )
        try:
            data = self._safe_json_loads(fixed)
            
        except Exception:
            data = {"_raw": raw, "_fixed": fixed, "_parse_error": True}
      

        return {"invoice_type": self.invoice_type, "raw": raw, "fixed": fixed, "json": data}

    