import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime

import os
import csv

# 創建 ChromeOptions 對象
chrome_options = Options()
chrome_options.add_argument("--headless")  # 啟用背景執行模式

# 初始化瀏覽器驅動程式
driver = webdriver.Chrome(options=chrome_options)

# 設定重複執行的次數
repeat_count = 43800

# 創建一個空字典，用於存儲每個幣種的資費紀錄
funding_records = {}

# 使用迴圈重複執行程式碼
for _ in range(repeat_count):
    try:
        # 前往目標網頁
        driver.get("https://www.coinglass.com/zh-TW/FundingRate")

        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@class='symbol-name']")
            )
        )

        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//a[contains(@class, 'shou')]")
            )
        )

        # 滾動網頁到展開按鈕可見位置
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)

        # 按下展開按鈕
        # input("等我按enter")
        expand_button = None
        while expand_button is None:
            try:
                expand_button = driver.find_element(
                    By.XPATH, "//*[@id='__next']/div[2]/div[1]/div[1]/div/div[5]/button"
                )
                # print(expand_button)
                # input("等我按enter")
                # expand_button.click()
                button_text = expand_button.get_attribute("innerText")

                if button_text == "查看全部":
                    # rect = expand_button.rect
                    # print("元素在網頁的高度：", rect["height"])
                    # input("等我按enter")
                    print("按鈕尚未點擊，點擊展開")
                    expand_button.click()
                    break
                # <button class="MuiButton-root MuiButton-variantSoft MuiButton-colorNeutral MuiButton-sizeMd cg-style-hmmqp3" type="button">查看全部</button>
                elif button_text == "收起":
                    print("展開按鈕已被按過，不用點擊")
                    break
                # <button class="MuiButton-root MuiButton-variantSoft MuiButton-colorNeutral MuiButton-sizeMd cg-style-hmmqp3" type="button">收起</button>
            except NoSuchElementException:
                print("找不到展開按鈕，重試中...")
                driver.execute_script("window.scrollTo(0, 32)")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

        # 等待一段時間
        time.sleep(1.2)

        # 建立空的結果列表
        result = []

        # 設定資費門檻
        fr = 0.4

        # 遍歷每個欄位
        for j in range(3, 10):
            # 使用XPath選擇器找到該欄位的表頭元素
            header_xpath = f"//*[@id='__next']/div[2]/div[1]/div[1]/div/div[4]/div/div/div/div/div[1]/table/thead/tr/th[{j}]/div/span[1]/div/div"
            print(header_xpath)
            # input("按下 Enter 鍵繼續...")
            header_element = driver.find_element(By.XPATH, header_xpath)
            header_text = header_element.text

            # 遍歷該欄位的各列
            i = 2
            while True:
                # 使用XPath選擇器找到該列的儲存格元素
                if i == 2:
                    cell_xpath = f"//*[@id='__next']/div[2]/div[1]/div[1]/div/div[4]/div/div/div/div/div[2]/table/tbody/tr[{i}]/td[{j}]/div[1]/div/a"
                else:
                    cell_xpath = f"//*[@id='__next']/div[2]/div[1]/div[1]/div/div[4]/div/div/div/div/div[2]/table/tbody/tr[{i}]/td[{j}]/div/div/a"
                # cell_xpath = f"//*[@id='__next']/div[2]/div[1]/div[1]/div/div[4]/div/div/div/div/div[2]/table/tbody/tr[{i}]/td[{j}]/div/div/a"
                # print(cell_xpath)
                # input("Enter繼續")
                try:
                    cell_element = driver.find_element(By.XPATH, cell_xpath)
                    cell_text = cell_element.text.strip("%")

                    # 檢查儲存格的數值是否超過1.5%
                    if cell_text != "-" and cell_text and abs(float(cell_text)) > fr:
                        href = cell_element.get_attribute("href")
                        print(
                            "交易所名稱:",
                            header_text,
                            "對應的代幣名稱:",
                            href.split("/")[-1],
                            "資費:",
                            cell_text,
                        )
                        result.append(
                            (
                                header_text,
                                href.split("/")[-1],
                                cell_text,
                                datetime.now(),
                            )
                        )

                    i += 1
                except NoSuchElementException:
                    print("找不到儲存格元素:", cell_xpath)
                    break

        messages = []

        # part1 印出結果並加入訊息列表
        for item in result:
            print("交易所名稱:", item[0], "代幣名稱:", item[1], "資費:", item[2])
            message = f"交易所名稱: {item[0]}\n代幣名稱: {item[1]}\n資費: {item[2]}"
            messages.append(message)

        # 將訊息列表組合成一個大訊息
        combined_message = "\n\n".join(messages)

        # 設定 Telegram Bot 的 API Token 和聊天 ID
        token = ""
        # chat_id = ""  # BOT
        # chat_id = "" #group
        chat_id = ""  # channel

        # 建立 POST 請求的 URL
        url = f"https://api.telegram.org/bot{token}/sendMessage"

        # 設定 POST 請求的參數
        params = {"chat_id": chat_id, "text": combined_message}

        # 發送 POST 請求
        response = requests.post(url, params=params)

        # 檢查回應的狀態碼
        if response.status_code == 200:
            print("訊息已成功發送到 Telegram")
        else:
            print("沒有超過" + str(fr) + "%的資費")
            current_time = datetime.now()
            print("當下時間:", current_time)

        # part2 使用迴圈遍歷每個資費異常的紀錄
        print("result is :", result)
        for item in result:
            exchange = item[0]
            token = item[1]
            funding_rate = item[2]
            timestamp = item[3].strftime("%Y-%m-%d %H:%M:%S")

            # 檢查該幣種的資費紀錄在path資料夾是否存在

            folder_path = r""  # 置換成執行電腦的路徑
            filename = os.path.join(folder_path, f"{token}_funding_records.csv")

            print("folderPath is", folder_path)
            print("filename is", filename)
            if os.path.exists(filename):
                # 如果已存在，將資費紀錄追加到該檔案中
                with open(filename, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, exchange, token, funding_rate])
                print("成功歸檔")
            else:
                # 如果不存在，創建一個新的檔案並加入資費紀錄
                with open(filename, "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        ["Timestamp", "Exchange", "Token", "FundingRate"]
                    )  # 寫入標題
                    writer.writerow(
                        [timestamp, exchange, token, funding_rate]
                    )  # 寫入第一筆紀錄
                print("成功創建新檔案並歸檔")

        # 休息一段時間，例如每次執行間隔 5 分鐘
        print("休息60秒")
        time.sleep(60)  # 300 秒 = 5 分鐘
        print("休息完了，繼續執行")
    except TimeoutException:
        print("網頁超時，重新啟動")
        driver.quit()
        time.sleep(10)
        driver = webdriver.Chrome(options=chrome_options)
        continue
    except Exception as e:
        print("An error occurred while executing JavaScript:", e)
        print("Restarting the webpage...")
        driver.quit()
        time.sleep(10)
        driver = webdriver.Chrome(options=chrome_options)
        continue

# 關閉瀏覽器驅動程式
driver.quit()
