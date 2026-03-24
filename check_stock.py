from playwright.sync_api import sync_playwright

def run_bot():
    with sync_playwright() as p:
        # 1. เปิดเบราว์เซอร์ (ตั้ง headless=False ไว้ก่อนเพื่อดูว่ามันทำงานถูกไหม)
        browser = p.chromium.launch(headless=False, slow_mo=50)

        # 2. 🌟 จุดสำคัญอยู่ตรงนี้! สั่งให้โหลดตั๋วผ่านประตู auth.json 🌟
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        print("🚀 กำลังพุ่งตรงเข้าสู่ระบบหลังบ้าน BigSeller...")
        
        # 3. วิ่งตรงไปที่หน้าแดชบอร์ด หรือหน้าจัดการสต็อกได้เลย
        # (ลองเปลี่ยน URL เป็นลิงก์หน้าเว็บที่ต้องการให้บอทเข้าไปทำงานได้เลยครับ)
        page.goto("https://www.bigseller.com/th_TH/dashboard.htm") 

        print("✅ ข้ามหน้าล็อกอินสำเร็จ! พร้อมลุยงานต่อ")

        # 4. หยุดรอให้เห็นผลงานสัก 5 วินาที ก่อนปิด (เดี๋ยวเราค่อยมาลบออกตอนเขียนคำสั่งทำงานจริง)
        page.wait_for_timeout(5000)

        browser.close()

if __name__ == "__main__":
    run_bot()