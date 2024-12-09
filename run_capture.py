import udp_capture
import database

database.creatDB()
#创建数据库（如果不存在）
udp_capture.core_capture()
#运行capture