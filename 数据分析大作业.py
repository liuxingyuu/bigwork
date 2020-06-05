#import time
import pandas as pd
import re
#start = time.clock()

print('本程序使用前请将IPIP和data与exe放入同一目录下')
# 让列名与数据对齐
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
city_name = input("请输入城市的中文名:")
#city_name = '大阪府'
rawdataIPIP = pd.read_csv('IPIP.csv', header=None, encoding='utf-8', names=range(1, 50))
newdataIPIP = rawdataIPIP[[1, 2, 4]]
newdataIPIP.rename(columns={1: '起始IP', 2: '结束IP', 4: '省级'}, inplace=True)
IPIPdata_list = newdataIPIP.values.tolist()
deg=10000000

new_data_listIPIP = []  # 保存筛选出来的列表
for data in IPIPdata_list:  # 遍历列表
    if re.match(city_name, data[2]) != None:  # 如果正则匹配出的数据不为None, 就将此数据添加到新列表中
        new_data_listIPIP.append(data)

names = ['起始IP', '结束IP', '省级']
dataIPIP = pd.DataFrame(columns=names, data=new_data_listIPIP)

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

dataIPIP.to_csv(city_name+'IP范围.csv',index=0,encoding = "utf-8") #存储所在城市网段
print(dataIPIP)

# 2.使用IPy库将点分十进制转换成int型，对后面的筛选工作进行预处理
from IPy import IP
import copy

intdata_list = copy.deepcopy(new_data_listIPIP)  # 复制一个列表用于转换IP操作

for data in intdata_list:  # 遍历列表

    data[0] = IP(data[0]).int()
    data[1] = IP(data[1]).int()

dataIPIPint = pd.DataFrame(columns=names, data=intdata_list)


#预处理
book={}
a=[]
for intdata_lists in intdata_list:
    temp=[]
    temp.append(intdata_lists[0])
    temp.append(intdata_lists[1])
    a.append(temp)

c=a[0][0]//deg
temp_3=[]
for i in range(1,len(a)):
    d=a[i][0]//deg
    if d == c:
        temp_3.append(a[i-1])
    else:
        temp_3.append(a[i-1])
        book[c] = temp_3
        temp_3=[]
        temp_3.append(a[i - 1])                     #防止进位导致数据遗漏
    c=d
    if(i==len(a)-1):
        book[c] = temp_3

# 3.构造函数judgeIP判断提取出的IP是否在Osaka的IP段内
def judgeIP(IPstr, book,list1):  # 想要判断的IP，用于判断的IP段列表名
    flag_1 = False
    dataint = IP(IPstr).int()
    sdataint=dataint//deg
    if sdataint in list1:
        IP_paras=book[sdataint]
        for IP_para in IP_paras:
            if dataint >= IP_para[0] and dataint <= IP_para[1]:
                flag_1 = True
                return flag_1  # 返回标志位是否在IP段内


# 4.构造函数get_Continuous_route判断两个连续的路由
import re
def get_Continuous_route(front_route, behind_route, Osaka_IP_list, side_list, point_list):
    # 前一跳信息，后一跳信息，输出的路由列表，输出的边界IP列表，输出的中心IP列表
    con_route = []
    res_1 = re.search('(?P<hop>.{1,2}):(?P<other>.*)', front_route)
    res_2 = re.search('(?P<hop>.{1,2}):(?P<other>.*)', behind_route)
    flag_IP = '*'

    if (res_1.groupdict()['other'] != '*') and (res_2.groupdict()['other'] != '*'):  # 判断连续的路由信息是否为*
        final_1 = re.search('(?P<hop>.*):(?P<IP>.*):(?P<TTL>.*):(?P<delay_time>.*)', front_route)
        final_2 = re.search('(?P<hop>.*):(?P<IP>.*):(?P<TTL>.*):(?P<delay_time>.*)', behind_route)

        flag_1 = judgeIP(final_1.groupdict()['IP'], book,list1=book.keys())

        flag_2 = judgeIP(final_2.groupdict()['IP'], book,list1=book.keys())  # 判断路由信息是否在网段内
        if(final_1.groupdict()['IP']!=final_2.groupdict()['IP']):
            if flag_1 and flag_2:
                con_route.append(final_1.groupdict()['IP'])
                con_route.append(final_2.groupdict()['IP'])
                Osaka_IP_list.append(con_route)

                point_list.append(final_1.groupdict()['IP'])
                point_list.append(final_2.groupdict()['IP'])

            if (flag_1 and (not flag_2)):
                side_list.append(final_1.groupdict()['IP'])

            if ((not flag_1) and flag_2):
                side_list.append(final_2.groupdict()['IP'])
    return (Osaka_IP_list, side_list, point_list)  # 输出的路径列表，输出的边界列表


# 5.提取data中符合条件的路由段

import re
import json
from IPy import IP

