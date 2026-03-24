import gspread
from google.oauth2.service_account import Credentials
import time
import requests
import json

# ==========================================
# ⚙️ ตั้งค่าระบบ (ใส่ข้อมูลของฟลุ๊คตรงนี้)
# ==========================================
SHEET_NAME = "Copy of สต็อก"
LINE_CHANNEL_TOKEN = "IWNkCrLTyBvITNJEg64EcGZS+wK5SVLUVHHrBviXczYaadxy/sFh5WZL0HZfGssdwKrjo8YJn0pfZJsNfdTpnKQcdbFvZ8kOV1EXcdbStw64OpIqmwspQHNcqQ+fQTSVpzTGYye+ri/gjKNF+QyTeQdB04t89/1O/w1cDnyilFU="
LINE_USER_ID = "U08131beb448f87196613dfeb94dc742b"

def send_line_oa_message(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_TOKEN}"
    }
    data = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    try:
        requests.post(url, headers=headers, data=json.dumps(data))
    except Exception as e:
        print(f"❌ ส่ง LINE แจ้งเตือนไม่สำเร็จ: {e}")

def process_orders_and_stock(products_data, page=None): # เพิ่ม page=None ไว้รองรับตอนรันจริง
    print("🔄 กำลังเชื่อมต่อกับ Google Sheets...")
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    gc = gspread.authorize(credentials)
    
    try:
        worksheet = gc.open(SHEET_NAME).sheet1
        all_skus_in_sheet = worksheet.col_values(1) 
        
        # เตรียมตะกร้าแยกของ
        ready_to_pack = []
        out_of_stock = []
        
        print("🔍 กำลังเริ่มตรวจสอบและตัดสต็อก...")
        
        for item in products_data:
            target_sku = item['sku']
            qty_needed = int(item['total_qty']) 
            
            # 🛑 1. กรอง SKU ที่ไม่ต้องยุ่งกับสต็อก
            ignore_prefixes = ("OSU", "TOTA", "KANT", "JADE")
            if target_sku.upper().startswith(ignore_prefixes):
                print(f"⏩ ข้าม {target_sku}: (กลุ่มสินค้าที่ตั้งค่ายกเว้น)")
                ready_to_pack.extend(item['orders'])
                continue 
            
            try:
                # 2. ค้นหาบรรทัดของ SKU
                row_index = all_skus_in_sheet.index(target_sku) + 1
                
                # 3. เช็กสต็อกปัจจุบัน
                current_stock_str = worksheet.cell(row_index, 3).value
                current_stock = int(current_stock_str) if current_stock_str else 0
                
                # ⚖️ 4. ประมวลผลแยกตะกร้า
                if current_stock >= qty_needed:
                    new_stock = current_stock - qty_needed
                    try:
                        worksheet.update_acell(f"C{row_index}", new_stock)
                    except Exception as e:
                        if "200" not in str(e): print(f"❌ Error update sheet: {e}")
                        
                    print(f"✅ {target_sku}: สต็อกพอ ({current_stock} -> เหลือ {new_stock})")
                    ready_to_pack.extend(item['orders']) 
                    
                else:
                    short_qty = qty_needed - current_stock
                    print(f"❌ {target_sku}: ของขาด! (ต้องการ {qty_needed} แต่มีแค่ {current_stock})")
                    item['short_qty'] = short_qty
                    out_of_stock.append(item)
                
                time.sleep(1) # กัน Sheets บล็อก
                
            except ValueError:
                print(f"⚠️ ไม่พบ {target_sku} ในไฟล์สต็อก")
                item['short_qty'] = qty_needed
                out_of_stock.append(item)
                
        # ==========================================
        # 📲 สรุปผลและส่ง LINE แจ้งเตือน
        # ==========================================
        print("\n🏁 ประมวลผลเสร็จสิ้น!")
        print(f"📦 ออเดอร์ที่พร้อมส่ง (รอไปกดใน BigSeller): {len(ready_to_pack)} รายการ")
        
        if len(out_of_stock) > 0:
            print(f"🚨 พบสินค้าขาดสต็อก {len(out_of_stock)} รายการ! กำลังส่ง LINE...")
            alert_msg = "🚨 แจ้งเตือน! สินค้าขาดสต็อก 🚨\n"
            alert_msg += "-" * 20 + "\n"
            for item in out_of_stock:
                alert_msg += f"📦 SKU: {item['sku']}\n"
                alert_msg += f"📝 {item['name']}\n"
                alert_msg += f"❌ ขาดอีก: {item.get('short_qty', item['total_qty'])} ชิ้น\n"
                alert_msg += f"🛒 ออเดอร์: {', '.join(item['orders'])}\n"
                alert_msg += "-" * 20 + "\n"
            alert_msg += "📲 รบกวนสั่งของเติมสต็อกด่วนครับ!"
            send_line_oa_message(alert_msg)
        else:
            print("🎉 สต็อกเพียงพอทุกรายการ ไม่มีแจ้งเตือน!")

        # ==========================================
        # 🎯 สเต็ปค้นหาใน BigSeller (ย้ายเข้ามาอยู่ในบล็อก try)
        # ==========================================
        if len(ready_to_pack) > 0 and page is not None:
            print(f"\n🎯 เริ่มสเต็ปค้นหา {len(ready_to_pack)} ออเดอร์ที่พร้อมส่ง...")
            
            page.locator('.ant-select-selection--single').first.click() 
            page.locator('li:has-text("หมายเลขคำสั่งซื้อ")').click()
            page.wait_for_timeout(500)

            page.locator('label:has-text("คลุมเครือ")').click()
            page.wait_for_timeout(500)

            for order_id in ready_to_pack:
                clean_id = order_id.split(' ')[0].replace('*', '')
                print(f"🔍 กำลังค้นหา: {clean_id}")
                
                page.locator('input.input-search.ant-input').fill(clean_id)
                page.keyboard.press("Enter")
                page.wait_for_timeout(2000)

                page.locator('input[type="checkbox"]').first.check()
                page.locator('input.input-search.ant-input').clear()

            print("🛡️ Dry Run: กำลังเอาเมาส์ไปชี้ปุ่มยืนยัน...")
            page.locator('.ant-btn-sm:has-text("ยืนยัน")').hover()
            
            print("💡 บอทหยุดรอแล้ว ตรวจสอบที่หน้าจอได้เลยครับ")
            page.pause()

        return ready_to_pack

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในระบบสต็อก: {e}")
        return []

# ==========================================
# ส่วนทดสอบการทำงาน
# ==========================================
if __name__ == "__main__":
    dummy_orders = [
        {"sku": "KONY00170", "name": "KONY ถอดลูกสูบ...", "total_qty": "1", "orders": ["*E3RK 1"]},
        {"sku": "NON00014", "name": "SUPER RFAY...", "total_qty": "50", "orders": ["*2NJN 1"]},
        {"sku": "OSUKA001", "name": "สว่าน...", "total_qty": "2", "orders": ["*XXYY 1"]}
    ]
    
    # ตอนทดสอบในไฟล์นี้จะไม่มี page ให้ส่งเข้าไป บอทจะข้ามสเต็ป BigSeller ไปก่อน
    ready_orders = process_orders_and_stock(dummy_orders)
    print("\n👉 ลิสต์ออเดอร์ที่พร้อมส่งไปคลิกต่อใน BigSeller:")
    print(ready_orders)