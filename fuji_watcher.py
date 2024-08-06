#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/29 19:27
@Author  : claudexie
@File    : demo.py
@Software: PyCharm
"""
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from xml.etree import ElementTree


FLICK_START_X = 300
FLICK_START_Y = 300
FLICK_DISTANCE = 700
SCROLL_SLEEP_TIME = 1


class JDAppOperator:
    def __init__(self):
        """
        初始化
        """
        capabilities = dict(
            platformName='Android',
            automationName='uiautomator2',
            deviceName='BH901V3R9E',
            appPackage='com.jingdong.app.mall',  # 微信的包名
            appActivity='main.MainActivity',  # 微信的启动活动
            noReset=True,  # 不重置应用的状态
            fullReset=False,  # 不完全重置应用
            forceAppLaunch=True  # 强制重新启动应用

        )
        appium_server_url = 'http://localhost:4723'
        self.cache_file = "items.txt"

        print('Loading driver...')
        driver = webdriver.Remote(appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))
        self.driver = driver
        print('Driver loaded successfully.')
        self.cur_item_name_set = set()


    def enter_item_list(self):
        """
        进入收藏店铺的商品页面
        :return:
        """
        # 使用显式完全加载
        for index in range(10):
            print(f"{index} time:")
            try:
                WebDriverWait(self.driver, 60).\
                    until(expected_conditions.presence_of_element_located((AppiumBy.XPATH, '//*[@text="我的"]'))).click()
                break
            except Exception as error:
                # 可能因为广告导致错误，重试一次
                print(error)
                time.sleep(1)
                continue

        WebDriverWait(self.driver, 60). \
            until(expected_conditions.presence_of_element_located((AppiumBy.XPATH, '//*[@text="商品收藏"]'))).click()

        WebDriverWait(self.driver, 60). \
            until(expected_conditions.presence_of_element_located((AppiumBy.XPATH, '//*[@text="店铺"]'))).click()

        WebDriverWait(self.driver, 60). \
            until(expected_conditions.presence_of_element_located((AppiumBy.XPATH,
                                                                   '//*[@text="富士（FUJIFILM）京东自营旗舰店"]'))).click()

        WebDriverWait(self.driver, 60). \
            until(expected_conditions.presence_of_element_located((AppiumBy.XPATH, '//*[@text="商品"]'))).click()

        WebDriverWait(self.driver, 60). \
            until(expected_conditions.presence_of_element_located((AppiumBy.XPATH, '//*[@text="仅看有货"]'))).click()

        print(f"enter item list successfully")

    def scroll(self):
        # 模拟拖动
        self.driver.swipe(FLICK_START_X, FLICK_START_Y + FLICK_DISTANCE, FLICK_START_X, FLICK_START_Y)
        time.sleep(1)

    def get_all_items(self):
        # 解析商品名，价格，店名
        print('开始爬取商品信息')
        all_item_name_set = set()
        while True:
            WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_element_located((AppiumBy.ID, 'com.jd.lib.jshop.feature:id/wk'))
            )
            shop_item_name_list = self.find_shop_item_name_list()
            shop_item_name_set = set(shop_item_name_list)
            # print(f"all_item_name_set: {all_item_name_set}")
            # print(f"shop_item_name_set: {shop_item_name_set}")
            if shop_item_name_set.issubset(all_item_name_set):
                break
            else:
                # 发现了新的商品，继续检查
                all_item_name_set.update(shop_item_name_set)
                pass
            self.scroll()
        print(">>>>>>>>>>")
        for e in all_item_name_set:
            print(e)
        return list(all_item_name_set)

    def find_shop_item_name_list(self):
        """
        获取商品清单
        :return:
        """
        shop_item_name_list = []
        # 获取当前页面的 XML 结构
        page_source = self.driver.page_source
        # 解析 XML
        tree = ElementTree.fromstring(page_source)
        # 查找所有元素
        all_elements = tree.findall(".//*")
        for element in all_elements:
            resource_id = element.attrib.get('resource-id', 'N/A')
            text = element.attrib.get('text', 'N/A')
            # class_name = element.attrib.get('class', 'N/A')
            # content_desc = element.attrib.get('content-desc', 'N/A')
            # bounds = element.attrib.get('bounds', 'N/A')
            # focusable = element.attrib.get('focusable', 'N/A')
            # enabled = element.attrib.get('enabled', 'N/A')
            clickable = element.attrib.get('clickable', 'false')
            if resource_id == "com.jd.lib.jshop.feature:id/wk":
                # print(element)
                shop_item_name_list.append(text)
            else:
                pass
                # print(f"Resource ID: {resource_id}, Text: {text}, Class: {class_name}, Content-desc: {content_desc}, "
                #       f"Bounds: {bounds}, Clickable: {clickable}, Focusable: {focusable}, Enabled: {enabled}")
        return shop_item_name_list

    def print_clickable_elements(self):
        # 获取当前页面的 XML 结构
        page_source = self.driver.page_source
        # 解析 XML
        tree = ElementTree.fromstring(page_source)
        # 查找所有元素
        all_elements = tree.findall(".//*")
        print("Clickable elements on the current page:")
        for elem in all_elements:
            clickable = elem.attrib.get('clickable', 'false')
            resource_id = elem.attrib.get('resource-id', 'N/A')
            text = elem.attrib.get('text', 'N/A')
            class_name = elem.attrib.get('class', 'N/A')
            content_desc = elem.attrib.get('content-desc', 'N/A')
            bounds = elem.attrib.get('bounds', 'N/A')
            focusable = elem.attrib.get('focusable', 'N/A')
            enabled = elem.attrib.get('enabled', 'N/A')
            if clickable == 'true':
                print(f"**Resource ID: {resource_id}, Text: {text}, Class: {class_name}, Content-desc: {content_desc}, "
                      f"Bounds: {bounds}, Clickable: {clickable}, Focusable: {focusable}, Enabled: {enabled}")
            else:
                print(f"Resource ID: {resource_id}, Text: {text}, Class: {class_name}, Content-desc: {content_desc}, "
                      f"Bounds: {bounds}, Clickable: {clickable}, Focusable: {focusable}, Enabled: {enabled}")

    def close(self):
        self.driver.quit()
        print('Driver closed.')

    def save_list_to_local_file(self):
        """
        缓存商品列表到本地文件
        :return:
        """
        # 打开文件并写入列表内容
        with open(self.cache_file, "w") as file:
            for item in self.cur_item_name_set:
                file.write(item + "\n")
        print(f"列表内容已写入到 {self.cache_file}")

    def load_list_from_local_file(self):
        """
        从本地文件中读取缓存数据
        :return:
        """
        # 初始化一个空列表
        my_list = []

        # 打开文件并读取内容
        with open(self.cache_file, "r") as file:
            for line in file:
                # 去除每行末尾的换行符，并将其添加到列表中
                my_list.append(line.strip())

        # 打印读取到的列表
        print("读取到的列表内容：")
        print(my_list)
        return my_list

    def run(self):
        # 进去商品列表
        self.enter_item_list()

        # 滚动获取全部商品
        self.cur_item_name_set = self.get_all_items()

        self.save_list_to_local_file()

        self.load_list_from_local_file()

    def get_fuji_item_name_list(self):
        """
        获取京东富士的商品列表
        :return:
        """
        self.enter_item_list()
        return self.get_all_items()


class WXAppOperator:
    def __init__(self):
        """
        初始化
        """
        capabilities = dict(
            platformName='Android',
            automationName='uiautomator2',
            deviceName='BH901V3R9E',
            appPackage='com.tencent.mm',  # 微信的包名
            appActivity='.ui.LauncherUI',  # 微信的启动活动
            noReset=True,  # 不重置应用的状态
            fullReset=False,  # 不完全重置应用
            forceAppLaunch=True  # 强制重新启动应用

        )
        appium_server_url = 'http://localhost:4723'
        print('Loading driver...')
        driver = webdriver.Remote(appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))
        self.driver = driver
        print('Driver loaded successfully.')
        self.cur_item_name_set = set()

    def enter_chat_page(self, chat_name: str):
        """
        进入聊天窗口
        :return:
        """
        # 使用显式完全加载
        WebDriverWait(self.driver, 60).\
            until(expected_conditions.presence_of_element_located((AppiumBy.XPATH, '//*[@text="微信"]')))

        WebDriverWait(self.driver, 60). \
            until(expected_conditions.presence_of_element_located((AppiumBy.XPATH,
                                                                   f'//*[@text="{chat_name}"]'))).click()

        print(f"enter chat ui of {chat_name} successfully")

    def send_text_msg(self, msg: str):
        """
        输入文字消息并发送
        :param msg:
        :return:
        """
        input_box = WebDriverWait(self.driver, 60).until(
            expected_conditions.presence_of_element_located((AppiumBy.ID, 'com.tencent.mm:id/bkk')))

        input_box.click()

        input_box.send_keys(msg)

        WebDriverWait(self.driver, 60). \
            until(expected_conditions.presence_of_element_located((AppiumBy.XPATH, f'//*[@text="发送"]'))).click()

    def print_clickable_elements(self):
        # 获取当前页面的 XML 结构
        page_source = self.driver.page_source
        # 解析 XML
        tree = ElementTree.fromstring(page_source)
        # 查找所有元素
        all_elements = tree.findall(".//*")
        print("Clickable elements on the current page:")
        for elem in all_elements:
            clickable = elem.attrib.get('clickable', 'false')
            resource_id = elem.attrib.get('resource-id', 'N/A')
            text = elem.attrib.get('text', 'N/A')
            class_name = elem.attrib.get('class', 'N/A')
            content_desc = elem.attrib.get('content-desc', 'N/A')
            bounds = elem.attrib.get('bounds', 'N/A')
            focusable = elem.attrib.get('focusable', 'N/A')
            enabled = elem.attrib.get('enabled', 'N/A')
            if clickable == 'true':
                print(f"**Resource ID: {resource_id}, Text: {text}, Class: {class_name}, Content-desc: {content_desc}, "
                      f"Bounds: {bounds}, Clickable: {clickable}, Focusable: {focusable}, Enabled: {enabled}")
            else:
                print(f"Resource ID: {resource_id}, Text: {text}, Class: {class_name}, Content-desc: {content_desc}, "
                      f"Bounds: {bounds}, Clickable: {clickable}, Focusable: {focusable}, Enabled: {enabled}")

    def close(self):
        self.driver.quit()
        print('Driver closed.')


if __name__ == '__main__':
    # 初始化京东APP的操作
    operator = JDAppOperator()
    fuji_item_name_list = operator.get_fuji_item_name_list()
    operator.close()

    # 如果发现100V，则发消息给我
    up_for_send_item_list = []
    for item_name in fuji_item_name_list:
        if "X100V" in item_name or "XT5" in item_name or "XT50" in item_name:
            up_for_send_item_list.append(item_name)
    if up_for_send_item_list:
        msg = "[发现关注相机上架]\n" + "\n".join(up_for_send_item_list)
        wx_operator = WXAppOperator()
        wx_operator.enter_chat_page("富士相机")
        wx_operator.send_text_msg(msg)
        wx_operator.close()
    else:
        print(f"无关注的商品: {len(fuji_item_name_list)}")

