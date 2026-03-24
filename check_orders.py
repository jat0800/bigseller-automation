from playwright.sync_api import sync_playwright

# 🌟 นำเข้าฟังก์ชันจากไฟล์ process_stock_and_line.py ที่เราแยกไว้
from process_stock_and_line import process_orders_and_stock

def check_new_orders():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        print("🚀 กำลังพุ่งไปที่หน้าจัดการออเดอร์...")
        page.goto("https://www.bigseller.com/web/order/index.htm?status=new", wait_until="domcontentloaded", timeout=60000) 
        page.wait_for_timeout(8000)

        # ==========================================
        # 🛡️ ระบบกำจัด Pop-up (อัปเกรด V2 ปราบเกรียน Ant Design)
        # ==========================================
        print("🔍 กำลังเช็กว่ามี Pop-up กวนใจไหม...")
        # เพิ่มจำนวนรอบเช็กเป็น 5 รอบ เผื่อมันเด้งซ้อนกันหลายชั้น
        for _ in range(6):
            try:
                # 1. เล็งเป้าหากากบาท (X) มุมขวาบนของกล่องแจ้งเตือน
                if page.locator('.ant-modal-close').first.is_visible(timeout=1000):
                    page.locator('.ant-modal-close').first.click(force=True)
                    print("💥 จัดการกดปิด (X) Pop-up")
                    page.wait_for_timeout(1000)
                
                # 2. หาปุ่มข้อความแบบเดิม

                elif page.locator('button:has-text("ปิด & ไม่เตือน")').first.is_visible(timeout=1000):
                    page.locator('button:has-text("ปิด & ไม่เตือน")').first.click(force=True)
                    print("💥 จัดการกดปุ่ม 'ปิด & ไม่เตือน'")
                    page.wait_for_timeout(1000)

                elif page.locator('button:has-text("ปิด")').first.is_visible(timeout=1000):
                    page.locator('button:has-text("ปิด")').first.click(force=True)
                    print("💥 จัดการกดปุ่ม 'ปิด'")
                    page.wait_for_timeout(1000)
                    
                elif page.locator('button:has-text("ข้าม")').first.is_visible(timeout=1000):
                    page.locator('button:has-text("ข้าม")').first.click(force=True)
                    print("💥 จัดการกดปุ่ม 'ข้าม'")
                    page.wait_for_timeout(1000)
                    
                elif page.locator('button:has-text("ต่อไป")').first.is_visible(timeout=1000):
                    page.locator('button:has-text("ต่อไป")').first.click(force=True)
                    print("💥 จัดการกดปุ่ม 'ต่อไป'")
                    page.wait_for_timeout(1000)
                    
                else:
                    break # โล่งแล้ว ลุยต่อ!
            except Exception:
                break
                
        print("✅ หน้าจอโล่งแล้ว ลุยดึงออเดอร์ต่อ!")

        # ==========================================
        # สเต็ปที่ 1-4: ดึงใบสรุป
        # ==========================================
        page.locator('input[name="listAllBox"]').check()
        page.wait_for_timeout(1000)
        page.locator('button:has-text("พิมพ์เป็นชุด")').first.click()
        page.wait_for_timeout(1000)
        page.locator('text="พิมพ์รายการสรุป"').last.click(force=True)
        page.wait_for_timeout(1000)

        with context.expect_page() as new_page_info:
            page.locator('button:has-text("ยืนยัน")').last.click()
            
        summary_page = new_page_info.value

        # 🛑 2. ทริคสำคัญ: สลับแท็บกลับมาหน้าหลักก่อน เพื่อให้ Pop-up โชว์ตัว
        page.bring_to_front() 
        page.wait_for_timeout(1500) # รอแอนิเมชัน Pop-up เด้งขึ้นมาให้ชัดๆ
        
        print("👉 กดยกเลิกสถานะ 'พิมพ์แล้ว' ที่หน้าหลัก...")
        try:
            # กดปุ่มยกเลิก ตาม Class ที่ฟลุ๊คให้มา
            page.locator('button.ant-btn-default:has-text("ยกเลิก")').last.click(timeout=3000)
            print("✅ กดยกเลิกสำเร็จ! รักษาออเดอร์ไว้ได้")
        except Exception:
            print("⚠️ ไม่เจอหน้าต่างถามสถานะการพิมพ์ (ข้ามไปสเต็ปต่อไป)")

        # 3. สลับแท็บกลับไปที่ 'ใบสรุป' เพื่อดูดข้อมูลต่อ
        summary_page.bring_to_front()

        summary_page.wait_for_load_state("domcontentloaded")
        summary_page.wait_for_selector('div[data-productname="product_sku"]', timeout=15000)
        summary_page.wait_for_timeout(2000) 

        # ==========================================
        # สเต็ปที่ 5: ดูดข้อมูลจากหน้าใบสรุป
        # ==========================================
        print("📥 กำลังดูดข้อมูลสินค้า...")
        products_data = summary_page.evaluate('''() => {
            let results = [];
            document.querySelectorAll('div.item_info').forEach(infoDiv => {
                let parentRow = infoDiv.closest('tr');
                if (!parentRow) parentRow = infoDiv.parentElement.parentElement; 

                let nameText = infoDiv.innerText.trim();
                let skuEl = parentRow.querySelector('div[data-productname="product_sku"]');
                let skuText = skuEl ? skuEl.innerText.trim() : "ไม่พบ SKU";
                let qtyEl = parentRow.querySelector('div[data-productname="product_sku_quantity"]');
                let qtyText = qtyEl ? qtyEl.innerText.trim() : "0";

                let orderEls = parentRow.querySelectorAll('.t_c');
                let ordersList = [];
                orderEls.forEach(orderEl => {
                    let orderText = orderEl.innerText.trim();
                    if(orderText !== "" && orderText !== "...") ordersList.push(orderText); 
                });

                results.push({"sku": skuText, "name": nameText, "total_qty": qtyText, "orders": ordersList});
            });
            return results;
        }''')
        summary_page.close() # ปิดหน้าใบสรุปไปเลย (เดี๋ยวค่อยปริ้นตอนท้าย)

        # ==========================================
        # 🧠 สเต็ปที่ 6: ส่งต่อให้ไฟล์ process_stock_and_line คิดงานให้
        # ==========================================
        # ฟังก์ชันนี้จะไปวิ่งตัด Sheets และแจ้ง LINE ให้เอง แล้วส่งลิสต์ออเดอร์กลับมาให้ตัวแปร ready_to_pack
        ready_to_pack = process_orders_and_stock(products_data)

        # ==========================================
        # 🎯 สเต็ปที่ 7: กลับมาติ๊กถูกออเดอร์พร้อมส่ง (แบบกวาดสายตาหาในหน้าเว็บ)
        # ==========================================
        if len(ready_to_pack) > 0:
            print(f"\n🎯 กลับมาที่ BigSeller: เริ่มสเต็ปติ๊กเลือก {len(ready_to_pack)} ออเดอร์ที่พร้อมส่ง...")
            
            # เคลียร์ติ๊กถูกทั้งหมดออกก่อน
            page.locator('input[name="listAllBox"]').uncheck()
            page.wait_for_timeout(1000)

            # 🚀 ทริคใหม่: ไล่หา 'บรรทัด' ที่มีเลขคำสั่งซื้อ แล้วติ๊กถูกในบรรทัดนั้นเลย (เว็บจะได้ไม่รีเฟรช)
            for order_id in ready_to_pack:
                clean_id = order_id.split(' ')[0].replace('*', '')
                print(f"🔍 กำลังหาและติ๊กออเดอร์: {clean_id}")
                
                try:
                    # หา tag <tr> (บรรทัดตาราง) ที่มีข้อความรหัสออเดอร์ แล้วสั่งเช็ค checkbox ในบรรทัดนั้น
                    row = page.locator(f'tr:has-text("{clean_id}")').first
                    row.locator('input[type="checkbox"]').first.check()
                    
                    page.wait_for_timeout(500) # พักหายใจนิดนึงให้เว็บตอบสนอง
                except Exception as e:
                    print(f"⚠️ อาเร๊ะ! หาออเดอร์ {clean_id} ไม่เจอในหน้านี้")

            # ==========================================
            # 🛡️ สเต็ปที่ 8: Dry Run เอาเมาส์ชี้ปุ่มยืนยัน
            # ==========================================
            print("\n🛡️ Dry Run: ติ๊กครบแล้ว! กำลังเอาเมาส์ไปชี้ปุ่มยืนยัน...")
            
            # หาปุ่มที่มีข้อความ ยืนยัน (จากรูปที่ 4)
            page.locator('button.ant-btn-primary:has-text("ยืนยัน")').last.hover()
            
            # ==========================================
            # 🖨️ สเต็ปสุดท้าย: แจ้งปริ้น
            # ==========================================
            print("💡 บอทเลือกออเดอร์พร้อมส่งสะสมไว้ให้ครบแล้วครับ!")
            print("👉 ฟลุ๊คสามารถกด พิมพ์รายการสรุป (เพื่อเอาแค่ของพร้อมส่ง) หรือ กดยืนยัน ได้เลย")
            page.pause()
            
        else:
            print("\n🏁 ไม่มีออเดอร์ที่พร้อมส่งในรอบนี้")

        # browser.close()

if __name__ == "__main__":
    check_new_orders()