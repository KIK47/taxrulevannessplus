from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, json, re
from database import save_upload_history

# import workflow modules
# แก้ไขบล็อก import ใน app.py
try:
    from prepro import FileHandler
    from ocr_flow import OCRService, TransactionExtractor
    from extraction import InvoiceExtractor as ex
    from predict_category import prediction
    from condition import check_condition
    WORKFLOW_AVAILABLE = True
except Exception as e: # <--- เพิ่ม as e
    print("FATAL IMPORT ERROR! Workflow disabled:", e) # <--- ตรวจสอบการดึงฟังก์ชัน
    WORKFLOW_AVAILABLE = False

APP_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.abspath(os.path.join(APP_DIR, "..", "frontend"))
UPLOAD_DIR = os.path.join(APP_DIR, "uploads")

JSON_DIR = os.path.join(APP_DIR, "json_outputs") 
os.makedirs(JSON_DIR, exist_ok=True)

print("ชื่อไฟล์ชื่อที่เข้า"+ UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# <--- การต่อหน้าบ้านเเละการสร้างโฟลเดอร์

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="/")
CORS(app)

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "landingpage.html")

# ==========================================
# เพิ่มส่วนนี้ลงไป เพื่อรับค่าจากหน้ากรอกมือ
# ==========================================
@app.route("/api/check", methods=["POST"])
def check_manual():
    try:
        data = request.json
        print("Received Manual Data:", data) # ดู log ว่าข้อมูลมาไหม

        # 1. ดึงตัวแปรที่จำเป็นสำหรับ check_condition
        user_name = data.get("buyer", "")
        net_income = float(data.get("net_income", 0))
        career = data.get("career", "employee")
        date_obj = data.get("date", {})
        # [แก้ตรงนี้] ถ้ามีปีส่งมา ให้บวก 543 เพื่อแปลงเป็น พ.ศ.
        if date_obj and "year" in date_obj:
            date_obj["year"] = int(date_obj["year"]) + 543 

        # 2. จัดเตรียมข้อมูลจำลองให้เหมือน OCR (เพื่อให้ Logic ทำงานได้)
        input_json = {
            "buyer": user_name,
            "date": date_obj,
            "total": float(data.get("total", 0)),
            "warranty_period": int(data.get("warranty_period", 0)),
            
            # ส่งค่าแยกไปเลย เดี๋ยว check_condition ไปจัดการต่อเอง
            "ssf_total": float(data.get("ssf_total", 0)),
            "rmf_total": float(data.get("rmf_total", 0)),
            
            "items": data.get("items", []),
            "sub_category": data.get("sub_category", ""),
            "category": data.get("main_category", ""),
            
            "invoice_no": data.get("invoice_no", ""),
            "tax_id_seller": data.get("tax_id_seller", ""),
            "tax_id_buyer": data.get("tax_id_buyer" ,""),
            "issuer_brand": data.get("issuer_brand" , "") ,
            "seller": data.get("seller", ""),
            
            # Mock ข้อมูลร้านค้า (เพราะกรอกมือไม่มีการเช็คกระทรวงพาณิชย์)
            "verified_seller_name": {"matched": "Manual Verified"} 
        }

        # 3. เรียก Logic ตรวจสอบ
        if WORKFLOW_AVAILABLE:
            checker = check_condition(
                input_json=input_json,
                file_name="manual_input",
                num=1,
                user_name=user_name,
                net_income=net_income,
                career=career
            )
            result = checker.check()
            return jsonify({"ok": True, "result": result})
        else:
            return jsonify({"ok": False, "error": "Workflow not available"}), 500

    except Exception as e:
        print("Manual Check Error:", e)
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/process", methods=["POST"])
def process_file():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file uploaded"}), 400

    f = request.files["file"]
    if not f or f.filename.strip() == "":
        return jsonify({"ok": False, "error": "Empty filename"}), 400
    
    # รับค่าชื่อผู้ใช้เเละรายได้สุทธิจากฟอร์ม
    user_name = (request.form.get("user_name") or "").strip()
    net_income_raw = request.form.get("net_income")
    career = request.form.get("career", "employee")
    filename = f.filename
    save_path = os.path.join(UPLOAD_DIR, filename)
    print("[DEBUG] net_income_raw from form:", repr(net_income_raw))
    print(save_path)
    f.save(save_path)

    if not WORKFLOW_AVAILABLE:
        demo = {
            "file": filename,
            "pages": {
                "1": {
                    "title": "เดโม",
                    "invoice_type": "Simple Invoice",
                    "seller": "บริษัทเดโม จำกัด",
                    "buyer": user_name or "ไม่ระบุ",
                    "tax_id": "1234567890123",
                    "date": {"day": "16", "month": "08", "year": "2568"},
                    "items": [
                        {"name": "เบี้ยประกันสุขภาพ", "category": "การออมการลงทุนและประกัน",
                         "sub_category": "เบี้ยประกันสุขภาพ", "deduction_status": "สามารถลดหย่อนได้"}
                    ],
                    "deduction_status": "ผ่านเงื่อนไขเบื้องต้น"
                }
            }
        }
        return jsonify({"ok": True, "result": demo})
    
    def normalize_page_key(p):
        if isinstance(p, int):
            return p
        s = str(p).strip()
        # ดึงเลขหน้าด้านซ้ายของรูปแบบ "x/y"
        m = re.match(r'^(\d+)(?:/\d+)?$', s)
        if m:
            return int(m.group(1))
        # เผื่อรูปแบบอื่น ๆ เช่น "page-3"
        m = re.search(r'(\d+)', s)
        return int(m.group(1)) if m else 1  # fallback

    try:
        file_handler = FileHandler(save_path)
        ocr_service = OCRService()
        extractor = TransactionExtractor(ocr_service)
        ocr_result = extractor.process_document(file_handler)  # {page: text}
        print(ocr_result.items())

        pages = {}
        base = os.path.splitext(filename)[0]

        for raw_page, text in ocr_result.items():
            print(raw_page)
            page = normalize_page_key(raw_page)
            invoice = ex(text)
            out = invoice.typhoon_extract()        # dict; บางเวอร์ชันเป็น {"json": {...}}
            payload = out.get("json", out)         # รองรับทั้งสองแบบ 2 บรรนี้คือันเก่า
            

            pred = prediction(payload).run()
            # finder = FindInvoiceCompany(input_json=pred, file_name=base, num=page)
            # verified = finder.invoice_company()
            checked = check_condition(pred,file_name=base, num=page, user_name=user_name,net_income=net_income_raw,).check()
            pages[str(page)] = checked   # << เก็บ dict ตรง ๆ
            
            try:
                # ตั้งชื่อไฟล์ JSON เช่น: invoice123_page1.json
                json_filename = f"{base}_page{page}.json"
                json_path = os.path.join(JSON_DIR, json_filename)

                with open(json_path, 'w', encoding='utf-8') as jf:
                    json.dump(checked, jf, ensure_ascii=False, indent=4)
                
                print(f"💾 Saved JSON locally: {json_path}")
            except Exception as e:
                print(f"Failed to save local JSON: {e}")
            
            try:
                # ดึงค่า Category ออกมาจากผลลัพธ์ (ถ้าหาไม่เจอให้ใส่ค่า default เป็นขีด)
                # ต้องเช็คว่าใน dict 'checked' ใช้ key ชื่ออะไร (เช่น 'category', 'sub_category')
                m_cat = checked.get("category", "ไม่ระบุ")
                s_cat = checked.get("sub_category", "ไม่ระบุ")
                
                print(f"กำลังบันทึกประวัติ: {filename} -> {m_cat}/{s_cat}")
                
                # เรียกฟังก์ชันจาก services.py
                save_upload_history(filename, m_cat, s_cat,checked)
                
            except Exception as db_e:
                print(f"Database Error (ไม่กระทบการทำงานหลัก): {db_e}")

        if os.path.exists(save_path):
            os.remove(save_path)
            print(f"🗑️ Deleted local file: {filename}")

        return jsonify({"ok": True, "result": {"file": filename, "pages": pages}})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # ดึง PORT จาก env (Render จะเซ็ตให้)
    app.run(host="0.0.0.0", port=port, debug=False)
