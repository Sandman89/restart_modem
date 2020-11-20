#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import time
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ip')
parser.add_argument('-port', '--port')
args = parser.parse_args()

ip = args.ip
port = args.port

def create_proxyauth_extension(proxy_host, proxy_port,
                               proxy_username, proxy_password,
                               scheme='http', plugin_path=None):
    """Proxy Auth Extension
    args:
        proxy_host (str): domain or ip address, ie proxy.domain.com
        proxy_port (int): port
        proxy_username (str): auth username
        proxy_password (str): auth password
    kwargs:
        scheme (str): proxy scheme, default http
        plugin_path (str): absolute path of the extension
    return str -> plugin_path
    """
    import string
    import zipfile

    if plugin_path is None:
        plugin_path = '/tmp/vimm_chrome_proxyauth_plugin.zip'

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = string.Template(
    """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "${scheme}",
                host: "${host}",
                port: parseInt(${port})
              },
              bypassList: ["foobar.com"]
            }
          };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "${username}",
                password: "${password}"
            }
        };
    }
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return plugin_path

proxyauth_plugin_path = create_proxyauth_extension(
    proxy_host="192.168.0.81",
    proxy_port=port,
    proxy_username="test",
    proxy_password="2470west"
)


co = Options()
co.add_argument("--headless")
# co.add_extension(proxyauth_plugin_path)


driver = webdriver.PhantomJS()
# driver = webdriver.Chrome(chrome_options=co)
# driver.set_page_load_timeout(20)
driver.delete_all_cookies()
driver.get("http://{}/".format(ip))
try:
    # авторизация
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'txtPwd')))
    driver.find_element_by_id('txtPwd').send_keys('admin')
    driver.find_element_by_id('btnLogin').click()
except (NoSuchElementException,TimeoutException):
    pass
try:
    time.sleep(3)
    # отключаем
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//input[@trans="disconnect"]')))
    time.sleep(1)
    driver.find_element_by_xpath('//input[@trans="disconnect"]').click()
except Exception as e:
    print(e)
finally:
    time.sleep(3)
# переход в настройки
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//a[@trans="setting"]')))
time.sleep(3)
driver.find_element_by_xpath('//a[@trans="setting"]').click()
# настройки сети
WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//a[@href="#net_setting"]')))
time.sleep(1)
driver.find_element_by_xpath('//a[@href="#net_setting"]').click()
# клик выбор сети
WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//a[@href="#net_select"]')))
time.sleep(2)
driver.find_element_by_xpath('//a[@href="#net_select"]').click()
# клик выбор сети
WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//select[@id="type"]')))
time.sleep(1)
driver.find_element_by_xpath('//select[@id="type"]').click()
time.sleep(1)
# только 3g
driver.find_element_by_xpath('.//select/option[@value="Only_WCDMA"]').click()
time.sleep(1)
driver.find_element_by_xpath('//div[@class="form-buttons"]/input[@type="button"]').click()
while True:
    time.sleep(1)
    network_type = driver.find_element_by_xpath('//span[@tiptitle="network_type"]').text
    #print(network_type)
    if network_type == 'UMTS':
        break
# только 4g
driver.find_element_by_xpath('.//select/option[@value="Only_LTE"]').click()
time.sleep(1)
driver.find_element_by_xpath('//div[@class="form-buttons"]/input[@type="button"]').click()
while True:
    time.sleep(1)
    network_type = driver.find_element_by_xpath('//span[@tiptitle="network_type"]').text
    #print(network_type)
    if network_type == 'LTE':
        break
# главная
WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//a[@href="#home"]')))
driver.find_element_by_xpath('//a[@href="#home"]').click()
time.sleep(2)
driver.find_element_by_xpath('//input[@trans="connect"]').click()
WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//input[@trans="disconnect"]')))
while True:
    if driver.find_element_by_xpath('//input[@trans="disconnect"]'):
        break
driver.quit()
print ("IP restart success")