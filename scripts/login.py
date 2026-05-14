from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.cloudcampus.com.cn/")

    # 等待手动登录
    input("登录完成后按回车...")

    # 保存登录状态
    context.storage_state(path="auth.json")
    print("已保存 auth.json")
    browser.close()
