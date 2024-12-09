import requests
import database
import re
import json
import time
import date_change

TOKEN = "Bot 1/MzM4NzQ=/1waJJzIp1/TPECHSCdxGHA=="
HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
    }
URL = 'https://www.kookapp.cn'
    
def get_msg_list():
    ##获取bot频道的消息列表
    api_url=URL+"/api/v3/message/list?target_id=1678490266013327"
    try :
        response = requests.get(api_url,headers=HEADERS)
        if response.status_code == 200:
            response_json = response.json()
            msg_items = response_json['data']['items']
            print(f"成功获得消息列表")
            return msg_items
        else:
            print(f"请求失败，状态码：{response.status_code}\n")
            raise ValueError
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误: {http_err}")
        return 'error'
    except requests.exceptions.RequestException as err:
        print(f"请求错误: {err}")
        return 'error'
    except ValueError as json_err:
        print(f'解析错误:{json_err}')
        return 'error'
    
def post_msg(content):
    
    api_url = URL+'/api/v3/message/create'
    data = {
        "target_id":"1678490266013327",
        "type": 9,
        "content":content
}
    data = json.dumps(data)
    
    try :
        response = requests.get(api_url,data=data,headers=HEADERS)
        if response.status_code == 200:
            response_json = response.json()
            print(f"{response_json}")
            # msg_items = response_json['data']['items']
            return True
        else:
            print(f"请求失败，状态码：{response.status_code}\n")
            raise ValueError
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误: {http_err}")
        return 'error'
    except requests.exceptions.RequestException as err:
        print(f"请求错误: {err}")
        return 'error'
    except ValueError as json_err:
        print(f'解析错误:{json_err}')
        return 'error'


last_msg_time = 0
#记录最后一个消息的时间

while True:
#主循环 每五秒拉取一次信息并判断是否需要处理
    try:
        msg_list=get_msg_list()
    except:
        print("获取消息队列时发生错误")
    if last_msg_time == 0 :
        last_msg_time = msg_list[-1]['create_at']
        continue
    for msg_item in msg_list:
        if msg_item['create_at'] > last_msg_time:
            content = msg_item['content']
            match=re.match(r'item#(.*)',content)
            if match:
            # 对符合正则表达式的玩家信息进行回应
            # TODO: 获取content后面的信息
                itemName_to_query = match.group(1)
                responce_rows=database.query(itemName_to_query)
            #找到信息后回复该玩家
                responce_content = ''
                if len(responce_rows) > 30 :
                    responce_content = '模糊查询结果超过30个，请重新使用范围更小的查询字符串,例如"禅师级背包"而不是"背包"'
                else :
                    for row in responce_rows:
                        update_time = date_change.timestamp_to_date(row[6])
                        responce_content += f'{row[5]}: 品质:{row[2]}.{row[3]} 价格{row[4]:,} 最后一次更新:{update_time}\n'
                if responce_content == '':
                    responce_content = '查询结果为空，原因可能有:\n数据库暂未更新\n机器人本地化信息缺失\n查询内容有误'
                post_msg(responce_content)
                
    last_msg_time = msg_list[-1]['create_at']
    time.sleep(5)