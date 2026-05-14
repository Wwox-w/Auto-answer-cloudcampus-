from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()

    # 打开首页，你自己导航到答题页面
    page.goto("https://www.cloudcampus.com.cn/")
    input("请手动导航到答题页面，确保题目已加载，然后按回车...")

    html = page.content()
    with open("quiz_page.html", "w", encoding="utf-8") as f:
        f.write(html)

    page.screenshot(path="quiz_page.png", full_page=True)
    print("已保存 quiz_page.html 和 quiz_page.png")
    browser.close()