Osaka_IP_list = []
side_list = []
point_list = []
f = open(r'data.txt', encoding="utf-8")  # 导入数据集
a = list(f)
length = len(a)
word = '\t'
Osaka_IP_list = []
j = 0
for i in range(length):
    w = [m.start() for m in re.finditer(word, a[i])]
    rawstr = a[i][w[0] + 1:w[1]]
    dict = json.loads(rawstr)

    IP_paras = intdata_list
    for rootIP in dict.keys():
        front_route = dict[rootIP][0]
        for route in dict[rootIP][1:]:
            behind_route = route
            (Osaka_IP_list, side_list, point_list) = get_Continuous_route(front_route, behind_route, Osaka_IP_list,
                                                                          side_list, point_list)
            front_route = behind_route
            # print(Osaka_IP_list)

f.close()

"""
names1_node=['起始IP','结束IP']
edge = pd.DataFrame(columns=names1_node, data=Osaka_IP_list)
edge.to_csv(city_name+'原始边.csv',index=0,encoding = "utf-8") #存储路由路径IP


names2_node=['节点']
new_Osaka_IP = pd.DataFrame(columns=names2_node, data=point_list)
new_Osaka_IP.to_csv(city_name+'原始中心节点.csv',index=0,encoding = "utf-8") #存储中心节点IP

names3_node=['节点']
side = pd.DataFrame(columns=names3_node, data=side_list)
side.to_csv(city_name+'原始边缘节点.csv',index=0,encoding = "utf-8") #存储边缘节点IP
"""

print("有{}条边".format(len(Osaka_IP_list)))
print("有{}个中心节点".format(len(point_list)))
print("有{}个边界节点".format(len(side_list)))

# 6.将节点进行去重，并输出到csv文件，方便后续直接调取


print('对点进行去重:')
a = set(point_list)
point_list = list(a)
point_list.sort()
names_node = ['节点']
point = pd.DataFrame(columns=names_node, data=point_list)

b = set(side_list)
side_list = list(b)
side_list.sort()
names_node = ['节点']
side = pd.DataFrame(columns=names_node, data=side_list)

Osaka_IP_list.sort()
names1_node = ['起始IP', '结束IP']

edge = pd.DataFrame(columns=names1_node, data=Osaka_IP_list)

# 7.为后面导入Gephi进行数据预处理
raw_node_list = []
for data_1 in point_list:
    raw_node_list.append(data_1[0])  # 建立新列表new_point_list用于储存点

for data_1 in side_list:
    raw_node_list.append(data_1[0])

# 8.从相应的文件中加载列表
import pandas as pd

Osaka_IP_list = edge.values.tolist()
point_list = point.values.tolist()
side_list = side.values.tolist()

names1_node=['起始IP','结束IP']
edge = pd.DataFrame(columns=names1_node, data=Osaka_IP_list)
edge.to_csv(city_name+'边.csv',index=0,encoding = "utf-8") #存储路由路径IP


names2_node=['节点']
new_Osaka_IP = pd.DataFrame(columns=names2_node, data=point_list)
new_Osaka_IP.to_csv(city_name+'中心节点.csv',index=0,encoding = "utf-8") #存储中心节点IP

names3_node=['节点']
side = pd.DataFrame(columns=names3_node, data=side_list)
side.to_csv(city_name+'边缘节点.csv',index=0,encoding = "utf-8") #存储边缘节点IP


print("有{}条边".format(len(Osaka_IP_list)))  # 有多少符合的IP边
print("有{}个中心节点".format(len(point_list)))
print("有{}个边界节点".format(len(side_list)))

# 9.找出边界节点

c=a&b
intersection_list = list(c)
intersection_list.sort()
names_node = ['节点']
intersection = pd.DataFrame(columns=names_node, data=intersection_list)
intersection.to_csv(city_name+'边界识别结果.csv',index=0,encoding = "utf-8") #存储边界识别结果
print("识别出{}个边界结点".format(len(intersection_list)))




node_list=[]                                            #建立新列表node_list用于储存一个二维的列表



#edge=pd.read_csv('大阪府边.csv', encoding='utf-8')
#edge_list = edge.values.tolist()

#result=pd.read_csv('大阪府边界识别结果.csv', encoding='utf-8')
#result_list = result.values.tolist()


#print(intersection_list)
#print(type(intersection_list))
#print(intersection_list[0])
#print(type(intersection_list[0]))



i=1
for point_lists in point_list:
    flag=0
    for result_lists in intersection_list:
        if point_lists[0] == result_lists:
            flag=1

    point_lists.insert(0, i)
    point_lists.append(flag)
    i=i+1

names_node=['Id','Label','flag']
point = pd.DataFrame(columns=names_node, data=point_list)
point.to_csv(city_name+'节点导入文件.csv',index=0,encoding = "utf-8") #存储所有的节点IP

dict_1={}
for point_lists in point_list:
    dict_1[point_lists[1]]=point_lists[0]

last_edge_list=[]

for edge_lists in Osaka_IP_list:
    #print(temp_1)
    temp_2=[]
    temp_2.append(dict_1[edge_lists[0]])
    temp_2.append(dict_1[edge_lists[1]])
    last_edge_list.append(temp_2)

names1_node=['source','target']
new_Osaka_IP = pd.DataFrame(columns=names1_node, data=last_edge_list)
new_Osaka_IP.to_csv(city_name+'边导入文件.csv',index=0,encoding = "utf-8") #存储中心节点IP

#end = time.clock()
#print('本程序运行时间为：'+str(end - start)+'秒 ')
city_name = input("请按任意键退出")