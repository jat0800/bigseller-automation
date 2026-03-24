from playwright.sync_api import sync_playwright

def check_new_orders():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        print("🚀 กำลังพุ่งไปที่หน้าจัดการออเดอร์...")
        page.goto("https://www.bigseller.com/web/order/index.htm?status=new", wait_until="domcontentloaded", timeout=60000) 

        # รอ 8 วินาทีให้ตารางออเดอร์โผล่มา
        page.wait_for_timeout(8000)
        print("✅ โหลดหน้าออเดอร์เสร็จเรียบร้อย!")

        # ==========================================
        # 🛡️ ระบบกำจัด Pop-up และประกาศกวนใจ
        # ==========================================
        print("🔍 กำลังเช็กว่ามี Pop-up กวนใจไหม...")
        # วนลูปเช็กสัก 3 รอบ เผื่อมีหน้าต่างซ้อนกัน
        for _ in range(3):
            try:
                # ให้เวลาบอทเพ่งมองหาปุ่มแค่ 1 วินาที (จะได้ไม่เสียเวลารอนานถ้าไม่มี Pop-up)
                if page.locator('button:has-text("ปิด")').first.is_visible(timeout=1000):
                    page.locator('button:has-text("ปิด")').first.click()
                    print("💥 จัดการกดปุ่ม 'ปิด'")
                    page.wait_for_timeout(1000) # รอหน้าต่างหดกลับ
                
                elif page.locator('button:has-text("ข้าม")').first.is_visible(timeout=1000):
                    page.locator('button:has-text("ข้าม")').first.click()
                    print("💥 จัดการกดปุ่ม 'ข้าม'")
                    page.wait_for_timeout(1000)
                    
                elif page.locator('button:has-text("ต่อไป")').first.is_visible(timeout=1000):
                    page.locator('button:has-text("ต่อไป")').first.click()
                    print("💥 จัดการกดปุ่ม 'ต่อไป'")
                    page.wait_for_timeout(1000)
                else:
                    # ถ้าหาไม่เจอทั้ง 3 ปุ่ม แปลว่าหน้าจอโล่งแล้ว ให้พังลูปออกไปทำงานต่อได้เลย
                    break 
            except Exception:
                break
                
        print("✅ หน้าจอโล่งแล้ว ลุยดึงออเดอร์ต่อ!")

        # ==========================================
        # สเต็ปที่ 1: ติ๊กเลือกออเดอร์ทั้งหมด
        # ==========================================
        print("👉 กำลังกดเลือกออเดอร์ทั้งหมด...")
        page.locator('input[name="listAllBox"]').check()
        page.wait_for_timeout(1000) # รอแป๊บนึงให้ระบบติ๊กถูกจนครบ

        # ==========================================
        # สเต็ปที่ 2: กดปุ่ม "พิมพ์เป็นชุด"
        # ==========================================
        print("👉 กำลังเปิดเมนู พิมพ์เป็นชุด...")
        page.locator('button:has-text("พิมพ์เป็นชุด")').first.click()
        page.wait_for_timeout(1000)

        # ==========================================
        # สเต็ปที่ 3: กดเลือก "พิมพ์รายการสรุป" จาก Dropdown
        # ==========================================
        print("👉 กำลังคลิก พิมพ์รายการสรุป...")
        # ใช้การหาจากข้อความได้เลย
        page.locator('text="พิมพ์รายการสรุป"').last.click(force=True)
        page.wait_for_timeout(1000)

        # ==========================================
        # สเต็ปที่ 4: กดยืนยัน Pop up + ดักจับแท็บใหม่ที่เด้งขึ้นมา
        # ==========================================
        print("👉 กำลังกดยืนยัน และสลับไปหน้าต่างใหม่...")
        
        # คำสั่ง expect_page() คือการรอรับแท็บใหม่ที่จะเด้งขึ้นมา
        with context.expect_page() as new_page_info:
            page.locator('button:has-text("ยืนยัน")').last.click()
            
        # สลับตัวคุมบอทไปที่หน้าต่างใหม่
        summary_page = new_page_info.value
        summary_page.wait_for_load_state("domcontentloaded")
        print("🎉 เข้าสู่หน้าใบสรุปสำเร็จแล้ว!")

        # ==========================================
        # สเต็ปที่ 5: ดูดข้อมูลแบบจัดกลุ่ม (1 SKU มีหลายออเดอร์)
        # ==========================================
        print("⏳ รอให้ระบบวาดตารางรายการสินค้า...")
        summary_page.wait_for_selector('div[data-productname="product_sku"]', timeout=15000)
        summary_page.wait_for_timeout(2000) 

        print("📥 กำลังดูดข้อมูลสินค้าและรหัสออเดอร์ย่อย...")
        
        products_data = summary_page.evaluate('''() => {
            let results = [];
            
            // หากล่อง "แถว" ของแต่ละสินค้า (BigSeller มักจะแยกเป็นบรรทัดๆ)
            // เราจะหาจาก class ที่ครอบ SKU และชื่อสินค้าเอาไว้
            let itemRows = document.querySelectorAll('div.item_info').forEach(infoDiv => {
                // หากล่องแม่ที่ครอบบรรทัดนี้อยู่ (เพื่อจะได้ดึงข้อมูลอื่นในบรรทัดเดียวกันได้)
                let parentRow = infoDiv.closest('tr'); // ลองใช้ tr ก่อน
                if (!parentRow) {
                     // ถ้าไม่ใช่ tr ลองหา div ที่น่าจะเป็นตัวคลุมบรรทัด
                     parentRow = infoDiv.parentElement.parentElement; 
                }

                // ดึงชื่อสินค้า
                let nameText = infoDiv.innerText.trim();

                // ดึง SKU (หาจากใน parentRow เดียวกัน)
                let skuEl = parentRow.querySelector('div[data-productname="product_sku"]');
                let skuText = skuEl ? skuEl.innerText.trim() : "ไม่พบ SKU";

                // ดึงจำนวน (หาจากใน parentRow เดียวกัน)
                let qtyEl = parentRow.querySelector('div[data-productname="product_sku_quantity"]');
                let qtyText = qtyEl ? qtyEl.innerText.trim() : "0";

                // ดึงรหัสออเดอร์ทั้งหมดที่เป็นของสินค้านี้
                let orderEls = parentRow.querySelectorAll('.t_c');
                let ordersList = [];
                orderEls.forEach(orderEl => {
                    let orderText = orderEl.innerText.trim();
                    if(orderText !== "" && orderText !== "...") { // ดักจับเผื่อติดจุดไข่ปลา
                        ordersList.push(orderText); 
                    }
                });

                results.push({
                    "sku": skuText,
                    "name": nameText,
                    "total_qty": qtyText,
                    "orders": ordersList
                });
            });
            
            return results;
        }''')

        # ==========================================
        # สเต็ปที่ 6: โชว์ผลลัพธ์ที่ได้ออกมาดู
        # ==========================================
        print(f"\n✅ ดึงข้อมูลสำเร็จ! ได้มาทั้งหมด {len(products_data)} SKU\n")
        
        for item in products_data:
            print(f"📦 SKU: {item['sku']} | จำนวนรวมต้องแพ็ค: {item['total_qty']}")
            print(f"   📝 ชื่อ: {item['name']}")
            print(f"   🏷️ รหัสออเดอร์ย่อย: {item['orders']}")
            print("-" * 60)

        # ==========================================
        # 🖨️ สเต็ปที่ 7: สั่งเด้งหน้าต่างปริ้น (A4)
        # ==========================================
        print("🖨️ กำลังสั่งเปิดหน้าต่างปริ้น...")
        print("👉 บอทจะหยุดรอตรงนี้นะครับ ฟลุ๊คสามารถกดปุ่ม Print หรือเคาะ Enter เพื่อปริ้นใบ A4 ได้เลย")
        print("👉 ปริ้นเสร็จแล้ว ค่อยมากด Resume (▶) ให้บอททำงานจนจบครับ")

        # ทริคโปรแกรมเมอร์: ใช้ setTimeout เพื่อไม่ให้บอทค้างตอนเปิดหน้าต่าง Print
        summary_page.evaluate("setTimeout(() => { window.print(); }, 1000);")

        # สั่งบอทหยุดรอ ให้คนกดปริ้นกระดาษให้เสร็จก่อน
        summary_page.pause()

        # ปิดเบราว์เซอร์เมื่อทำงานเสร็จทุกอย่าง
        print("🏁 จบการทำงานของบอทดึงออเดอร์!")
        browser.close()

if __name__ == "__main__":
    check_new_orders()