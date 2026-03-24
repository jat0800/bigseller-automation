import requests
import json

def send_line_oa_message(message):
    # 📌 ใส่ Token และ User ID ที่ก๊อปปี้มาจากสเต็ปที่ 2
    channel_access_token = "IWNkCrLTyBvITNJEg64EcGZS+wK5SVLUVHHrBviXczYaadxy/sFh5WZL0HZfGssdwKrjo8YJn0pfZJsNfdTpnKQcdbFvZ8kOV1EXcdbStw64OpIqmwspQHNcqQ+fQTSVpzTGYye+ri/gjKNF+QyTeQdB04t89/1O/w1cDnyilFU="
    user_id = "U08131beb448f87196613dfeb94dc742b" 
    
    url = "https://api.line.me/v2/bot/message/push"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_access_token}"
    }
    
    # รูปแบบคำสั่งของ Messaging API
    data = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            print("✅ ส่งแจ้งเตือนเข้า LINE OA สำเร็จ!")
        else:
            print(f"❌ ส่ง LINE ไม่สำเร็จ รหัส Error: {response.status_code}")
            print(f"รายละเอียด: {response.text}")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการส่ง LINE: {e}")

# ==========================================
# ส่วนทดสอบการทำงาน
# ==========================================
if __name__ == "__main__":
    out_of_stock = [
        {"sku": "KONY00256", "name": "โคมไฟหลอด LED 30 หลอด...", "short_qty": 2, "orders": ["*W7H6 1"]},
        {"sku": "OSU00008", "name": "OSUKA แบตเตอรี่ 20 โวลต์...", "short_qty": 1, "orders": ["*JK0Q 1"]}
    ]

    if len(out_of_stock) > 0:
        alert_msg = "🚨 แจ้งเตือน! สินค้าขาดสต็อก 🚨\n"
        alert_msg += "-" * 20 + "\n"
        
        for item in out_of_stock:
            alert_msg += f"📦 SKU: {item['sku']}\n"
            alert_msg += f"📝 {item['name']}\n"
            alert_msg += f"❌ ขาดอีก: {item['short_qty']} ชิ้น\n"
            alert_msg += f"🛒 ออเดอร์: {', '.join(item['orders'])}\n"
            alert_msg += "-" * 20 + "\n"
            
        alert_msg += "📲 รบกวนสั่งของเติมสต็อกด่วนครับ!"
        
        send_line_oa_message(alert_msg)
    else:
        print("🎉 สต็อกแน่นๆ ไม่มีของขาดครับ")