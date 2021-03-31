import json
import os


# 每一次重新使用前最好删除log.txt 文件


class Cookies(object):

    def saveCookies(self, driver):
        cookies = driver.get_cookies()
        """
        # 新版本的chromedrive拒绝了"expiry value"（到期密钥）。
        # 删除 expiry cookie
        """
        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie['expiry']

        os.makedirs('cookies', exist_ok=True)

        with open('cookies/log.txt', 'w') as f:
            json.dump(cookies, f)

    def getCookies(self):
        try:
            with open('cookies/log.txt', 'r') as f:
                js = json.load(f)
                return js
        except Exception:
            return None
