import pyshark
import binascii
import re
import json
import pandas as pd
from pathlib import Path
import time
import database

def to_json(items_data):
    items_data = ','.join(items_data)
    regular_json_data = f"[{items_data}]"
    return regular_json_data

         
def core_capture():
    #获取udp包，并将多个Fragment还原为一个数据流
    fragments = {}
    ABN_addr = ''
    cap = pyshark.LiveCapture(interface='以太网', display_filter="udp")
    current_directory = Path(__file__).parent
    item_json_path = current_directory / 'items.json'
    with open(item_json_path,'r',encoding='utf-8') as items_file:
        items_database = json.load(items_file)
    for pkt in cap.sniff_continuously():
        

        if 'IP' in pkt and 'UDP' in pkt:
            if ABN_addr !='' and pkt.ip.src != ABN_addr:
                continue
            ip_id = pkt.ip.id  # 通过IP ID来标识分片的组
            frag_offset = int(pkt.ip.frag_offset)  # 获取分片偏移量
            more_fragments = pkt.ip.flags_mf  # 检查是否有更多分片
            data = pkt.udp.payload.binary_value  # 获取UDP的数据部分

            # 如果这是一个新片段，我们创建一个新的列表
            if ip_id not in fragments:
                fragments[ip_id] = []

            # 根据分片偏移量将数据插入到正确的位置
            while len(fragments[ip_id]) <= frag_offset:
                fragments[ip_id].append(b"")  # 填充空数据部分以保证正确的拼接

            fragments[ip_id][frag_offset] = data  # 放置当前片段数据

            # 如果没有更多的分片（MF为0），则表示这个包是最后一个分片
            if more_fragments == 'False':
                # 将所有片段合并为一个完整的数据流
                complete_data = b''.join(fragments[ip_id])
                # 完成后清除缓存，以便处理下一个IP ID的分片
                del fragments[ip_id]
                
    
                # 解码数据流转换为ascii
                ascii_data = complete_data.decode('ascii',errors='ignore')
                if "UnitPrice" in ascii_data: #寻找包含货物信息的字符串
                    ABN_addr = pkt.ip.src #记录下当前阿尔比恩服务端的ip地址
                    pattern = r'\{"Id".*?\}'#正则表达式
                    items_data = re.findall(pattern,ascii_data)
                    # print(f"黑市信息:{items_data}")
                    complete_items_data = to_json(items_data)
                    json_items_data= json.loads(complete_items_data)#解析为Json字典
                    # print(f"黑市商品信息：{json_items_data}")
                    # df = pd.DataFrame(json_items_data)
                    # print(df)
                    for item in json_items_data:
                        orderId = item['Id']
                        item_typeId = item['ItemTypeId']
                        tier = item['Tier']
                        enchantment = item['EnchantmentLevel']
                        price = item['UnitPriceSilver']//10000
                        item_name = ''
                        seller = item['SellerName']
                        buyer = item['BuyerName']
                        now = int(time.time())
                        
                        
                        for item_info in items_database:
                            if item_typeId == item_info['UniqueName']:
                                item_name = item_info['LocalizedNames']["ZH-CN"]
                        if item_name == '':
                            item_name = item_typeId    
                            
                        data_to_submit = {
                            "orderId": orderId,
                            "item_typeId" : item_typeId,
                            "tier" : tier,
                            "enchantment" : enchantment,
                            "price" : price,
                            "item_name" : item_name,
                            "now" : int(time.time()),
                        } 
                        
                        database.submit_data(data_to_submit)                                     
                        print(f"装备:{item_name}\n品质:{tier}.{enchantment} \n价格:{price:,} \n")
                        
                        

                # # 完成后清除缓存，以便处理下一个IP ID的分片
                # del fragments[ip_id]




