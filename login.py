"""浏览器鉴权状态获取脚本 — 手动登录后保存 Cookie/Session"""

from playwright.sync_api import sync_playwright


def save_login_state(platform_name: str, login_url: str, output_file: str) -> None:
    print(f"\n启动浏览器准备登录 [{platform_name}]...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print(f"正在访问登录页: {login_url}")
        page.goto(login_url)

        print("\n" + "=" * 50)
        print(f"请在弹出的浏览器窗口中，手动完成 [{platform_name}] 的登录（扫码或密码）。")
        print("确认登录成功，且页面完全加载后，请在此终端按下 [回车键] 继续...")

        input()

        context.storage_state(path=output_file)
        print(f"✅ [{platform_name}] 登录状态已成功保存到 {output_file}！")

        browser.close()


if __name__ == "__main__":
    print("请选择要获取登录凭证的平台：")
    print("1. 实习僧 (shixiseng)")
    print("2. 牛客网 (nowcoder)")

    choice = input("请输入数字 (1 或 2): ").strip()

    if choice == "1":
        save_login_state("实习僧", "https://www.shixiseng.com/", "auth_state_shixiseng.json")
    elif choice == "2":
        save_login_state("牛客网", "https://www.nowcoder.com/login", "auth_state_nowcoder.json")
    else:
        print("输入无效，请重新运行。")
