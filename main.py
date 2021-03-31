import json
import os
import re
import time
from telnetlib import EC

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from Cookies import Cookies

cks = Cookies()

url = 'http://www.cfh.ac.cn'
# Create a new instance of the Firefox driver

root = 'E:\chromedriver\chromedriver.exe'

driver = webdriver.Chrome(executable_path=root)

driver.implicitly_wait(10)  # 隐性等待，最长等30秒

# 获取cookie跳过登录 第一次登陆最好删除Cookies 文件手动登陆
cookies = cks.getCookies()

if cookies is None:
    driver.get(url)
    el = driver.find_element_by_link_text("登录")
    el.click()

    el = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolderContent_TxtUserIdent"]')
    el.send_keys("your cfh 账号")
    el = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolderContent_TxtPsw"]')
    el.send_keys("密码")
    el = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolderContent_BtnLogin"]')
    el.click()
    # 10秒时间输入验证码 点击登陆
    time.sleep(10)
    # 正常登录得到 “自然图库” 定位不同
    el = driver.find_element_by_xpath('//*[@id="aspnetForm"]/div[3]/a[2]')
    el.click()

else:
    driver.get(url)
    for i in cookies:
        driver.add_cookie(i)
    # 一定要刷新一下
    driver.refresh()
    # 跳过登录的 “自然图库” 的定位

    el = driver.find_element_by_xpath('//*[@id="sitechannels"]/div/a[2]')
    el.click()

# go to the google home page

# 获取cookies 用于下次跳过登录
cks.saveCookies(driver)

el = driver.find_element_by_xpath('//*[@id="spQuery"]')
el.click()

# 查询

el = driver.find_element_by_xpath('//*[@id="k"]')
el.send_keys('盆栽')

el = driver.find_element_by_xpath('//*[@id="btnQuery"]')
el.click()

# //*[@id="AlbumsBody"]/div[16]/div[1]/a/img
el = driver.find_element_by_xpath('//*[@id="AlbumsBody"]/div[16]/div[1]/a/img')
el.click()

time.sleep(2)

tags = driver.window_handles
driver.switch_to_window(tags[1])

# 获取源码

# print(driver.page_source)
# print(driver.title)

# 获取当前相册 图片数量
n = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder_body_labPageMsg_Top"]')
text = n.text
pattern = re.compile(r"\d*\/\d*")
# print(pattern.search(text))
p = pattern.search(text).group()
nums = p.split('/')
currentpage = int(nums[0])
totalpages = int(nums[1])

while currentpage <= totalpages:
    print(currentpage)

    els = driver.find_elements_by_class_name('photoItem')

    for e in els:
        # 判别是否有详细鉴定
        try:
            mark = e.find_element_by_class_name('specimen_mark')
        except Exception:
            continue
        if mark.get_attribute('src') != 'http://www.cfh.ac.cn/images/label.png':
            continue

        # # print(img.get_attribute('src'))
        # href = img.get_attribute('src')
        name = e.find_element_by_class_name('photoCName').find_element_by_tag_name('span').text
        latin = e.find_element_by_class_name('LatinName')
        latiname = latin.text
        latin.click()

        # 跳转页面
        tags = driver.window_handles
        driver.switch_to_window(tags[2])

        # 查找相册数量
        el = driver.find_element_by_xpath('//*[@id="SpPhotoCountLabel"]')

        pattern = re.compile(r"\d*")
        # print(pattern.search(text))
        pages = pattern.search(el.text).group()
        pages = int(pages)
        if pages <= 0:
            driver.close()
            driver.switch_to_window(tags[1])
            continue
        el.click()
        tags = driver.window_handles
        driver.switch_to_window(tags[3])
        # 爬取当前页面的所有元素
        items = driver.find_elements_by_class_name('photoItem')

        address = {}
        i = 1
        for it in items:

            src = it.find_element_by_class_name('smallphoto')
            # print(src.get_attribute('src'))
            href = src.get_attribute('src')
            # print(name, ',', latiname, ',', href)

            address[i] = href
            i += 1

        os.makedirs('img/' + latiname + '-' + name, exist_ok=True)
        with open('img/' + latiname + '-' + name + '/1.json', 'w') as f:
            json.dump(address, f)

        # 爬完图片回到原来相册

        driver.close()
        driver.switch_to_window(tags[2])
        driver.close()
        driver.switch_to_window(tags[1])

    currentpage += 1
    # 跳转下一页

    try:
        next = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder_body_ImgBtnNext"]')
        next.click()
        time.sleep(2)
    except Exception:
        break

#


# # the page is ajaxy so the title is originally this:
# print(driver.title)
#
# # find the element that's name attribute is q (the google search box)
# inputElement = driver.find_element_by_name("q")
#
# # type in the search
# inputElement.send_keys("cheese!")
#
# # submit the form (although google automatically searches now without submitting)
# inputElement.submit()

try:
    # we have to wait for the page to refresh, the last thing that seems to be updated is the title
    WebDriverWait(driver, 10).until(EC.title_contains("cheese!"))

    # You should see "cheese! - Google Search"
    print(driver.title)

finally:
    driver.quit()
