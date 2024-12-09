from datetime import datetime
import time
def timestamp_to_date(timestamp):
    # 毫秒转秒
    dt = time.localtime(timestamp)
    # print(dt)
    str=time.strftime('%m-%d %H:%M:%S',dt)
    return str
    
# timestamp = 1733640471679
# timestamp_to_date(timestamp)