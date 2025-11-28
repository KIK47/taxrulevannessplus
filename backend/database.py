import os
from supabase import create_client, Client

# ========================================================
# ตั้งค่าการเชื่อมต่อ Supabase
# ========================================================
# URL และ Key ของคุณ
url = os.getenv("data_url")
key = os.getenv("data_key")

# สร้าง Client
try:
    supabase: Client = create_client(url, key)
except Exception as e:
    print(f"Supabase Connection Error: {e}")
    supabase = None

# ========================================================
# ฟังก์ชันสำหรับบันทึกข้อมูล
# ========================================================
def save_upload_history(filename, maincategory, subcategory,json_data):
    """
    รับค่าชื่อไฟล์และหมวดหมู่ แล้วบันทึกลงตาราง upload_history
    """
    # ถ้าเชื่อมต่อไม่ได้ ให้จบการทำงานเลย
    if supabase is None:
        print("❌ Cannot connect to Supabase")
        return False

    try:
        # เตรียมข้อมูลสำหรับส่งเข้า Database
        # (ไม่ต้องส่งวันที่ เพราะตั้งให้ Supabase เติมอัตโนมัติแล้ว)
        data = {
            "name": filename,
            "maincategory": maincategory, 
            "subcategory": subcategory,
            "jsonfile": json_data
        }
        
        # สั่ง Insert ข้อมูลลงตาราง 'upload_history'
        response = supabase.table("fileupload").insert(data).execute()
        
        print(f"✅ Saved to DB Success: {filename}")
        return True

    except Exception as e:
        print(f"❌ Database Error: {e}")
        return False