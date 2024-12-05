import pymysql
from datetime import datetime, date
import time
import os

con = pymysql.connect(host="localhost", port=3306, user="root", passwd="1234", db="travelblog")
cmd = con.cursor()

q = "SELECT `user_lid` FROM `following` WHERE `login_id`=2"
cmd.execute(q)
res = cmd.description
print(res)

# res = ((3,), (4,), (5,))
# li = [x[0] for x in res]
# li.append(2)
# li = tuple(li)
# print(li)
#
# cmd.execute(f"SELECT * FROM `following` WHERE `login_id` IN {li} ")
# print(cmd.fetchall())

# r = ((16, 2, 6, 'afjnweh', '2023-02-05', '14:10:31', 'makima.jpg', 'Zayan Shamz'), (15, 2, 2, 'copy alle naayie\r\n', '2023-02-05', '14:10:21', 'makima.jpg', 'Zayan Shamz'), (14, 2, 4, 'looking cool\r\n', '2023-02-05', '14:10:00', 'makima.jpg', 'Zayan Shamz'), (13, 2, 4, 'wow', '2023-02-05', '14:09:41', 'makima.jpg', 'Zayan Shamz'), (12, 2, 6, 'hello\r\nhi', '2023-02-04', '12:14:32', 'makima.jpg', 'Zayan Shamz'), (11, 2, 2, 'jljklkm', '2023-02-04', '12:14:19', 'makima.jpg', 'Zayan Shamz'), (10, 2, 2, 'lkjlkj\r\nl;lk\r\nl\r\n;lkl;klkl', '2023-02-03', '12:36:58', 'makima.jpg', 'Zayan Shamz'), (9, 2, 3, 'sa', '2023-02-03', '12:27:35', 'makima.jpg', 'Zayan Shamz'), (8, 2, 3, 'd', '2023-02-03', '12:27:32', 'makima.jpg', 'Zayan Shamz'), (7, 2, 3, 'f', '2023-02-03', '12:27:29', 'makima.jpg', 'Zayan Shamz'), (6, 2, 4, 'noooo', '2023-02-03', '11:15:29', 'makima.jpg', 'Zayan Shamz'), (5, 2, 4, 'yess', '2023-02-03', '00:40:48', 'makima.jpg', 'Zayan Shamz'), (4, 2, 3, 'd\r\nd\r\nd\r\nd\r\nd\r\nd\r\nd\r\nd\r\nd\r\nd\r\n', '2023-01-30', '16:38:07', 'makima.jpg', 'Zayan Shamz'), (3, 2, 3, 'fv\r\nf\r\nf\r\nf\r\nf\r\nf\r\nf\r\nf', '2023-01-30', '16:21:25', 'makima.jpg', 'Zayan Shamz'), (2, 2, 3, 'hii', '2023-01-30', '15:49:09', 'makima.jpg', 'Zayan Shamz'), (1, 2, 3, 'yess', '2023-01-30', '12:29:31', 'makima.jpg', 'Zayan Shamz'))
# print(r)
# i=2
# print(r[0][3])
# print(r[i-2][3])
# # for i in r:
# #     print(i)
#
# rowCount = math.ceil(1/3)
# print(f"row Count = {rowCount}")
#
# #
# li = [8, None]
# li = tuple(li)
# print(li)


datt = [int(x) for x in str.split("2001-08-13",'-')]
dob = date(datt[0],datt[1],datt[2])
today = date.today()
age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
print(age)