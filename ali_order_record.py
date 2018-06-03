# -*- coding: utf-8 -*-
import time
import pymssql
import requests
from selenium import webdriver


class AutomationWeb(object):
    def __int__(self, url, submitdata):
        self.url = url

    def launchBrowser(self):
        driver = webdriver.Chrome()
        driver.get(self.url)
        return driver

    # 启动浏览器


    def runBrowser(self):

        # 相关配置参数
        refreshtime = 5;  # 页面刷新间隔时间
        executetime = 10000;  # 执行时间
        memo = "13197515498"  # 收款人账号
        QRcodetime = 30  # 二维码等待时间

        self.url = "https://consumeprod.alipay.com/record/standard.htm"
        driver = AutomationWeb.launchBrowser(self)

        # 点击交易记录
        try:
            # 点击这个月的交易记录
            time.sleep(QRcodetime)
            driver.find_element_by_id("J-one-month").click()

        except:
            print("请扫描二维码")
            time.sleep(QRcodetime)
            # driver.find_element_by_id("J-today").click()
            driver.find_element_by_id("J-one-month").click()

        # 记录交易记录接口地址
        recordinterfaceurl = "http://www.vbenniu.com/webApI/Alidirect_Notify";
        orderid = []  # 存放订单号记录
        refreshcount = 0
        successurlcount = 1
        runtime = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        print("开始运行时间:" + str(int(time.time())))
        while refreshcount < executetime:
            length = 0
            submitdata = []
            refreshexceptioncount = 0
            refreshexception = driver.find_elements_by_class_name("ui-tip-content")

            if len(driver.find_elements_by_class_name("qrcode-info")) > 0:
                try:
                    if "qrcode-info" in driver.find_elements_by_class_name("qrcode-info")[0].get_attribute("innerText"):
                        time.sleep(QRcodetime)  # 每次刷新页面判断页面是否有二维码图片，如同有则等待30s
                except:
                    pass

            # 判断页面是否有异常信息,若有则点击交易记录
            if len(refreshexception) > 0:
                try:
                    if "由于系统异常，暂不能进行此操作" in refreshexception[0].get_attribute("innerText"):
                        while refreshexceptioncount < len(driver.find_elements_by_tag_name('a')):
                            if "交易记录" in str(
                                    driver.find_elements_by_tag_name('a')[refreshexceptioncount].get_attribute(
                                        "innerText")):
                                print("出现异常时间:", str(int(time.time())))
                                driver.find_elements_by_tag_name('a')[refreshexceptioncount].click()
                            refreshexceptioncount = refreshexceptioncount + 1
                except:
                    time.sleep(10)

            while length < len(driver.find_elements_by_class_name("J-item")):
                # 订单属性
                transfernamemo = driver.find_elements_by_class_name("consume-title")[length].get_attribute(
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
                        time.strftime("%Y-%m-%d ") + "" + str(driver.find_element_by_xpath(
                            realtransfertimexpath).get_attribute(
                            "innerText").strip(" ")))
                elif data == "昨天":
                    transfertime = str(
                        time.strftime("%Y-%m-%d", time.localtime(int(time.time() - 86400)))
                        + " " + str(driver.find_element_by_xpath(realtransfertimexpath).get_attribute(
                            "innerText")).strip(" "))
                else:
                    transferdata = driver.find_element_by_xpath(realtransferdataxpath).get_attribute(
                        "innerText")
                    transfertime = str(
                        transferdata + driver.find_element_by_xpath(realtransfertimexpath).get_attribute(
                            "innerText"))

                # 订单转账人
                transfernamexpath = ".//*[@id='J-item-|1|']/td[3]/p[2]"
                realtransfernamexpath = transfernamexpath.split("|")[0] + str(length + 1) + \
                                        transfernamexpath.split("|")[2]
                transfername = str(driver.find_element_by_xpath(realtransfernamexpath).get_attribute("innerText"))

                # 订单转账金额
                transferamount = driver.find_elements_by_class_name("amount-pay")[length].get_attribute("innerText")

                # 订单属性
                transferstatusxpath = ".//*[@id='J-item-|1|']/td[6]/p[1]"
                realtransferstatusxpath = transferstatusxpath.split("|")[0] + str(length + 1) + \
                                          transferstatusxpath.split("|")[2]
                transferstatus = driver.find_element_by_xpath(realtransferstatusxpath).get_attribute("innerText");

                # 验证是否能够获取到订单详情按钮,若没有则获取最后详情的URL

                transferorderxpath = ".//*[@id='J-tradeNo-|4|']"
                readtransferorderxpath = transferorderxpath.split('|')[0] + str(length + 1) + \
                                         transferorderxpath.split('|')[2]

                transferorderid = str(driver.find_element_by_xpath(readtransferorderxpath).get_attribute("title"))

                if transferorderid not in orderid and '+' in transferamount and transfertime > runtime and "天弘基金管理有限公司" not in transfername:

                    orderid.append(transferorderid)
                    record = {
                        "transfernamemo": transfernamemo,
                        "transfertime": transfertime,
                        "transfername": transfername,
                        "transferamount": transferamount.strip('+').strip(),
                        "transferstatus": transferstatus,
                        "transferorderid": transferorderid,
                    }
                    submitdata.append(record)

                    # 记录订单给记录交易接口

                    # 判断请求 记录交易记录接口是否失败，若失败则连续请求三次，大于三次则放弃记录该记录
                    requestrecordurl = 0
                    while requestrecordurl < 3:
                        try:
                            requestdata = {
                                "Gateway": "alipay",  # 付款类型
                                "alipay_account": "13197515498",
                                "memo": memo,  # 收款人账号
                                "title": transfernamemo,  # 备注
                                "Payaccount": transfername,  # 付款人账号
                                "Money": transferamount.strip('+').strip(),  # 金额
                                "tradeNo": transferorderid,  # 订单号
                            }
                            requestresult = requests.post(recordinterfaceurl, requestdata)
                            if requestresult.status_code == 200:
                                requestrecordurl = 3
                                print("发送订单数据成功,目前记录的订单数: %s" % successurlcount)
                                successurlcount = successurlcount + 1
                            else:
                                requestrecordurl = requestrecordurl + 1
                                print("请求接口URL:" + recordinterfaceurl + "错误,正在尝试第 %s 连接" % (requestrecordurl))
                        except:
                            print("接口提交数据失败")

                length = length + 1
            if len(submitdata) > 0:
                # 数据库提交数据
                try:
                    connectsql = AutomationWeb().connectDatabase(submitdata)
                    connectsql.commit()
                    connectsql.close()
                except:
                    print("连接数据库出错，尝试重新连接，可能存在数据丢失，请检查下面的数据是否存入数据库")
                    print(transferorderid)
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
                submitdata[executecount].get("transfernamemo"),
                submitdata[executecount].get("transfertime"),
                submitdata[executecount].get("transfername"),
                submitdata[executecount].get("transferamount"),
                submitdata[executecount].get("transferstatus"),
                submitdata[executecount].get("transferorderid"),
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            ))
            print("提交的订单号为：" + submitdata[executecount].get("transferorderid"))
            executecount = executecount + 1
        return connectsql


if __name__ == "__main__":
    AutomationWeb().runBrowser()
