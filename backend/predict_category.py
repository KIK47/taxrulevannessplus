import joblib, json, re
import numpy as np
from typing import Union, Dict, Any
from pythainlp.tokenize import word_tokenize
from pythainlp.corpus.common import thai_stopwords
from json.decoder import JSONDecodeError
from sklearn.pipeline import Pipeline  # ✅ เพิ่ม: ใช้ตรวจว่าเป็น Pipeline หรือไม่

class prediction:
    def __init__(
        self,
        input_json: Union[str, dict],
        main_model_path: str = "./best_model/main01model_manual.pkl",
        sub_personal_path: str = "./best_model/sub01model.pkl",
        sub_invest_path: str = "./best_model/sub02model.pkl",
        sub_assets_path: str = "./best_model/sub03model.pkl",
        sub_easy_path: str = "./best_model/sub04model.pkl",
        sub_donation_path: str = "./best_model/sub05model.pkl",
    ):
        self.input_json_raw = input_json

        # โหลดโมเดลหลัก
        self.main_model = joblib.load(main_model_path)

        # ✅ เพิ่ม: ตรวจชนิดอินพุตที่โมเดลหลักคาดหวัง (ข้อความ vs เวกเตอร์)
        self.main_expects_text = self._detect_main_input_type()

        # โหลด sub-models (คาดว่าเป็น tuple: (model, vectorizer))
        self.sub_model_personal, self.sub_vec_personal = joblib.load(sub_personal_path)
        self.sub_model_invest,   self.sub_vec_invest   = joblib.load(sub_invest_path)
        self.sub_model_assets,   self.sub_vec_assets   = joblib.load(sub_assets_path)
        self.sub_model_easy,     self.sub_vec_easy     = joblib.load(sub_easy_path)
        self.sub_model_donation, self.sub_vec_donation = joblib.load(sub_donation_path)

        # ✅ เพิ่ม: ทำให้ sub-model รองรับทุกฟอร์แมต (tuple สลับ, pipeline เดี่ยว, model เดี่ยว)
        def _normalize_pair(obj):
            """
            คืนค่าเป็น (model, vectorizer, is_pipeline)
            - Pipeline เดี่ยว  -> (pipeline, None, True)
            - tuple 2 ชิ้น     -> เดาว่าอันไหนคือ vectorizer จากการมี .transform
            - อื่น ๆ (model)   -> (model, None, False)
            """
            if isinstance(obj, Pipeline):
                return obj, None, True
            if isinstance(obj, tuple) and len(obj) == 2:
                a, b = obj
                a_is_vec = hasattr(a, "transform")
                b_is_vec = hasattr(b, "transform")
                # vectorizer มี .transform เสมอ
                if a_is_vec and not b_is_vec:
                    return b, a, False  # (model, vectorizer)
                if b_is_vec and not a_is_vec:
                    return a, b, False  # (model, vectorizer)
                # เดาอย่างปลอดภัย: ถือว่าตัวแรกคือ model, ตัวที่สองเป็น vectorizer ถ้ามี
                return a, (b if b_is_vec else None), False
            # โมเดลเดี่ยว
            return obj, None, False

        # ✅ Normalize ทุกตัว (เพิ่ม flag is_pipeline)
        self.sub_model_personal, self.sub_vec_personal, self.sub_is_pipe_personal = _normalize_pair(
            (self.sub_model_personal, self.sub_vec_personal)
        )
        self.sub_model_invest,   self.sub_vec_invest,   self.sub_is_pipe_invest   = _normalize_pair(
            (self.sub_model_invest, self.sub_vec_invest)
        )
        self.sub_model_assets,   self.sub_vec_assets,   self_sub_is_pipe_assets   = _normalize_pair(
            (self.sub_model_assets, self.sub_vec_assets)
        )
        # เก็บชื่อ attribute ให้สอดคล้อง (เพิ่มเท่านั้น ไม่ลบของเดิม)
        self.sub_is_pipe_assets = self_sub_is_pipe_assets

        self.sub_model_easy,     self.sub_vec_easy,     self.sub_is_pipe_easy     = _normalize_pair(
            (self.sub_model_easy, self.sub_vec_easy)
        )
        self.sub_model_donation, self.sub_vec_donation, self.sub_is_pipe_donation = _normalize_pair(
            (self.sub_model_donation, self.sub_vec_donation)
        )

        self.stopwords = set(thai_stopwords())

        # ✅ เพิ่ม: โหลด Thai2Vec แบบ lazy เฉพาะเมื่อจำเป็น
        self.thai2vec_model = None
        if not self.main_expects_text:
            from pythainlp import word_vector
            self.thai2vec_model = word_vector.WordVector(model_name="thai2fit_wv").get_model()

        # ✅ เพิ่ม: map ชื่อหมวดให้ตรงกับ _predict_sub
        self.cat_map = {
            "สิทธิลดหย่อนส่วนตัวและครอบครัว": "สิทธิลดหย่อนส่วนตัวและครอบครัว",
            "ค่าลดหย่อน/ยกเว้น ด้านการออม การลงทุน และประกัน": "การออมการลงทุนและประกัน",
            "การออมการลงทุนและประกัน": "การออมการลงทุนและประกัน",
            "ค่าลดหย่อน/ยกเว้น จากสินทรัพย์และมาตรการนโยบายภาครัฐ": "สินทรัพย์และมาตรการนโยบายภาครัฐ",
            "สินทรัพย์และมาตรการนโยบายภาครัฐ": "สินทรัพย์และมาตรการนโยบายภาครัฐ",
            "Easy E-Receipt": "Easy E-Receipt",
            "เงินบริจาค": "เงินบริจาค",
        }

    # ===== Utilities =====
    @staticmethod
    def safe_json_loads(text: str) -> dict:
        try:
            return json.loads(text)
        except JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise

    def preprocess_text(self, text: str) -> str:
        text = "" if text is None else str(text)
        text = re.sub(r"[^\u0E00-\u0E7Fa-zA-Z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip().lower()
        tokens = word_tokenize(text, engine="newmm")
        return " ".join([t for t in tokens if t and t not in self.stopwords])

    def sentence_vector(self, sentence: str) -> np.ndarray:
        if self.thai2vec_model is None:
            # เผื่อกรณีเรียกโดยไม่ได้โหลดไว้ (ไม่ควรเกิด)
            from pythainlp import word_vector
            self.thai2vec_model = word_vector.WordVector(model_name="thai2fit_wv").get_model()
        words = word_tokenize(sentence, engine="newmm")
        vectors = [self.thai2vec_model[w] for w in words if w in self.thai2vec_model]
        return np.mean(vectors, axis=0) if vectors else np.zeros(self.thai2vec_model.vector_size)

    def _detect_main_input_type(self) -> bool:
        """
        พยายามเดาด้วยการลอง predict แบบ 'ข้อความ' ก่อน
        คืนค่า True  = โมเดลหลักคาดหวัง 'ข้อความ' (เช่น TF-IDF Pipeline)
              False = โมเดลหลักคาดหวัง 'เวกเตอร์เชิงตัวเลข'
        """
        try:
            _ = self.main_model.predict(["ทดสอบข้อความ"])
            return True
        except Exception:
            return False

    def _normalize_cat(self, cat: str) -> str:
        return self.cat_map.get(cat, cat)

    # ===== Predictors =====
    def _predict_category(self, cleaned_name: str) -> str:
        # ✅ แก้: ไม่เรียก .transform() กับ LogisticRegression โดยตรง
        if self.main_expects_text:
            # โมเดลหลักเป็น Pipeline (รับข้อความ)
            return self.main_model.predict([cleaned_name])[0]
        else:
            # โมเดลหลักรอเวกเตอร์ (เช่น LR ที่เทรนจาก thai2vec)
            vec = self.sentence_vector(cleaned_name).reshape(1, -1)
            return self.main_model.predict(vec)[0]

    def _predict_sub(self, cat: str, cleaned_name: str) -> str:
        # ทำชื่อหมวดให้ตรง key
        cat = self._normalize_cat(cat)

        def _do_predict(model, vec, is_pipe):
            if is_pipe:
                # pipeline: ส่งข้อความตรง ๆ
                return model.predict([cleaned_name])[0]
            if vec is not None:
                # มี vectorizer แยก
                X = vec.transform([cleaned_name])
                return model.predict(X)[0]
            # กรณีพิเศษ: ไม่มีทั้ง pipeline และ vectorizer
            try:
                return model.predict([cleaned_name])[0]
            except Exception:
                return "ไม่ทราบหมวดหมู่"

        if cat == "สิทธิลดหย่อนส่วนตัวและครอบครัว":
            return _do_predict(self.sub_model_personal, self.sub_vec_personal, self.sub_is_pipe_personal)
        elif cat == "การออมการลงทุนและประกัน":
            return _do_predict(self.sub_model_invest, self.sub_vec_invest, self.sub_is_pipe_invest)
        elif cat == "สินทรัพย์และมาตรการนโยบายภาครัฐ":
            return _do_predict(self.sub_model_assets, self.sub_vec_assets, self.sub_is_pipe_assets)
        elif cat == "Easy E-Receipt":
            return _do_predict(self.sub_model_easy, self.sub_vec_easy, self.sub_is_pipe_easy)
        elif cat == "เงินบริจาค":
            return _do_predict(self.sub_model_donation, self.sub_vec_donation, self.sub_is_pipe_donation)
        else:
            return "ไม่ทราบหมวดหมู่"

    def run(self) -> Dict[str, Any]:
        data = self.input_json_raw
        if isinstance(data, str):
            data = self.safe_json_loads(data)

        title = data.get("title", "")
        title = str(title)
        items = data.get("items") or []

        if "ภัย" in title:
            title = title.replace("ภัย", "ชีวิต")
        data["title"] = title

        seller = data.get("seller", "") or ""
        invoice_type = data.get("invoice_type", "") or ""
        # เพิ่ม or "" เพื่อเปลี่ยน None ให้เป็นข้อความว่าง
        item_names = [ str((it or {}).get("name") or "") for it in items ]
        raw = f"{title}".strip()
        cleaned = self.preprocess_text(raw)

        cat = self._predict_category(cleaned)
        sub = self._predict_sub(cat, cleaned)
        title_text = (title or "").lower()
        title_tax = (data.get("title_tax_invoice") or "").lower()
        # แนะนำให้ใส่ str() ครอบเพื่อความชัวร์ หรือใช้บรรทัดข้างบนแก้แล้วก็พอ
        name_txt = " ".join(item_names).lower()

        print(f"[R1] txt={raw!r}")
        print(f"[R1] cleaned={cleaned!r}")
        print(f"[R1] cat={cat} | sub={sub}")

        # --- RULE: override กลุ่มย่อยเมื่อเป็น ใบกำกับภาษี/ใบเสร็จ ---
        if (
            "ใบเสร็จรับเงิน" in title_tax
            or "ใบกำกับภาษี" in title_tax
            or "tax invoice" in title_tax
        ):
            # ✅ เช็คจากชื่อ item อย่างเดียว
            is_accommodation = any(k in name_txt for k in [
                "ห้องพัก", "ค่าห้อง", "ค่าที่พัก",
                "room", "accommodation", "hotel"
            ])

            is_food = any(k in name_txt for k in [
                "ค่าอาหาร", "อาหาร", "food",
                "บุฟเฟต์", "buffet",
                "เครื่องดื่ม", "drink",
                "กาแฟ", "coffee"
            ])

            if is_accommodation or is_food:
                # → มาตรการท่องเที่ยว
                cat = "สินทรัพย์และมาตรการนโยบายภาครัฐ"
                sub = "ค่าท่องเที่ยวภายในประเทศ"
                print("[RULE] override เป็น ค่าท่องเที่ยวภายในประเทศ จาก item ห้องพัก/อาหาร")
            else:
                # → E-Receipt ทั่วไป
                cat = "Easy E-Receipt"
                sub = "ค่าซื้อสินค้าหรือค่าบริการในระบบภาษีมูลค่าเพิ่ม"
                print("[RULE] override เป็น Easy E-Receipt จากใบกำกับภาษีทั่วไป (ดูจาก item)")
        
        # --- RULE: คนพิการ ---
        if (
            "คนทุพพลภาพ" in title_text
            or "ทุพพลภาพ" in title_text
            or "พิการ" in title_text
            ):
            sub = "อุปการะเลี้ยงดูคนพิการหรือคนทุพพลภาพ"
        
        if ("กองทุนรวมเพื่อการเลี้ยงชีพ" in title_text):
            sub = "ค่าซื้อหน่วยลงทุนเพื่อการเลี้ยงชีพ (RMF)"

        # --- RULE: override กลุ่มย่อยเมื่อเป็น Easy E-Receipt ด้วยชื่อสินค้า ---
        if self._normalize_cat(cat) == "Easy E-Receipt":
            name_txt = " ".join([(it or {}).get("name", "") for it in (data.get("items") or [])]).lower()

            if any(k in name_txt for k in ["หนังสือ", "book", "ebook", "e-book", "นิตยสาร", "หนังสือพิมพ์"]):
                sub = "ค่าซื้อหนังสือ e-book" if ("ebook" in name_txt or "e-book" in name_txt) \
            else "ค่าซื้อหนังสือ หนังสือพิมพ์ และนิตยสาร"
            elif "otop" in name_txt:
                sub = "ค่าซื้อสินค้า OTOP"
            else:
                sub = "ค่าซื้อสินค้าหรือค่าบริการในระบบภาษีมูลค่าเพิ่ม"
        
        # --- RULE: override กลุ่มย่อยเมื่อเป็น Easy E-Receipt ด้วยชื่อสินค้า ---
        if self._normalize_cat(cat) == "สิทธิลดหย่อนส่วนตัวและครอบครัว" and (
            "เลิกสัญญาจ้าง" in title_text
            ):
            sub = "เงินค่าชดเชยที่ได้รับตามกฎหมายแรงงาน (กรณีนำมารวมคำนวณภาษี)"
        
        # --- RULE: แก้ไขกรณี กอช. เป็น SSF ---
        if self._normalize_cat(cat) == "การออมการลงทุนและประกัน":
            # 1) ถ้าเป็น กองทุนการออมแห่งชาติ จริง ๆ → บังคับให้เป็น กอช.
            if "กองทุนการออมแห่งชาติ" in title_text or "กอช" in title_text:
                sub = "เงินสะสมกองทุนการออมแห่งชาติ (กอช.)"
                print("[RULE] บังคับเป็น กอช. จาก title ที่มีคำว่า กองทุนการออมแห่งชาติ/กอช")

            # 2) ถ้าเป็นกองทุนรวมเพื่อการออม (SSF) → บังคับเป็น SSF
            elif "กองทุนรวมเพื่อการออม" in title_text or "กองทุนรวม" in title_text:
                sub = "ค่าซื้อหน่วยลงทุนในกองทุนรวมเพื่อการออม SSF"
                print("[RULE] บังคับเป็น SSF จาก title ที่มีคำว่า กองทุนรวม(เพื่อการออม)")
        
        cat = self._predict_category(cleaned)
        sub = self._predict_sub(cat, cleaned)
        title_text = (title or "").lower()
        title_tax = (data.get("title_tax_invoice") or "").lower()
        
        # ========================================================
        # ✅ แก้ไข Logic ดักจับ "การเมือง" และ "บริจาค"
        # ========================================================
        
        # 1. ถ้ามีคำว่า "การเมือง" -> ไปหมวดสินทรัพย์ฯ
        if ("การเมือง" in title_text) or ("บริจาคการเมือง" in title_text):
            cat = "สินทรัพย์และมาตรการนโยบายภาครัฐ"
            sub = "เงินที่บริจาคแก่พรรคการเมือง"
            print("[RULE] พบ 'การเมือง' -> สินทรัพย์ฯ / บริจาคพรรคการเมือง")

        # 2. ถ้ามีคำว่า "บริจาค" (และไม่ใช่การเมือง) -> ไปหมวดเงินบริจาค
        elif "บริจาค" in title_text:
            cat = "เงินบริจาค"
            
            # เช็คว่าเป็นสถานศึกษาหรือไม่ (เช็คจาก keyword: ศึกษา, โรงเรียน, มหาลัย, ฯลฯ)
            education_keywords = ["ศึกษา", "โรงเรียน", "มหาวิทยาลัย", "วิทยาลัย", "ศูนย์พัฒนาเด็ก", "กีฬ", "พยาบาล"]
            
            if any(word in title_text for word in education_keywords):
                # กรณีเป็นบริจาคการศึกษา (ลดหย่อน 2 เท่า)
                sub = "เงินบริจาคสนับสนุนการศึกษา/สถานพยาบาล/อื่นๆ"
                print("[RULE] พบ 'บริจาค' + 'สถานศึกษา' -> บริจาคการศึกษา")
            else:
                # กรณีบริจาคทั่วไป
                sub = "เงินบริจาคทั่วไป"
                print("[RULE] พบ 'บริจาค' ทั่วไป -> บริจาคทั่วไป")
                
        # ========================================================
        # จบส่วนแก้ไข
        # ========================================================

        name_txt = " ".join(item_names).lower()
        

        # ===== เช็ค "ซ่อมบ้าน" จากชื่อไอเทม โดยไม่สร้างตัวแปรลิสต์แยก =====
        for it in items:
            name = (it.get("name") or "").lower()
            if any(k in name for k in [
                "ซ่อมบ้าน", "ซ่อมหลังคา", "เปลี่ยนหลังคา",
                "ซ่อมฝ้า", "ซ่อมฝ้าเพดาน",
                "ซ่อมผนัง", "ซ่อมกำแพง",
                "ซ่อมพื้น", "ซ่อมพื้นบ้าน",
                "ซ่อมรั้ว", "ซ่อมประตูรั้ว",
                "ทาสีบ้าน", "ซ่อมสีบ้าน",
                "ปูกระเบื้อง", "ซ่อมกระเบื้อง",
                "เปลี่ยนประตู", "ซ่อมประตู",
                "เปลี่ยนหน้าต่าง", "ซ่อมหน้าต่าง",
                "ซ่อมไฟฟ้า", "งานไฟฟ้า",
                "ซ่อมประปา", "งานประปา",
                "ปรับปรุงบ้าน", "รีโนเวทบ้าน"
            ]):
                data["sub_category"] = "ค่าซ่อมบ้านจากอุทกภัย"
                it["sub_category"] = "ค่าซ่อมบ้านจากอุทกภัย"
                print("[RULE] จัดเป็นค่าซ่อมบ้านจากอุทกภัย จากชื่อไอเทม:", name)
                break

            # ===== เช็ค "ซ่อมรถ" จากชื่อไอเทม โดยไม่สร้างตัวแปรลิสต์แยก =====
            if any(k in name for k in [
                "ซ่อมรถ", "ซ่อมรถยนต์", "ซ่อมรถกระบะ", "อู่ซ่อมรถ",
                "ซ่อมตัวถัง", "เคาะพ่นสี", "ทำสีรถ",
                "เปลี่ยนยาง", "ยางรถยนต์", "ตั้งศูนย์", "ถ่วงล้อ",
                "เปลี่ยนแบตเตอรี่", "แบตเตอรี่รถยนต์",
                "ซ่อมเครื่องยนต์", "ซ่อมเกียร์",
                "ซ่อมช่วงล่าง", "เปลี่ยนโช้ค",
                "ซ่อมกันชน", "ซ่อมกระจก", "ซ่อมกระจกรถ",
                "ล้างแอร์รถ", "ฟิล์มกรองแสงรถ"
            ]):
                data["sub_category"] = "ค่าซ่อมรถจากอุทกภัย"
                it["sub_category"] = "ค่าซ่อมรถจากอุทกภัย"
                print("[RULE] จัดเป็นค่าซ่อมรถจากอุทกภัย จากชื่อไอเทม:", name)
                break

        data["category"] = self._normalize_cat(cat)
        data["sub_category"] = sub

            
        # แนบ total ถ้ามี (กัน error ต่อสตริง)
        total = str(data.get("total", "")) if data.get("total") is not None else ""

        

        return data
