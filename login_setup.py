from playwright.sync_api import sync_playwright

def login_and_save_state():
    with sync_playwright() as p:
        # 1. เปิดเบราว์เซอร์แบบให้เห็นหน้าจอ (headless=False) จะได้กรอกรหัสได้
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context()
        page = context.new_page()

        print("🌐 กำลังเปิดหน้าเว็บ BigSeller...")
        # ไปที่หน้า Login ของ BigSeller ประเทศไทย
        page.goto("https://www.bigseller.com/th/login.htm")

        print("\n=======================================================")
        print("🧑‍💻 เฮียคิม ดำเนินการล็อกอินบนหน้าต่างเว็บที่เด้งขึ้นมาได้เลยครับ")
        print("พิมพ์เบอร์โทร, รหัสผ่าน, ติ๊กยอมรับเงื่อนไข และแก้ Captcha ให้เรียบร้อย")
        print("=======================================================\n")

        # 2. ระบบจะหยุดรอตรงนี้ จนกว่าเฮียจะล็อกอินเสร็จและมากด Enter ในนี้
        input("กด Enter ที่นี่ 'หลังจาก' ล็อกอินสำเร็จและเห็นหน้าแดชบอร์ดแล้วนะครับ...")

        # 3. ดูดคุกกี้และสถานะการล็อกอินทั้งหมดมาเซฟเป็นไฟล์ auth.json
        context.storage_state(path="auth.json")
        print("✅ บันทึกตั๋วผ่านประตู (Cookies) สำเร็จ! ไฟล์ auth.json ถูกสร้างแล้ว")

        # ปิดเบราว์เซอร์
        browser.close()

if __name__ == "__main__":
    login_and_save_state()