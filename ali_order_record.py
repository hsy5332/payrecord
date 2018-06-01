# -*- coding: utf-8 -*-
import time
import pymssql
import requests
from selenium import webdriver


class AutomationWeb(object):
    def __int__(self, url, submitdata):
        self.url = url

    def launchBrowser(self):
        # driver = webdriver.Firefox()
        driver = webdriver.Chrome()
        driver.get(self.url)
        return driver

    # 启动浏览器


    def runBrowser(self):
        self.url = "https://consumeprod.alipay.com/record/standard.htm"
        driver = AutomationWeb.launchBrowser(self)
        driver.implicitly_wait(30)

        # 点击交易记录
        try:
            # 点击这个月的交易记录
            driver.find_element_by_id("J-one-month").click()
        except:
            print("请扫描二维码")
            # driver.find_element_by_id("J-today").click()
            driver.find_element_by_id("J-one-month").click()

        # 相关配置参数
        refreshtime = 15;  # 页面刷新间隔时间
        executetime = 10000;  # 执行时间

        # 记录交易记录接口地址
        recordinterfaceurl = "http://www.vbenniu.com/webApI/Alidirect_Notify";
        orderid = []  # 存放订单号记录
        refreshcount = 0
        successurlcount = 1
        runtime = time.strftime("%Y-%m-%d %H:%M", time.localtime());
        while refreshcount < executetime:
            length = 0
            submitdata = []
            while length < len(driver.find_elements_by_class_name("J-item")):
                # 订单属性
                transferattribute = driver.find_elements_by_class_name("consume-title")[length].get_attribute(
                    "innerText")
                # 订单时间
                transfertimexpath = ".//*[@id='J-item-|1|']/td[2]/p[2]"
                realtransfertimexpath = transfertimexpath.split("|")[0] + str(length + 1) + \
                                        transfertimexpath.split("|")[2]

                transferdataxpath = ".//*[@id='J-item-|1|']/td[2]/p[1]"
                realtransferdataxpath = transferdataxpath.split("|")[0] + str(length + 1) + \
                                        transferdataxpath.split("|")[2]

                data = driver.find_element_by_xpath(realtransferdataxpath).get_attribute("innerText")
                if data == "今天":
                    transfertime = str(
                        time.strftime("%Y-%m-%d ") + " " + driver.find_element_by_xpath(
                            realtransfertimexpath).get_attribute(
                            "innerText"))
                elif data == "昨天":
                    transfertime = str(
                        time.strftime("%Y-%m-%d", time.localtime(int(time.time() - 86400)))
                        + " " + driver.find_element_by_xpath(realtransfertimexpath).get_attribute(
                            "innerText"))
                else:
                    transferdata = driver.find_element_by_xpath(realtransferdataxpath).get_attribute(
                        "innerText")
                    transfertime = str(
                        transferdata + " " + driver.find_element_by_xpath(realtransfertimexpath).get_attribute(
                            "innerText"))

                # 订单转账人
                transfernamexpath = ".//*[@id='J-item-|1|']/td[3]/p[2]"
                realtransfernamexpath = transfernamexpath.split("|")[0] + str(length + 1) + \
                                        transfernamexpath.split("|")[2]
                transfername = driver.find_element_by_xpath(realtransfernamexpath).get_attribute("innerText")

                # 订单转账金额
                transferamount = driver.find_elements_by_class_name("amount-pay")[length].get_attribute("innerText")

                # 订单属性
                transferstatusxpath = ".//*[@id='J-item-|1|']/td[6]/p[1]"
                realtransferstatusxpath = transferstatusxpath.split("|")[0] + str(length + 1) + \
                                          transferstatusxpath.split("|")[2]
                transferstatus = driver.find_element_by_xpath(realtransferstatusxpath).get_attribute("innerText");
                transferorder = driver.find_element_by_id("J-tradeNo-" + str(length + 1)).get_attribute("innerText");

                if transferorder not in orderid and '+' in transferamount and transfertime > runtime:
                    orderid.append(transferorder)
                    driver.find_elements_by_class_name("consume-title")[length].click()
                    newwindowslist = driver.window_handles  # 记录新开的窗口
                    driver.switch_to_window(newwindowslist[1])  # 跳转订单详情页
                    driver.switch_to_window(newwindowslist[0])  # 跳转 支付宝 交易记录页面
                    newwindowslist.pop  # 删除newwindowslist中新打开窗口的记录
                    # 抓取页面数据
                    transferstatusone = driver.find_elements_by_class_name("status")[1].get_attribute(
                        "innerText")  # 交易状态
                    transferamountone = \
                        driver.find_elements_by_class_name("amount")[0].get_attribute("innerText").split('\t')[
                            0]  # 交易金额
                    transfertimeone = \
                        driver.find_elements_by_class_name("fn-left")[2].get_attribute("innerText").replace("\t",
                                                                                                            "").split(
                            "：")[1]  # 交易时间
                    transferorderone = \
                        driver.find_elements_by_class_name("ft-gray")[1].get_attribute("innerText").split(":")[
                            1]  # 交易订单号
                    transfernameone = \
                        driver.find_elements_by_class_name("ft-gray")[0].get_attribute("innerText").split(":")[
                            1]  # 对方账户名称
                    transfernamemo = driver.find_elements_by_class_name("title")[4].get_attribute("innerText")  # 交易备注

                    recordone = {
                        "transferstatusone": transferstatusone,
                        "transferamountone": transferamountone,
                        "transfertimeone": transfertimeone,
                        "transferorderone": transferorderone,
                        "transfernameone": transfernameone,
                        "transfernamemo": transfernamemo,
                    }
                    # 记录订单给记录交易接口

                    # 判断请求 记录交易记录接口是否失败，若失败则连续请求三次，大于三次则放弃记录该记录
                    requestrecordurl = 0
                    while requestrecordurl < 3:
                        requestresult = requests.post(recordinterfaceurl, recordone)
                        if requestresult.status_code == 200:
                            requestrecordurl = 3
                            print("发送订单数据成功,目前记录的订单数: %s" % successurlcount)
                            successurlcount = successurlcount + 1
                        else:
                            requestrecordurl = requestrecordurl + 1
                            print("请求接口URL:" + recordinterfaceurl + "错误,正在尝试第 %s 连接" % (requestrecordurl))

                    print(recordone)
                    driver.close()  # 关闭订单详情页

                    # 生成字典,把数据存到列表中
                    record = {
                        "transferattribute": transferattribute,
                        "transfertime": transfertime,
                        "transfername": transfername,
                        "transferamount": transferamount.strip('+').strip(),
                        "transferstatus": transferstatus,
                        "transferorder": transferorder,
                    }
                    submitdata.append(record)

                length = length + 1
            if len(submitdata) > 0:
                try:
                    connectsql = AutomationWeb().connectDatabase(submitdata)
                    connectsql.commit()
                    connectsql.close()
                except:
                    print("连接数据库出错，尝试重新连接，可能存在数据丢失，请检查下面的数据是否存入数据库")
                    print(transferorder)
            refreshcount = refreshcount + 1;
            time.sleep(refreshtime)
            driver.refresh();

    # 执行浏览器

    def connectDatabase(self, submitdata):
        sqlserverlink = "106.14.144.68"
        username = "sa"
        password = "win@2008"
        database = "alipay_order_record"
        connectsql = pymssql.connect(sqlserverlink, username, password, database)
        cursor = connectsql.cursor()
        executecount = 0
        while executecount < len(submitdata):
            cursor.execute("INSERT INTO ali_record  VALUES ('%s','%s','%s','%s','%s','%s','%s')" % (
                submitdata[executecount].get("transferattribute"),
                submitdata[executecount].get("transfertime"),
                submitdata[executecount].get("transfername"),
                submitdata[executecount].get("transferamount"),
                submitdata[executecount].get("transferstatus"),
                submitdata[executecount].get("transferorder"),
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            ))
            print("提交的订单号为：" + submitdata[executecount].get("transferorder"))
            executecount = executecount + 1
        return connectsql


if __name__ == "__main__":
    AutomationWeb().runBrowser()
