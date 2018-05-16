# -*- coding:utf-8  -*-
import requests
import json
import datetime
import time
import pymssql


class OrderRecord(object):
    def requestRecord(self):
        # startqueryday = time.mktime(
        #     time.strptime(str(datetime.date.today()) + " 00:00:00", "%Y-%m-%d %H:%M:%S")) + addtime

        sleeptime = 3
        currenttime = int(time.time())
        reducedtimes = currenttime + 259200
        geturlcount = 1  # 执行geturllist中数量，必须小于等于4
        submitcount = 1  # 提交次数
        orderid = []  # 订单ID
        cookieskey = "p_skey=kVogVC2yDR4mtFleZP-UrSuoGsm1o-funlWWNZa87AU_"
        urlskey = "MZuEyazgqd"
        qqnumber = "459941505"
        g_tk = "998511542"  # 订单详细最后
        onepage = "0%7C201805%7C10%7C96a3f65a20a10700cd4c2010%7C3%7C1526113174%7C100002690118051200096331552981727269%7C"
        twopage = "0%7C201805%7C10%7Cd2a0f65a20a10700cd4c2010%7C3%7C1526112466%7C100002690118051200096331252888899269%7C"
        threepage = "0%7C201805%7C10%7Cca9bf65a20a10700cd4c2010%7C3%7C1526111178%7C100002690118051200096332754344697269%7C"
        posturl = "http://pay.10min.top/webApI/Alidirect_Notify"
        print("开始运行时间：" + str(time.time()))
        while currenttime < reducedtimes:
            startqueryday = currenttime
            geturl = [(
                "https://myun.tenpay.com/cgi-bin/clientv1.0/qwallet_record_list.cgi?limit=10&offset=0&s_time=2017-05-13&ref_param=&source_type=7&time_type=%s&bill_type=0&uin=%s&skey=%s&skey_type=2" % (
                    str(
                        time.strftime("%Y%m", time.localtime(time.time()))), qqnumber, urlskey)),
                (
                    "https://myun.tenpay.com/cgi-bin/clientv1.0/qwallet_record_list.cgi?limit=10&offset=10&s_time=2017-05-13&ref_param=0%s&source_type=7&time_type=%s&bill_type=0&uin=%s&skey=%s&skey_type=2" % (
                        onepage, str(
                            time.strftime("%Y%m", time.localtime(time.time()))), qqnumber, urlskey)),
                (
                    "https://myun.tenpay.com/cgi-bin/clientv1.0/qwallet_record_list.cgi?limit=10&offset=20&s_time=2017-05-13&ref_param=0%s&source_type=7&time_type=%s&bill_type=0&uin=%s&skey=%s&skey_type=2" % (
                        twopage, str(
                            time.strftime("%Y%m", time.localtime(time.time()))), qqnumber, urlskey)),
                (
                    "https://myun.tenpay.com/cgi-bin/clientv1.0/qwallet_record_list.cgi?limit=10&offset=30&s_time=2017-05-13&ref_param=0%s&source_type=7&time_type=%s&bill_type=0&uin=%s&skey=%s&skey_type=2" % (
                        threepage, str(
                            time.strftime("%Y%m", time.localtime(time.time()))), qqnumber, urlskey)),
            ]

            heads = {
                "accept": "application/json",
                "accept-encoding": "gzip, deflate",
                "accept-language": "zh-CN,en-US;q=0.8",
                "cookie": cookieskey,
            }

            datascount = 0
            while datascount <= int(geturlcount - 1):
                datalist = []
                try:
                    onedatas = json.loads(requests.get(geturl[datascount], headers=heads).text)
                    count = 0
                    for onedata in onedatas.get("records"):
                        reducedtime = time.mktime(
                            time.strptime(str(onedata.get("create_time")), "%Y-%m-%d %H:%M:%S"))  # 把获取的数据转换成时间戳，进行对比
                        if reducedtime >= startqueryday:
                            if onedata.get("source_type") != '10' and '红包' not in onedata.get('desc'):
                                url = (
                                    "https://mqq.tenpay.com/cgi-bin/qwallet_app/qpayment_trans_detail.cgi?listid=%s&_t=%s&uin=%s&skey=%s&skey_type=2&g_tk=%s" % (
                                        str(onedata.get("sp_billno")), time.time(), qqnumber, urlskey, g_tk))
                                realdata = json.loads(requests.get(url).text)
                                if realdata.get("records")[0].get('listid') not in orderid:
                                    datalist.append(realdata.get("records")[0])
                                    orderid.append(realdata.get("records")[0].get('listid'))
                                    if len(datalist) > 0:
                                        posturlcount = 0
                                        errocount = 0
                                        while posturlcount < len(datalist):
                                            if str(datalist[posturlcount].get("payer_uin")) != qqnumber:  # 判断是不是收账人
                                                posturlrequstdata = {
                                                    "Gateway": "tenpay",
                                                    "Money": int(datalist[posturlcount].get("total_fee")) / 100,
                                                    "title": datalist[posturlcount].get("memo"),
                                                    "tradeNo": datalist[posturlcount].get("listid"),
                                                    "memo": datalist[posturlcount].get("seller_uin"),
                                                    "alipay_account": datalist[posturlcount].get("seller_uin"),
                                                    "Payaccount": datalist[posturlcount].get("payer_uin"),
                                                }
                                                print(posturlrequstdata)
                                                try:
                                                    requestResult = requests.post(posturl, posturlrequstdata)
                                                    print(requestResult.text)
                                                    posturlcount = posturlcount + 1
                                                    print("记录的订单数为：" + str(submitcount))
                                                    submitcount = submitcount + 1
                                                except:
                                                    print("请求" + posturl + "失败！，请检查原因。")
                                                    if errocount > 5:  # 判断请求URL失败次数是不是大于5，如果是则放弃。
                                                        posturlcount = len(datalist)
                                                    errocount = errocount + 1
                                                try:
                                                    connectsql = OrderRecord().connectDatabase(qqnumber, datalist)
                                                    connectsql.commit()
                                                    connectsql.close()
                                                except:
                                                    time.sleep(5)
                                                    print("连接数据库出错，尝试重新连接，可能存在数据丢失，请检查下面的数据是否存入数据库")
                                                    print(datalist)
                                            else:
                                                posturlcount = posturlcount + 1  # 不是收账人，也需要加1
                                    else:
                                        pass
                            else:
                                # 当是红包是，不处理。
                                pass
                            count = count + 1
                except:
                    print("出现请求QQURL错误时间：" + str(time.time()))
                    print(json.loads(requests.get(geturl[datascount], headers=heads).text))

                datascount = datascount + 1
            time.sleep(sleeptime)
            currenttime = currenttime + sleeptime

    def connectDatabase(self, qqnumber, data):
        sqlserverlink = "106.14.144.68"
        username = "sa"
        password = "win@2008"
        database = "alipay_order_record"
        connectsql = pymssql.connect(sqlserverlink, username, password, database)
        cursor = connectsql.cursor()
        executecount = 0
        while executecount < len(data):
            if str(data[executecount].get("payer_uin")) != qqnumber:
                cursor.execute(
                    "INSERT INTO order_record_qq  VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                        str(data[executecount].get("price")),
                        str(data[executecount].get("payer_name")),
                        str(data[executecount].get("payer_uin")),
                        str(data[executecount].get("seller_name")),
                        str(data[executecount].get("seller_uin")),
                        str(data[executecount].get("listid")),
                        str(data[executecount].get("memo")),
                        str(int(data[executecount].get("total_fee")) / 100),
                        str(data[executecount].get("transfer_eta")),
                        str(data[executecount].get("modify_time")),
                        str(data[executecount].get("create_time"))))
                print("提交的订单号为：" + str(data[executecount].get("listid")))
            executecount = executecount + 1
        return connectsql


if __name__ == "__main__":
    OrderRecord().requestRecord()

    # 目前是按一天去算，每间隔3秒钟请求一次
