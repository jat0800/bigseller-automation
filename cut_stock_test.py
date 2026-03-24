import gspread
from google.oauth2.service_account import Credentials
import time

def deduct_stock_in_sheet(products_data):
    print("🔄 กำลังเชื่อมต่อกับ Google Sheets...")
    
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    gc = gspread.authorize(credentials)
    
    # 📌 ใส่ชื่อไฟล์ Google Sheets ที่ฟลุ๊ค "ทำสำเนา" มาแล้ว
    sheet_name = "Copy of สต็อก" 
    
    try:
        # เปิดไฟล์และเลือกชีตแรก
        worksheet = gc.open(sheet_name).sheet1
        print(f"✅ เปิดไฟล์ '{sheet_name}' สำเร็จ! กำลังเริ่มตัดสต็อก...")
        
        # ดึงข้อมูล SKU ทั้งหมดใน "คอลัมน์ A" (คอลัมน์ที่ 1) มาเก็บไว้เป็น List เพื่อใช้ค้นหา
        all_skus_in_sheet = worksheet.col_values(1) 
        
        for item in products_data:
            target_sku = item['sku']
            qty_to_deduct = int(item['total_qty']) # จำนวนที่ต้องหัก
            
            # ==========================================
            # 🛑 ระบบกรอง SKU ที่ไม่ต้องตัดสต็อก
            # ==========================================
            ignore_prefixes = ("OSU", "TOTA", "KANT", "JADE")
            # แปลงเป็นพิมพ์ใหญ่ก่อนเช็ก เผื่อบางทีเว็บส่งมาเป็นตัวพิมพ์เล็ก
            if target_sku.upper().startswith(ignore_prefixes):
                print(f"⏩ ข้าม {target_sku}: สินค้ากลุ่มนี้ไม่ต้องตัดสต็อก")
                continue # สั่งให้กระโดดข้ามไปทำ SKU ตัวถัดไปทันที!

            try:
                # 1. ค้นหาว่า SKU นี้อยู่ "บรรทัดที่เท่าไหร่" ในไฟล์ Sheets
                row_index = all_skus_in_sheet.index(target_sku) + 1
                
                # 2. ดึง "สต็อกปัจจุบัน" จากคอลัมน์ C (คอลัมน์ที่ 3) ของบรรทัดนั้น
                current_stock_str = worksheet.cell(row_index, 3).value
                current_stock = int(current_stock_str) if current_stock_str else 0
                
                # 3. คำนวณสต็อกคงเหลือ
                new_stock = current_stock - qty_to_deduct
                
                # ==========================================
                # 4. อัปเดตข้อมูล (พร้อมโล่ป้องกันบัค 200)
                # ==========================================
                try:
                    # เปลี่ยนมาใช้ update_acell (ระบุชื่อช่องตรงๆ เช่น C5)
                    worksheet.update_acell(f"C{row_index}", new_stock)
                except Exception as update_err:
                    if "200" in str(update_err):
                        pass # ถ้าเป็นบัค 200 ให้ปล่อยผ่านไปเลย (เพราะอัปเดตสำเร็จแล้ว)
                    else:
                        print(f"❌ เกิดปัญหาตอนเขียนข้อมูล {target_sku}: {update_err}")
                        continue # ถ้าเป็น Error อื่น ให้ข้ามไปทำตัวต่อไป
                
                print(f"📦 {target_sku}: สต็อกเดิม {current_stock} ชิ้น -> หัก {qty_to_deduct} -> เหลือ {new_stock} ชิ้น")
                
                # ใส่ระบบหน่วงเวลา 1 วินาที ป้องกัน Google Sheets บล็อก
                time.sleep(1) 
                
            except ValueError:
                print(f"❌ ข้าม {target_sku}: หา SKU นี้ไม่เจอในไฟล์สต็อก!")
                
        print("\n🎉 ตัดสต็อกในระบบจำลองเสร็จสมบูรณ์!")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")

# ==========================================
# ส่วนทดสอบ (เอาข้อมูลที่บอทดึงได้เมื่อวานมาเทส)
# ==========================================
if __name__ == "__main__":
    dummy_orders = [
        {"sku": "KONY00170", "name": "KONY ถอดลูกสูบ...", "total_qty": "6", "orders": ["*E3RK 1"]},
        {"sku": "NON00014", "name": "SUPER RFAY...", "total_qty": "2", "orders": ["*2NJN 1"]}
    ]
    
    deduct_stock_in_sheet(dummy_orders)