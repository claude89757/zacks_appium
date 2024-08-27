#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/8/9 20:06
@Author  : claudexie
@File    : x_watcher.py
@Software: PyCharm
"""
import time
import os
import pickle
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup



class TwitterWatcher:
    def __init__(self, driver_path, username, password, timeout=10, cookies_file='cookies.pkl'):
        self.driver_path = driver_path
        self.username = username
        self.password = password
        self.timeout = timeout
        self.interaction_timeout = 600
        self.cookies_file = cookies_file
        self.driver = None

    def setup_driver(self):
        service = Service(self.driver_path)
        chrome_options = Options()
        chrome_options.add_argument("--lang=en")
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def teardown_driver(self):
        if self.driver:
            self.driver.quit()

    def print_page_source(self):
        if self.driver:
            # 使用BeautifulSoup格式化HTML源代码
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            formatted_html = soup.prettify()
            print(formatted_html)

    def find_element(self, by, value):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def save_cookies(self):
        with open(self.cookies_file, 'wb') as file:
            pickle.dump(self.driver.get_cookies(), file)

    def load_cookies(self):
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, 'rb') as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)

    def login(self):
        print(f"try to login...")
        self.driver.get('https://twitter.com/login?lang=en')

        username_input = self.find_element(By.XPATH, '//input[@name="text" and @autocomplete="username"]')
        username_input.send_keys(self.username)

        try:
            # 点击“下一步”按钮
            next_button = self.find_element(By.XPATH, '//span[text()="Next"]/ancestor::button[@role="button"]')
            print(f"click {next_button.text}")
            next_button.click()
        except Exception as error:
            print(error)
            # 适配中文版本
            next_button = self.find_element(By.XPATH, '//span[text()="下一步"]/ancestor::button[@role="button"]')
            print(f"click {next_button.text}")
            next_button.click()

        # 暂停脚本执行, 人工操作登录，等待浏览器页面变成home页面
        print("Waiting for the home page to load...")
        WebDriverWait(self.driver, self.interaction_timeout).until(
            EC.url_to_be('https://x.com/home')
        )

        self.save_cookies()
        print(f"login successfully")

    def search(self, query):
        self.driver.get('https://twitter.com/home')
        search_input = self.find_element(By.XPATH, '//input[@aria-label="Search query"]')
        search_input.send_keys(query)
        search_input.send_keys(Keys.RETURN)

    def get_top_n_posts(self, n):
        tweets = []
        scroll_attempts = 0
        max_scroll_attempts = 30

        while len(tweets) < n and scroll_attempts < max_scroll_attempts:
            tweet_elements = self.driver.find_elements(By.XPATH,
                                                       '//div[@data-testid="cellInnerDiv"]//article[@role="article"]')
            print(f"Scroll attempt {scroll_attempts + 1}: Found {len(tweet_elements)} tweets")

            for tweet in tweet_elements:
                if tweet not in tweets:
                    tweets.append(tweet)
                    if len(tweets) >= n:
                        break

            if len(tweets) < n:
                self.scroll_page()
                scroll_attempts += 1
                time.sleep(2)
            else:
                break
        print(f"Final: Found {len(tweets)} tweets.")
        return self.filter_posts(tweets)

    def collect_comments_and_user_data(self, max_comments=50):
        comments_data = []
        comments_collected = 0
        scroll_attempts = 0
        max_scroll_attempts = 10

        while comments_collected < max_comments and scroll_attempts < max_scroll_attempts:
            comments = self.driver.find_elements(By.XPATH, '//article[@role="article" and @data-testid="tweet"]')
            for comment in comments:
                if comments_collected >= max_comments:
                    break
                try:
                    # 获取用户名称
                    user_element = comment.find_element(By.XPATH, './/div[@data-testid="User-Name"]')
                    user_name = user_element.find_element(By.XPATH, './/span').text

                    # 获取评论内容
                    content = comment.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text

                    comments_data.append({
                        'user_name': user_name,
                        'content': content
                    })
                    comments_collected += 1
                except Exception as e:
                    print("failed:")

            if comments_collected < max_comments:
                self.scroll_page()
                scroll_attempts += 1
            print(f"comments_collected: {comments_collected}")
            for comment in comments_data:
                print(comment)
        print(f"Collected {comments_collected} comments.")
        return comments_data

    def scroll_page(self):
        try:
            scroll_pause_time = random.uniform(1, 3)  # 随机暂停时间
            scroll_distance = random.randint(500, 1500)  # 随机滚动距离

            self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
            time.sleep(scroll_pause_time)
            print(f"Scrolled the page by {scroll_distance} pixels and paused for {scroll_pause_time} seconds.")
        except Exception as e:
            print(f"Failed to scroll the page: {e}")

    def scroll_to_top(self):
        try:
            scroll_pause_time = random.uniform(1, 3)  # 随机暂停时间

            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(scroll_pause_time)
            print(f"Scrolled to the top of the page and paused for {scroll_pause_time} seconds.")
        except Exception as e:
            print(f"Failed to scroll to the top of the page: {e}")

    def filter_posts(self, tweets):
        # 预留的推特过滤函数
        # 在这里添加你的推特过滤逻辑
        return tweets

    def filter_comment(self, user, content):
        # 预留的评论过滤函数
        # 在这里添加你的评论过滤逻辑
        return True

    def enter_post(self, post_element):
        """
        进入推特内容详情
        :return:
        """
        # 获取推文元素的尺寸
        width = post_element.size['width']
        height = post_element.size['height']

        # 使用 JavaScript 在推文元素的右上角触发点击事件
        self.driver.execute_script("""
                          var element = arguments[0];
                          var x = arguments[1];
                          var y = arguments[2];
                          var clickEvent = new MouseEvent('click', {
                              view: window,
                              bubbles: true,
                              cancelable: true,
                              clientX: x,
                              clientY: y
                          });
                          element.dispatchEvent(clickEvent);
                      """, post_element, width - 1, 1)  # 右上角的坐标 (width-1, 1)

    def run(self, search_key_word: str):
        try:
            self.setup_driver()
            # 检查是否存在 cookies 文件
            if os.path.exists(self.cookies_file):
                try:
                    self.driver.get('https://twitter.com/home')
                    self.load_cookies()
                    self.driver.refresh()
                    time.sleep(3)
                except Exception as error:
                    print(error)
                    print("Cookies are invalid, clearing cookies and re-login.")
                    self.driver.delete_all_cookies()
                    self.login()
            else:
                self.login()
            # 混淆: 随机等待时间
            time.sleep(random.uniform(1, 3))

            # 再次检查是否需要登录
            if "home" in self.driver.current_url:
                print("success.............")
            else:
                raise Exception(f"login failed: {self.driver.current_url}")

            # 搜索关键字
            self.search(search_key_word)

            max_check_post_num = 5
            for index in range(1, max_check_post_num+1):
                print(f"checking post [{index}] >>>>>>>>>>>>>>>>>>>")
                # 获取前N个推特
                top_n_posts = self.get_top_n_posts(index)
                check_post = top_n_posts[index-1]
                try:
                    self.enter_post(check_post)
                    time.sleep(3)  # 等待页面加载
                    self.collect_comments_and_user_data()
                    self.driver.back()
                    time.sleep(3)  # 等待页面返回
                except Exception as e:
                    print(f"Failed to process tweet: {e}")
                    time.sleep(506060)
                # 返回顶端
                self.scroll_to_top()
        finally:
            self.teardown_driver()


if __name__ == "__main__":
    chrome_driver_path = '/usr/local/bin/chromedriver'
    username = 'claude89757@gmail.com'
    password = 'your_password'

    search_key_word = "cat"

    watcher = TwitterWatcher(chrome_driver_path, username, password)
    watcher.run(search_key_word)
