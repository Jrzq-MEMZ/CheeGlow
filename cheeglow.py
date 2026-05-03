#!/usr/bin/env python3
"""
CheeGlow - 精美桌面组件
基于 Python + CustomTkinter 的现代化桌面小组件
功能：实时时钟、天气信息、倒数日、透明度/主题自定义
"""

import customtkinter as ctk
import tkinter as tk
import json
import os
import sys
import requests
import urllib.parse
from datetime import datetime, timedelta
import threading
import time
import platform

if platform.system() == "Windows":
    import ctypes

APP_NAME = "CheeGlow"
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(APP_DIR, "cheeglow_config.json")

TRANSPARENT_COLOR = "#010101"
FONT_FAMILY = "Microsoft YaHei"
FONT_EMOJI = "Segoe UI Emoji"
EDGE_SIZE = 8
CORNER_SIZE = 16
MIN_WIDTH = 300
MIN_HEIGHT = 240

THEMES = {
    "暖阳": {
        "bg": "#2D2417", "card": "#3D3020", "accent": "#F0A030",
        "text": "#F5E6D0", "subtext": "#B0A090",
        "button": "#F0A030", "button_text": "#2D2417",
        "accent_dim": "#5A4520",
    },
    "薄荷": {
        "bg": "#1A2A25", "card": "#253530", "accent": "#40D0A0",
        "text": "#D0F0E8", "subtext": "#80B0A0",
        "button": "#40D0A0", "button_text": "#1A2A25",
        "accent_dim": "#2A4A3A",
    },
    "星空": {
        "bg": "#1A1A30", "card": "#252545", "accent": "#8080FF",
        "text": "#D0D0F0", "subtext": "#8080B0",
        "button": "#8080FF", "button_text": "#1A1A30",
        "accent_dim": "#353560",
    },
    "樱花": {
        "bg": "#2A1A25", "card": "#3A2535", "accent": "#FF80B0",
        "text": "#F0D0E0", "subtext": "#B080A0",
        "button": "#FF80B0", "button_text": "#2A1A25",
        "accent_dim": "#4A2540",
    },
}

CHINA_REGIONS = {
    "北京市": ["东城区", "西城区", "朝阳区", "丰台区", "石景山区", "海淀区",
               "顺义区", "通州区", "大兴区", "房山区", "门头沟区", "昌平区",
               "平谷区", "密云区", "怀柔区", "延庆区"],
    "上海市": ["黄浦区", "徐汇区", "长宁区", "静安区", "普陀区", "虹口区",
               "杨浦区", "浦东新区", "闵行区", "宝山区", "嘉定区", "金山区",
               "松江区", "青浦区", "奉贤区", "崇明区"],
    "天津市": ["和平区", "河东区", "河西区", "南开区", "河北区", "红桥区",
               "滨海新区", "东丽区", "西青区", "津南区", "北辰区", "武清区",
               "宝坻区", "蓟州区", "静海区", "宁河区"],
    "重庆市": ["渝中区", "大渡口区", "江北区", "沙坪坝区", "九龙坡区",
               "南岸区", "北碚区", "渝北区", "巴南区", "万州区", "涪陵区",
               "綦江区", "大足区", "长寿区", "江津区", "合川区", "永川区",
               "南川区", "璧山区", "铜梁区", "潼南区", "荣昌区"],
    "河北省": {
        "石家庄市": ["长安区", "桥西区", "新华区", "裕华区", "藁城区", "鹿泉区", "栾城区"],
        "唐山市": ["路南区", "路北区", "古冶区", "开平区", "丰南区", "丰润区", "曹妃甸区"],
        "保定市": ["竞秀区", "莲池区", "满城区", "清苑区", "徐水区"],
        "邯郸市": ["邯山区", "丛台区", "复兴区", "峰峰矿区", "肥乡区", "永年区"],
        "秦皇岛市": ["海港区", "山海关区", "北戴河区", "抚宁区"],
        "廊坊市": ["安次区", "广阳区", "霸州市", "三河市", "固安县"],
        "承德市": ["双桥区", "双滦区", "鹰手营子矿区"],
        "张家口市": ["桥东区", "桥西区", "宣化区", "下花园区"],
        "沧州市": ["新华区", "运河区", "沧县", "青县", "任丘市", "黄骅市"],
        "衡水市": ["桃城区", "冀州区", "枣强县", "武邑县", "深州市"],
        "邢台市": ["襄都区", "信都区", "任泽区", "南和区"],
    },
    "山西省": {
        "太原市": ["小店区", "迎泽区", "杏花岭区", "尖草坪区", "万柏林区", "晋源区"],
        "大同市": ["平城区", "云冈区", "新荣区", "云州区"],
        "临汾市": ["尧都区", "曲沃县", "翼城县", "襄汾县", "洪洞县", "侯马市"],
        "运城市": ["盐湖区", "临猗县", "万荣县", "永济市", "河津市"],
        "晋中市": ["榆次区", "太谷区", "祁县", "平遥县", "介休市"],
        "长治市": ["潞州区", "上党区", "屯留区", "潞城区"],
        "晋城市": ["城区", "泽州县", "高平市"],
        "朔州市": ["朔城区", "平鲁区", "山阴县"],
        "忻州市": ["忻府区", "定襄县", "原平市"],
        "阳泉市": ["城区", "矿区", "郊区", "平定县"],
    },
    "辽宁省": {
        "沈阳市": ["和平区", "沈河区", "大东区", "皇姑区", "铁西区", "苏家屯区",
                   "浑南区", "沈北新区", "于洪区", "辽中区"],
        "大连市": ["中山区", "西岗区", "沙河口区", "甘井子区", "旅顺口区", "金州区",
                   "普兰店区", "瓦房店市", "庄河市"],
        "鞍山市": ["铁东区", "铁西区", "立山区", "千山区", "海城市"],
        "抚顺市": ["新抚区", "东洲区", "望花区", "顺城区"],
        "锦州市": ["古塔区", "凌河区", "太和区", "义县", "北镇市", "凌海市"],
        "营口市": ["站前区", "西市区", "鲅鱼圈区", "老边区", "盖州市", "大石桥市"],
        "丹东市": ["元宝区", "振兴区", "振安区", "东港市", "凤城市"],
        "盘锦市": ["双台子区", "兴隆台区", "大洼区", "盘山县"],
        "阜新市": ["海州区", "新邱区", "太平区", "清河门区", "细河区"],
        "辽阳市": ["白塔区", "文圣区", "宏伟区", "弓长岭区", "太子河区", "辽阳县"],
    },
    "吉林省": {
        "长春市": ["南关区", "宽城区", "朝阳区", "二道区", "绿园区", "双阳区", "九台区"],
        "吉林市": ["昌邑区", "龙潭区", "船营区", "丰满区", "永吉县", "磐石市"],
        "四平市": ["铁西区", "铁东区", "梨树县", "公主岭市", "双辽市"],
        "延边州": ["延吉市", "图们市", "敦化市", "珲春市", "龙井市", "和龙市"],
        "通化市": ["东昌区", "二道江区", "通化县", "集安市", "梅河口市"],
        "松原市": ["宁江区", "前郭尔罗斯县", "长岭县", "乾安县", "扶余市"],
    },
    "黑龙江省": {
        "哈尔滨市": ["道里区", "南岗区", "道外区", "平房区", "松北区", "香坊区",
                      "呼兰区", "阿城区", "双城区", "依兰县", "宾县", "巴彦县"],
        "齐齐哈尔市": ["龙沙区", "建华区", "铁锋区", "昂昂溪区", "富拉尔基区"],
        "大庆市": ["萨尔图区", "龙凤区", "让胡路区", "红岗区", "大同区", "肇州县"],
        "牡丹江市": ["东安区", "阳明区", "爱民区", "西安区", "绥芬河市", "海林市"],
        "佳木斯市": ["向阳区", "前进区", "东风区", "郊区", "富锦市", "同江市"],
        "鸡西市": ["鸡冠区", "恒山区", "滴道区", "城子河区", "虎林市", "密山市"],
        "绥化市": ["北林区", "望奎县", "兰西县", "青冈县", "肇东市", "安达市"],
    },
    "江苏省": {
        "南京市": ["玄武区", "秦淮区", "建邺区", "鼓楼区", "浦口区", "栖霞区",
                   "雨花台区", "江宁区", "六合区", "溧水区", "高淳区"],
        "苏州市": ["虎丘区", "吴中区", "相城区", "姑苏区", "吴江区", "昆山市",
                   "太仓市", "常熟市", "张家港市"],
        "无锡市": ["锡山区", "惠山区", "滨湖区", "梁溪区", "新吴区", "江阴市", "宜兴市"],
        "常州市": ["天宁区", "钟楼区", "新北区", "武进区", "金坛区", "溧阳市"],
        "徐州市": ["鼓楼区", "云龙区", "贾汪区", "泉山区", "铜山区", "新沂市", "邳州市"],
        "南通市": ["崇川区", "通州区", "海门区", "如皋市", "启东市", "如东县", "海安市"],
        "扬州市": ["广陵区", "邗江区", "江都区", "宝应县", "仪征市", "高邮市"],
        "盐城市": ["亭湖区", "盐都区", "大丰区", "东台市", "射阳县", "建湖县"],
        "连云港市": ["连云区", "海州区", "赣榆区", "东海县", "灌云县", "灌南县"],
        "镇江市": ["京口区", "润州区", "丹徒区", "丹阳市", "扬中市", "句容市"],
        "泰州市": ["海陵区", "高港区", "姜堰区", "兴化市", "靖江市", "泰兴市"],
        "淮安市": ["淮安区", "淮阴区", "清江浦区", "洪泽区", "涟水县", "盱眙县"],
        "宿迁市": ["宿城区", "宿豫区", "沭阳县", "泗阳县", "泗洪县"],
    },
    "浙江省": {
        "杭州市": ["上城区", "拱墅区", "西湖区", "滨江区", "萧山区", "余杭区",
                   "临平区", "钱塘区", "富阳区", "临安区", "桐庐县", "淳安县", "建德市"],
        "宁波市": ["海曙区", "江北区", "北仑区", "镇海区", "鄞州区", "奉化区",
                   "余姚市", "慈溪市", "宁海县", "象山县"],
        "温州市": ["鹿城区", "龙湾区", "瓯海区", "洞头区", "瑞安市", "乐清市", "永嘉县"],
        "嘉兴市": ["南湖区", "秀洲区", "嘉善县", "海盐县", "海宁市", "平湖市", "桐乡市"],
        "绍兴市": ["越城区", "柯桥区", "上虞区", "新昌县", "诸暨市", "嵊州市"],
        "金华市": ["婺城区", "金东区", "武义县", "浦江县", "磐安县", "兰溪市",
                   "义乌市", "东阳市", "永康市"],
        "台州市": ["椒江区", "黄岩区", "路桥区", "温岭市", "临海市", "玉环市"],
        "湖州市": ["吴兴区", "南浔区", "德清县", "长兴县", "安吉县"],
        "丽水市": ["莲都区", "青田县", "缙云县", "龙泉市"],
        "衢州市": ["柯城区", "衢江区", "江山市", "常山县", "开化县", "龙游县"],
        "舟山市": ["定海区", "普陀区", "岱山县", "嵊泗县"],
    },
    "安徽省": {
        "合肥市": ["蜀山区", "包河区", "庐阳区", "瑶海区", "肥东县", "肥西县",
                   "长丰县", "庐江县", "巢湖市"],
        "芜湖市": ["镜湖区", "鸠江区", "弋江区", "湾沚区", "繁昌区", "南陵县", "无为市"],
        "蚌埠市": ["龙子湖区", "蚌山区", "禹会区", "淮上区", "怀远县", "五河县", "固镇县"],
        "淮南市": ["田家庵区", "大通区", "谢家集区", "八公山区", "潘集区", "凤台县"],
        "马鞍山市": ["花山区", "雨山区", "博望区", "当涂县", "含山县", "和县"],
        "安庆市": ["迎江区", "大观区", "宜秀区", "怀宁县", "太湖县", "宿松县", "桐城市"],
        "黄山市": ["屯溪区", "黄山区", "徽州区", "歙县", "休宁县", "祁门县", "黟县"],
        "铜陵市": ["铜官区", "义安区", "郊区", "枞阳县"],
        "阜阳市": ["颍州区", "颍东区", "颍泉区", "临泉县", "太和县", "阜南县", "界首市"],
        "滁州市": ["琅琊区", "南谯区", "来安县", "全椒县", "定远县", "天长市", "明光市"],
        "六安市": ["金安区", "裕安区", "叶集区", "霍邱县", "舒城县", "金寨县", "霍山县"],
    },
    "福建省": {
        "福州市": ["鼓楼区", "台江区", "仓山区", "马尾区", "晋安区", "长乐区",
                   "闽侯县", "连江县", "福清市"],
        "厦门市": ["思明区", "湖里区", "集美区", "海沧区", "同安区", "翔安区"],
        "泉州市": ["鲤城区", "丰泽区", "洛江区", "泉港区", "晋江市", "石狮市", "南安市"],
        "漳州市": ["芗城区", "龙文区", "龙海区", "云霄县", "漳浦县", "诏安县"],
        "莆田市": ["城厢区", "涵江区", "荔城区", "秀屿区", "仙游县"],
        "三明市": ["三元区", "沙县区", "永安市", "明溪县", "清流县", "宁化县"],
        "龙岩市": ["新罗区", "永定区", "长汀县", "上杭县", "武平县", "连城县", "漳平市"],
        "南平市": ["延平区", "建阳区", "建瓯市", "武夷山市", "邵武市"],
        "宁德市": ["蕉城区", "福安市", "福鼎市", "霞浦县", "古田县", "柘荣县"],
    },
    "江西省": {
        "南昌市": ["东湖区", "西湖区", "青云谱区", "青山湖区", "新建区", "红谷滩区"],
        "九江市": ["浔阳区", "濂溪区", "柴桑区", "庐山市", "瑞昌市", "共青城市"],
        "赣州市": ["章贡区", "南康区", "赣县区", "瑞金市", "信丰县", "大余县"],
        "吉安市": ["吉州区", "青原区", "吉安县", "吉水县", "新干县", "井冈山市"],
        "上饶市": ["信州区", "广丰区", "广信区", "德兴市", "婺源县", "铅山县"],
        "景德镇市": ["昌江区", "珠山区", "浮梁县", "乐平市"],
        "萍乡市": ["安源区", "湘东区", "莲花县", "上栗县", "芦溪县"],
        "新余市": ["渝水区", "分宜县"],
        "鹰潭市": ["月湖区", "余江区", "贵溪市"],
        "抚州市": ["临川区", "东乡区", "南城县", "黎川县", "南丰县"],
    },
    "山东省": {
        "济南市": ["历下区", "市中区", "槐荫区", "天桥区", "历城区", "长清区",
                   "章丘区", "济阳区", "莱芜区", "钢城区"],
        "青岛市": ["市南区", "市北区", "黄岛区", "崂山区", "李沧区", "城阳区",
                   "即墨区", "胶州市", "平度市", "莱西市"],
        "烟台市": ["芝罘区", "福山区", "牟平区", "莱山区", "蓬莱区", "龙口市", "莱阳市"],
        "潍坊市": ["潍城区", "寒亭区", "坊子区", "奎文区", "临朐县", "昌乐县",
                   "青州市", "诸城市", "寿光市", "高密市"],
        "临沂市": ["兰山区", "罗庄区", "河东区", "沂南县", "沂水县", "费县", "平邑县"],
        "济宁市": ["任城区", "兖州区", "曲阜市", "邹城市", "嘉祥县", "金乡县"],
        "淄博市": ["淄川区", "张店区", "博山区", "临淄区", "周村区", "桓台县"],
        "威海市": ["环翠区", "文登区", "荣成市", "乳山市"],
        "日照市": ["东港区", "岚山区", "五莲县", "莒县"],
        "泰安市": ["泰山区", "岱岳区", "新泰市", "肥城市", "宁阳县", "东平县"],
        "德州市": ["德城区", "陵城区", "乐陵市", "禹城市", "临邑县"],
        "聊城市": ["东昌府区", "茌平区", "临清市", "阳谷县", "莘县"],
        "枣庄市": ["市中区", "薛城区", "峄城区", "台儿庄区", "山亭区", "滕州市"],
        "东营市": ["东营区", "河口区", "垦利区", "广饶县", "利津县"],
        "菏泽市": ["牡丹区", "定陶区", "曹县", "单县", "成武县", "巨野县", "郓城县"],
        "滨州市": ["滨城区", "沾化区", "邹平市", "博兴县", "惠民县"],
    },
    "河南省": {
        "郑州市": ["中原区", "二七区", "管城区", "金水区", "上街区", "惠济区",
                   "中牟县", "巩义市", "荥阳市", "新密市", "新郑市", "登封市"],
        "洛阳市": ["老城区", "西工区", "瀍河区", "涧西区", "洛龙区", "偃师区", "孟津区"],
        "开封市": ["龙亭区", "顺河区", "鼓楼区", "禹王台区", "祥符区"],
        "南阳市": ["宛城区", "卧龙区", "南召县", "方城县", "社旗县", "唐河县", "邓州市"],
        "安阳市": ["文峰区", "北关区", "殷都区", "龙安区", "林州市", "安阳县"],
        "新乡市": ["红旗区", "卫滨区", "凤泉区", "牧野区", "卫辉市", "辉县市"],
        "许昌市": ["魏都区", "建安区", "禹州市", "长葛市", "鄢陵县", "襄城县"],
        "平顶山市": ["新华区", "卫东区", "石龙区", "湛河区", "汝州市", "舞钢市"],
        "焦作市": ["解放区", "中站区", "马村区", "山阳区", "沁阳市", "孟州市"],
        "信阳市": ["浉河区", "平桥区", "罗山县", "光山县", "新县", "商城县", "固始县"],
        "周口市": ["川汇区", "淮阳区", "项城市", "鹿邑县", "太康县", "郸城县"],
        "驻马店市": ["驿城区", "确山县", "遂平县", "汝南县", "平舆县", "新蔡县"],
    },
    "湖北省": {
        "武汉市": ["江岸区", "江汉区", "硚口区", "汉阳区", "武昌区", "青山区",
                   "洪山区", "东西湖区", "蔡甸区", "江夏区", "黄陂区", "新洲区", "汉南区"],
        "宜昌市": ["西陵区", "伍家岗区", "点军区", "猇亭区", "夷陵区", "宜都市", "当阳市"],
        "襄阳市": ["襄城区", "樊城区", "襄州区", "南漳县", "谷城县", "老河口市", "枣阳市"],
        "荆州市": ["沙市区", "荆州区", "公安县", "监利市", "江陵县", "松滋市", "石首市"],
        "黄冈市": ["黄州区", "团风县", "红安县", "罗田县", "英山县", "麻城市", "武穴市"],
        "十堰市": ["茅箭区", "张湾区", "郧阳区", "丹江口市", "郧西县", "竹山县"],
        "孝感市": ["孝南区", "孝昌县", "大悟县", "应城市", "安陆市", "汉川市"],
        "荆门市": ["东宝区", "掇刀区", "沙洋县", "京山市", "钟祥市"],
        "黄石市": ["黄石港区", "西塞山区", "下陆区", "铁山区", "大冶市", "阳新县"],
        "咸宁市": ["咸安区", "嘉鱼县", "通城县", "崇阳县", "通山县", "赤壁市"],
        "鄂州市": ["梁子湖区", "华容区", "鄂城区"],
        "随州市": ["曾都区", "随县", "广水市"],
        "恩施州": ["恩施市", "利川市", "建始县", "巴东县", "来凤县"],
    },
    "湖南省": {
        "长沙市": ["芙蓉区", "天心区", "岳麓区", "开福区", "雨花区", "望城区",
                   "长沙县", "浏阳市", "宁乡市"],
        "株洲市": ["天元区", "荷塘区", "芦淞区", "石峰区", "渌口区", "醴陵市"],
        "湘潭市": ["雨湖区", "岳塘区", "湘潭县", "湘乡市", "韶山市"],
        "衡阳市": ["珠晖区", "雁峰区", "石鼓区", "蒸湘区", "南岳区", "衡阳县", "衡南县"],
        "岳阳市": ["岳阳楼区", "云溪区", "君山区", "岳阳县", "湘阴县", "汨罗市", "临湘市"],
        "常德市": ["武陵区", "鼎城区", "津市市", "澧县", "临澧县", "桃源县", "石门县"],
        "张家界市": ["永定区", "武陵源区", "慈利县", "桑植县"],
        "郴州市": ["北湖区", "苏仙区", "桂阳县", "宜章县", "资兴市"],
        "益阳市": ["赫山区", "资阳区", "沅江市", "南县", "桃江县", "安化县"],
        "娄底市": ["娄星区", "双峰县", "新化县", "冷水江市", "涟源市"],
        "邵阳市": ["双清区", "大祥区", "北塔区", "邵东市", "武冈市", "新邵县"],
        "永州市": ["零陵区", "冷水滩区", "祁阳市", "东安县", "双牌县"],
        "怀化市": ["鹤城区", "中方县", "洪江市", "沅陵县", "辰溪县"],
    },
    "广东省": {
        "广州市": ["荔湾区", "越秀区", "海珠区", "天河区", "白云区", "黄埔区",
                   "番禺区", "花都区", "南沙区", "从化区", "增城区"],
        "深圳市": ["罗湖区", "福田区", "南山区", "宝安区", "龙岗区", "盐田区",
                   "龙华区", "坪山区", "光明区"],
        "珠海市": ["香洲区", "斗门区", "金湾区"],
        "汕头市": ["金平区", "龙湖区", "濠江区", "潮阳区", "潮南区", "澄海区"],
        "佛山市": ["禅城区", "南海区", "顺德区", "三水区", "高明区"],
        "东莞市": ["莞城街道", "南城街道", "东城街道", "万江街道", "松山湖", "虎门镇", "长安镇"],
        "中山市": ["石岐街道", "东区街道", "西区街道", "南区街道", "小榄镇", "古镇镇"],
        "惠州市": ["惠城区", "惠阳区", "博罗县", "惠东县", "龙门县"],
        "江门市": ["蓬江区", "江海区", "新会区", "台山市", "开平市", "鹤山市", "恩平市"],
        "湛江市": ["赤坎区", "霞山区", "坡头区", "麻章区", "吴川市", "廉江市", "雷州市"],
        "茂名市": ["茂南区", "电白区", "高州市", "化州市", "信宜市"],
        "肇庆市": ["端州区", "鼎湖区", "高要区", "四会市", "广宁县", "德庆县"],
        "揭阳市": ["榕城区", "揭东区", "揭西县", "惠来县", "普宁市"],
        "潮州市": ["湘桥区", "潮安区", "饶平县"],
        "清远市": ["清城区", "清新区", "英德市", "连州市", "佛冈县"],
        "韶关市": ["武江区", "浈江区", "曲江区", "乐昌市", "南雄市"],
        "梅州市": ["梅江区", "梅县区", "兴宁市", "大埔县", "丰顺县"],
        "河源市": ["源城区", "紫金县", "龙川县", "连平县", "和平县"],
        "阳江市": ["江城区", "阳东区", "阳春市", "阳西县"],
        "汕尾市": ["城区", "海丰县", "陆丰市", "陆河县"],
        "云浮市": ["云城区", "云安区", "罗定市", "新兴县", "郁南县"],
    },
    "广西壮族自治区": {
        "南宁市": ["兴宁区", "青秀区", "江南区", "西乡塘区", "良庆区", "邕宁区", "武鸣区"],
        "桂林市": ["秀峰区", "叠彩区", "象山区", "七星区", "雁山区", "临桂区", "阳朔县"],
        "柳州市": ["城中区", "鱼峰区", "柳南区", "柳北区", "柳江区", "柳城县", "鹿寨县"],
        "北海市": ["海城区", "银海区", "铁山港区", "合浦县"],
        "梧州市": ["万秀区", "长洲区", "龙圩区", "苍梧县", "藤县", "岑溪市"],
        "玉林市": ["玉州区", "福绵区", "容县", "北流市", "博白县"],
        "百色市": ["右江区", "田阳区", "平果市", "靖西市"],
        "钦州市": ["钦南区", "钦北区", "灵山县", "浦北县"],
        "贵港市": ["港北区", "港南区", "覃塘区", "桂平市", "平南县"],
    },
    "海南省": {
        "海口市": ["秀英区", "龙华区", "琼山区", "美兰区"],
        "三亚市": ["海棠区", "吉阳区", "天涯区", "崖州区"],
        "儋州市": ["那大镇", "白马井镇", "中和镇"],
        "琼海市": ["嘉积镇", "博鳌镇", "潭门镇"],
        "万宁市": ["万城镇", "兴隆镇"],
        "文昌市": ["文城镇", "东郊镇", "龙楼镇"],
    },
    "四川省": {
        "成都市": ["锦江区", "青羊区", "金牛区", "武侯区", "成华区", "龙泉驿区",
                   "青白江区", "新都区", "温江区", "双流区", "郫都区", "新津区",
                   "都江堰市", "彭州市", "邛崃市", "崇州市", "简阳市"],
        "绵阳市": ["涪城区", "游仙区", "安州区", "江油市", "三台县", "梓潼县"],
        "德阳市": ["旌阳区", "罗江区", "广汉市", "什邡市", "绵竹市", "中江县"],
        "宜宾市": ["叙州区", "翠屏区", "南溪区", "江安县", "长宁县", "珙县"],
        "泸州市": ["江阳区", "纳溪区", "龙马潭区", "泸县", "合江县", "叙永县"],
        "南充市": ["顺庆区", "高坪区", "嘉陵区", "阆中市", "南部县", "营山县"],
        "乐山市": ["市中区", "沙湾区", "五通桥区", "金口河区", "峨眉山市", "犍为县"],
        "自贡市": ["自流井区", "贡井区", "大安区", "沿滩区", "荣县", "富顺县"],
        "攀枝花市": ["东区", "西区", "仁和区", "米易县", "盐边县"],
        "内江市": ["市中区", "东兴区", "隆昌市", "资中县", "威远县"],
        "达州市": ["通川区", "达川区", "万源市", "宣汉县", "开江县"],
        "眉山市": ["东坡区", "彭山区", "仁寿县", "丹棱县", "洪雅县", "青神县"],
        "资阳市": ["雁江区", "安岳县", "乐至县"],
        "广安市": ["广安区", "前锋区", "华蓥市", "岳池县", "武胜县"],
    },
    "贵州省": {
        "贵阳市": ["南明区", "云岩区", "花溪区", "乌当区", "白云区", "观山湖区"],
        "遵义市": ["红花岗区", "汇川区", "播州区", "仁怀市", "赤水市", "桐梓县"],
        "六盘水市": ["钟山区", "六枝特区", "水城区", "盘州市"],
        "安顺市": ["西秀区", "平坝区", "普定县", "镇宁县", "关岭县", "紫云县"],
        "毕节市": ["七星关区", "大方县", "织金县", "黔西市", "金沙县", "纳雍县"],
        "铜仁市": ["碧江区", "万山区", "江口县", "石阡县", "思南县"],
    },
    "云南省": {
        "昆明市": ["五华区", "盘龙区", "官渡区", "西山区", "呈贡区", "晋宁区", "安宁市"],
        "大理州": ["大理市", "祥云县", "宾川县", "弥渡县", "巍山县", "洱源县"],
        "丽江市": ["古城区", "玉龙县", "永胜县", "华坪县", "宁蒗县"],
        "曲靖市": ["麒麟区", "沾益区", "马龙区", "宣威市", "富源县", "罗平县"],
        "玉溪市": ["红塔区", "江川区", "通海县", "澄江市", "华宁县"],
        "楚雄州": ["楚雄市", "禄丰市", "双柏县", "牟定县", "南华县"],
        "红河州": ["个旧市", "开远市", "蒙自市", "弥勒市", "建水县"],
        "西双版纳州": ["景洪市", "勐海县", "勐腊县"],
        "普洱市": ["思茅区", "宁洱县", "墨江县", "景东县"],
    },
    "西藏自治区": {
        "拉萨市": ["城关区", "堆龙德庆区", "达孜区", "林周县", "当雄县", "曲水县"],
        "日喀则市": ["桑珠孜区", "江孜县", "定日县", "拉孜县", "萨迦县"],
        "山南市": ["乃东区", "扎囊县", "贡嘎县", "桑日县", "琼结县"],
        "林芝市": ["巴宜区", "工布江达县", "米林县", "波密县"],
        "昌都市": ["卡若区", "江达县", "贡觉县", "类乌齐县"],
    },
    "陕西省": {
        "西安市": ["新城区", "碑林区", "莲湖区", "灞桥区", "未央区", "雁塔区",
                   "阎良区", "临潼区", "长安区", "高陵区", "鄠邑区"],
        "宝鸡市": ["渭滨区", "金台区", "陈仓区", "凤翔区", "岐山县", "扶风县"],
        "咸阳市": ["秦都区", "杨陵区", "渭城区", "兴平市", "三原县", "泾阳县"],
        "延安市": ["宝塔区", "安塞区", "延长县", "延川县", "子长市", "志丹县"],
        "汉中市": ["汉台区", "南郑区", "城固县", "洋县", "西乡县", "勉县"],
        "安康市": ["汉滨区", "汉阴县", "石泉县", "宁陕县", "紫阳县"],
        "渭南市": ["临渭区", "华州区", "华阴市", "韩城市", "富平县", "蒲城县"],
        "铜川市": ["王益区", "印台区", "耀州区", "宜君县"],
        "榆林市": ["榆阳区", "横山区", "神木市", "府谷县", "靖边县", "定边县"],
        "商洛市": ["商州区", "洛南县", "丹凤县", "商南县", "山阳县"],
    },
    "甘肃省": {
        "兰州市": ["城关区", "七里河区", "西固区", "安宁区", "红古区", "永登县", "榆中县"],
        "天水市": ["秦州区", "麦积区", "甘谷县", "武山县", "秦安县"],
        "酒泉市": ["肃州区", "金塔县", "瓜州县", "敦煌市", "玉门市"],
        "白银市": ["白银区", "平川区", "靖远县", "会宁县", "景泰县"],
        "武威市": ["凉州区", "民勤县", "古浪县", "天祝县"],
        "张掖市": ["甘州区", "山丹县", "民乐县", "临泽县", "高台县"],
        "庆阳市": ["西峰区", "庆城县", "环县", "华池县", "合水县", "宁县", "镇原县"],
        "定西市": ["安定区", "通渭县", "陇西县", "渭源县", "临洮县"],
    },
    "青海省": {
        "西宁市": ["城东区", "城中区", "城西区", "城北区", "湟中区", "湟源县", "大通县"],
        "格尔木市": ["昆仑路街道", "黄河路街道", "金峰路街道"],
        "海东市": ["乐都区", "平安区", "民和县", "互助县", "化隆县"],
    },
    "内蒙古自治区": {
        "呼和浩特市": ["新城区", "回民区", "玉泉区", "赛罕区", "土左旗", "托克托县"],
        "包头市": ["东河区", "昆都仑区", "青山区", "九原区", "石拐区", "白云矿区"],
        "鄂尔多斯市": ["东胜区", "康巴什区", "达拉特旗", "准格尔旗", "伊金霍洛旗"],
        "赤峰市": ["红山区", "松山区", "元宝山区", "宁城县", "林西县"],
        "通辽市": ["科尔沁区", "霍林郭勒市", "开鲁县", "奈曼旗"],
    },
    "宁夏回族自治区": {
        "银川市": ["兴庆区", "西夏区", "金凤区", "永宁县", "贺兰县", "灵武市"],
        "石嘴山市": ["大武口区", "惠农区", "平罗县"],
        "中卫市": ["沙坡头区", "中宁县", "海原县"],
        "吴忠市": ["利通区", "红寺堡区", "盐池县", "同心县", "青铜峡市"],
    },
    "新疆维吾尔自治区": {
        "乌鲁木齐市": ["天山区", "沙依巴克区", "新市区", "水磨沟区", "头屯河区",
                        "达坂城区", "米东区"],
        "克拉玛依市": ["独山子区", "克拉玛依区", "白碱滩区", "乌尔禾区"],
        "吐鲁番市": ["高昌区", "鄯善县", "托克逊县"],
        "喀什地区": ["喀什市", "疏附县", "疏勒县", "英吉沙县", "莎车县"],
        "伊犁州": ["伊宁市", "奎屯市", "霍尔果斯市", "伊宁县", "察布查尔县"],
        "阿克苏地区": ["阿克苏市", "库车市", "温宿县", "沙雅县"],
    },
    "香港特别行政区": ["中西区", "湾仔区", "东区", "南区", "九龙城区", "观塘区",
                      "深水埗区", "黄大仙区", "油尖旺区", "沙田区", "元朗区", "屯门区"],
    "澳门特别行政区": ["花地玛堂区", "圣安多尼堂区", "大堂区", "望德堂区",
                      "风顺堂区", "嘉模堂区", "路氹城"],
    "台湾省": {
        "台北市": ["中正区", "大同区", "中山区", "松山区", "大安区", "万华区",
                   "信义区", "士林区", "北投区", "内湖区", "南港区", "文山区"],
        "高雄市": ["新兴区", "前金区", "苓雅区", "盐埕区", "左营区", "三民区"],
        "台中市": ["中区", "东区", "南区", "西区", "北区", "西屯区", "南屯区", "北屯区"],
        "台南市": ["中西区", "东区", "南区", "北区", "安平区", "安南区"],
        "新北市": ["板桥区", "中和区", "永和区", "新庄区", "三重区", "芦洲区"],
    },
}


def _flatten_cities():
    result = []
    for prov, val in CHINA_REGIONS.items():
        if isinstance(val, list):
            for c in val:
                result.append(c)
        elif isinstance(val, dict):
            for city, counties in val.items():
                for county in counties:
                    result.append(county)
    return result


ALL_CITY_NAMES = _flatten_cities()

WEATHER_ICONS = {
    "晴": "☀️", "多云": "⛅", "阴": "☁️",
    "小雨": "🌦️", "中雨": "🌧️", "大雨": "🌧️", "暴雨": "⛈️",
    "雷阵雨": "⛈️", "雷暴": "⛈️",
    "小雪": "🌨️", "中雪": "🌨️", "大雪": "❄️", "暴雪": "❄️",
    "雾": "🌫️", "霾": "🌫️", "冻雾": "🌫️",
    "大风": "💨", "冰雹": "🌨️", "冻雨": "🌧️", "雨夹雪": "🌨️",
}

WEEKDAYS_CN = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

WEATHER_EN_TO_CN = {
    "Sunny": "晴", "Clear": "晴",
    "Partly cloudy": "多云", "Partly Cloudy": "多云",
    "Cloudy": "阴", "Overcast": "阴",
    "Mist": "雾", "Fog": "雾", "Foggy": "雾", "Haze": "霾",
    "Light drizzle": "小雨", "Patchy rain possible": "小雨",
    "Light rain": "小雨", "Light rain shower": "小雨",
    "Patchy light drizzle": "小雨", "Patchy light rain": "小雨",
    "Moderate rain": "中雨", "Moderate rain at times": "中雨",
    "Heavy rain": "大雨", "Heavy rain at times": "大雨",
    "Torrential rain shower": "暴雨", "Heavy freezing drizzle": "暴雨",
    "Light thunderstorm": "雷阵雨", "Thunderstorm in vicinity": "雷阵雨",
    "Moderate or heavy thunderstorm": "雷暴", "Thunderstorm": "雷暴",
    "Patchy light snow": "小雪", "Light snow": "小雪",
    "Light snow showers": "小雪", "Patchy moderate snow": "中雪",
    "Moderate snow": "中雪", "Patchy heavy snow": "大雪",
    "Heavy snow": "大雪", "Blizzard": "暴雪",
    "Ice pellets": "冰雹", "Light showers of ice pellets": "冰雹",
    "Moderate or heavy showers of ice pellets": "冰雹",
    "Light freezing rain": "冻雨", "Moderate or heavy freezing rain": "冻雨",
    "Freezing fog": "冻雾",
    "Windy": "大风",
    "Patchy sleet possible": "雨夹雪", "Light sleet": "雨夹雪",
    "Moderate or heavy sleet": "雨夹雪",
    "Light sleet showers": "雨夹雪",
    "Moderate or heavy sleet showers": "雨夹雪",
}


def _translate_weather(en_desc):
    if not en_desc:
        return "未知"
    if en_desc in WEATHER_EN_TO_CN:
        return WEATHER_EN_TO_CN[en_desc]
    for key, val in WEATHER_EN_TO_CN.items():
        if key.lower() in en_desc.lower():
            return val
    return en_desc


def get_weather_icon(desc):
    for key, icon in WEATHER_ICONS.items():
        if key in desc:
            return icon
    return "🌤️"


class ConfigManager:
    DEFAULT_CONFIG = {
        "city": "北京",
        "opacity": 0.85,
        "theme": "星空",
        "countdown_name": "春节",
        "countdown_date": "2027-02-06",
        "pos_x": 100,
        "pos_y": 100,
        "width": 380,
        "height": 380,
    }

    def __init__(self):
        self.config = self._load()

    def _load(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    return {**self.DEFAULT_CONFIG, **saved}
        except Exception:
            pass
        return dict(self.DEFAULT_CONFIG)

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value


class WeatherService:
    def __init__(self):
        self.cache = {}
        self.cache_time = 0
        self.cache_duration = 1800

    def get_weather(self, city):
        now = time.time()
        if city in self.cache and (now - self.cache_time) < self.cache_duration:
            return self.cache[city]
        try:
            encoded = urllib.parse.quote(city)
            url = f"https://wttr.in/{encoded}?format=j1"
            resp = requests.get(url, timeout=10, headers={"User-Agent": "curl/7.68.0"})
            resp.encoding = "utf-8"
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current_condition", [{}])[0]
                en_desc = ""
                for item in current.get("weatherDesc", []):
                    if item.get("value"):
                        en_desc = item["value"]
                        break
                desc = _translate_weather(en_desc)
                result = {
                    "temp": current.get("temp_C", "--"),
                    "desc": desc,
                    "feels_like": current.get("FeelsLikeC", "--"),
                    "humidity": current.get("humidity", "--"),
                    "wind_speed": current.get("windspeedKmph", "--"),
                }
                self.cache[city] = result
                self.cache_time = now
                return result
        except Exception as e:
            print(f"获取天气失败: {e}")
            if city in self.cache:
                return self.cache[city]
        return {
            "temp": "--", "desc": "获取失败",
            "feels_like": "--", "humidity": "--", "wind_speed": "--",
        }

    def fetch_async(self, city, callback):
        def _worker():
            result = self.get_weather(city)
            callback(result)
        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def invalidate(self):
        self.cache.clear()
        self.cache_time = 0


class CheeGlowWidget(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.config_mgr = ConfigManager()
        self.weather_svc = WeatherService()
        self.current_theme = self.config_mgr.get("theme", "星空")
        self._drag_offset = (0, 0)
        self._settings_win = None
        self._pinned_top = False
        self._weather_after_id = None
        self._countdown_after_id = None
        self._resize_edge = None
        self._resize_start = None

        self._setup_window()
        self._apply_theme()
        self._fix_black_border()
        self._hide_from_taskbar()
        self._create_ui()
        self._start_clock()
        self._fetch_weather()
        self._update_countdown()
        self._keep_on_all_desktops()

    def _setup_window(self):
        self.title(APP_NAME)
        self.overrideredirect(True)

        w = self.config_mgr.get("width", 380)
        h = self.config_mgr.get("height", 380)
        x = self.config_mgr.get("pos_x", 100)
        y = self.config_mgr.get("pos_y", 100)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.attributes("-alpha", self.config_mgr.get("opacity", 0.85))
        self._set_window_level("bottom")

    def _fix_black_border(self):
        if platform.system() != "Windows":
            return
        try:
            self.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if not hwnd:
                hwnd = int(self.winfo_id())
            class MARGINS(ctypes.Structure):
                _fields_ = [
                    ("cxLeftWidth", ctypes.c_int),
                    ("cxRightWidth", ctypes.c_int),
                    ("cyTopHeight", ctypes.c_int),
                    ("cyBottomHeight", ctypes.c_int),
                ]
            margins = MARGINS(-1, -1, -1, -1)
            ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))
        except Exception:
            pass
        self.configure(fg_color=TRANSPARENT_COLOR)
        self.attributes("-transparentcolor", TRANSPARENT_COLOR)

    def _hide_from_taskbar(self):
        if platform.system() != "Windows":
            return
        try:
            self.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if not hwnd:
                hwnd = int(self.winfo_id())
            GWL_EXSTYLE = -20
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_NOACTIVATE = 0x08000000
            WS_EX_APPWINDOW = 0x00040000
            ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ex_style = (ex_style & ~WS_EX_APPWINDOW) | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)
        except Exception:
            pass

    def _keep_on_all_desktops(self):
        if platform.system() != "Windows":
            return
        if not self._pinned_top:
            self._set_window_level("bottom")
        self.after(5000, self._keep_on_all_desktops)

    def _set_window_level(self, level):
        if platform.system() != "Windows":
            return
        try:
            self.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if not hwnd:
                hwnd = int(self.winfo_id())
            if level == "bottom":
                z_order = 1
                self._pinned_top = False
            else:
                z_order = -1
                self._pinned_top = True
            flags = 0x0002 | 0x0001 | 0x0010
            ctypes.windll.user32.SetWindowPos(hwnd, z_order, 0, 0, 0, 0, flags)
        except Exception:
            pass

    def _apply_theme(self):
        theme = THEMES.get(self.current_theme, THEMES["星空"])
        self._theme = theme
        ctk.set_appearance_mode("dark")

    def _get_edge(self, x, y):
        w = self.winfo_width()
        h = self.winfo_height()
        if x >= w - CORNER_SIZE and y >= h - CORNER_SIZE:
            return "corner"
        if x >= w - EDGE_SIZE and y >= h - EDGE_SIZE:
            return "corner"
        if x >= w - EDGE_SIZE:
            return "right"
        if y >= h - EDGE_SIZE:
            return "bottom"
        return None

    def _get_cursor_for_edge(self, edge):
        return {"right": "sb_h_double_arrow", "bottom": "sb_v_double_arrow",
                "corner": "bottom_right_corner"}.get(edge, "")

    def _on_mouse_move(self, event):
        edge = self._get_edge(event.x, event.y)
        cursor = self._get_cursor_for_edge(edge) if edge else ""
        try:
            self.configure(cursor=cursor if cursor else "")
        except Exception:
            pass

    def _on_press(self, event):
        edge = self._get_edge(event.x_root - self.winfo_rootx(),
                               event.y_root - self.winfo_rooty())
        if edge:
            self._resize_edge = edge
            self._resize_start = (
                event.x_root, event.y_root,
                self.winfo_width(), self.winfo_height(),
            )
        else:
            self._resize_edge = None
            self._drag_offset = (event.x, event.y)

    def _on_motion(self, event):
        if self._resize_edge and self._resize_start:
            dx = event.x_root - self._resize_start[0]
            dy = event.y_root - self._resize_start[1]
            new_w = max(MIN_WIDTH, self._resize_start[2] + dx)
            new_h = max(MIN_HEIGHT, self._resize_start[3] + dy)
            x = self.winfo_x()
            y = self.winfo_y()
            self.geometry(f"{new_w}x{new_h}+{x}+{y}")
            self.config_mgr.set("width", new_w)
            self.config_mgr.set("height", new_h)
        else:
            x = self.winfo_x() + event.x - self._drag_offset[0]
            y = self.winfo_y() + event.y - self._drag_offset[1]
            self.geometry(f"+{x}+{y}")
            self.config_mgr.set("pos_x", x)
            self.config_mgr.set("pos_y", y)

    def _on_release(self, event):
        self._resize_edge = None
        self._resize_start = None
        self.config_mgr.save()

    def _build_ctx_menu(self):
        menu = tk.Menu(self, tearoff=0, font=(FONT_FAMILY, 11))
        menu.add_command(label="⚙  设置", command=self._open_settings)
        menu.add_separator()
        menu.add_command(label="✕  退出", command=self._on_close)
        return menu

    def _on_right_click(self, event):
        menu = self._build_ctx_menu()
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _create_ui(self):
        theme = self._theme

        self.main_frame = ctk.CTkFrame(
            self, corner_radius=20, fg_color=theme["card"], border_width=0
        )
        self.main_frame.pack(fill="both", expand=True, padx=6, pady=6)

        self.clock_label = ctk.CTkLabel(
            self.main_frame, text="00:00:00",
            font=ctk.CTkFont(family=FONT_FAMILY, size=42, weight="bold"),
            text_color=theme["text"],
        )
        self.clock_label.pack(pady=(20, 0))

        self.date_label = ctk.CTkLabel(
            self.main_frame, text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=theme["subtext"],
        )
        self.date_label.pack(pady=(2, 0))

        ctk.CTkFrame(
            self.main_frame, height=1, fg_color=theme["accent_dim"]
        ).pack(fill="x", padx=24, pady=8)

        weather_center = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        weather_center.pack(pady=(0, 0))

        self.weather_icon_label = ctk.CTkLabel(
            weather_center, text="🌤️",
            font=ctk.CTkFont(family=FONT_EMOJI, size=28),
        )
        self.weather_icon_label.pack()

        self.weather_city_label = ctk.CTkLabel(
            weather_center, text="加载中...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=theme["text"],
        )
        self.weather_city_label.pack(anchor="center")

        self.weather_detail_label = ctk.CTkLabel(
            weather_center, text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=theme["subtext"],
        )
        self.weather_detail_label.pack(anchor="center")

        ctk.CTkFrame(
            self.main_frame, height=1, fg_color=theme["accent_dim"]
        ).pack(fill="x", padx=24, pady=8)

        self.countdown_label = ctk.CTkLabel(
            self.main_frame, text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=42, weight="bold"),
            text_color=theme["accent"],
        )
        self.countdown_label.pack(pady=(0, 16))

        for widget in [self]:
            widget.bind("<ButtonPress-1>", self._on_press)
            widget.bind("<B1-Motion>", self._on_motion)
            widget.bind("<ButtonRelease-1>", self._on_release)
            widget.bind("<Motion>", self._on_mouse_move)
            widget.bind("<Button-3>", self._on_right_click)

        self._bind_children(self.main_frame)

    def _bind_children(self, parent):
        for child in parent.winfo_children():
            child.bind("<ButtonPress-1>", self._on_press)
            child.bind("<B1-Motion>", self._on_motion)
            child.bind("<ButtonRelease-1>", self._on_release)
            child.bind("<Button-3>", self._on_right_click)
            if isinstance(child, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
                self._bind_children(child)

    def _start_clock(self):
        self._tick()

    def _tick(self):
        now = datetime.now()
        self.clock_label.configure(text=now.strftime("%H:%M:%S"))
        weekday = WEEKDAYS_CN[now.weekday()]
        self.date_label.configure(text=f"{now.year}年{now.month}月{now.day}日  {weekday}")
        self.after(1000, self._tick)

    def _fetch_weather(self):
        if self._weather_after_id:
            self.after_cancel(self._weather_after_id)
        city = self.config_mgr.get("city", "北京")
        self.weather_city_label.configure(text=f"{city} · 加载中...")
        self.weather_svc.fetch_async(city, self._on_weather_received)
        self._weather_after_id = self.after(1800000, self._fetch_weather)

    def _on_weather_received(self, result):
        try:
            icon = get_weather_icon(result["desc"])
            self.weather_icon_label.configure(text=icon)
            city = self.config_mgr.get("city", "北京")
            self.weather_city_label.configure(text=f"{city} · {result['desc']}")
            self.weather_detail_label.configure(
                text=f"🌡️ {result['temp']}°C  体感{result['feels_like']}°C  💧 {result['humidity']}%"
            )
        except Exception:
            pass

    def _update_countdown(self):
        if self._countdown_after_id:
            self.after_cancel(self._countdown_after_id)
        name = self.config_mgr.get("countdown_name", "春节")
        date_str = self.config_mgr.get("countdown_date", "2027-02-06")
        try:
            target = datetime.strptime(date_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            diff = (target - today).days
            if diff > 0:
                self.countdown_label.configure(text=f"📅 距{name} {diff}天")
            elif diff == 0:
                self.countdown_label.configure(text=f"🎉 今天{name}!")
            else:
                self.countdown_label.configure(text=f"📅 {name}过{abs(diff)}天")
        except ValueError:
            self.countdown_label.configure(text="⚠️ 日期格式错误")
        self._countdown_after_id = self.after(60000, self._update_countdown)

    def _open_settings(self):
        if self._settings_win and self._settings_win.winfo_exists():
            self._settings_win.focus()
            return
        self._settings_win = SettingsWindow(self)

    def refresh_theme(self, theme_name):
        self.current_theme = theme_name
        self.config_mgr.set("theme", theme_name)
        self._apply_theme()
        for widget in self.winfo_children():
            widget.destroy()
        self._fix_black_border()
        self._hide_from_taskbar()
        self._create_ui()
        self._fetch_weather()
        self._update_countdown()

    def refresh_opacity(self, value):
        self.attributes("-alpha", float(value))
        self.config_mgr.set("opacity", float(value))

    def refresh_weather(self):
        self.weather_svc.invalidate()
        self._fetch_weather()

    def refresh_countdown(self):
        self._update_countdown()

    def _on_close(self):
        self.config_mgr.save()
        self.destroy()


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent: CheeGlowWidget):
        super().__init__(parent)
        self.parent = parent
        self.config_mgr = parent.config_mgr
        theme = parent._theme

        self.title(f"{APP_NAME} 设置")
        self.geometry("460x700+200+150")
        self.configure(fg_color=theme["bg"])
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.grab_set()

        self._city_var = tk.StringVar(value=self.config_mgr.get("city", "北京"))
        self._create_ui(theme)

    def _create_ui(self, theme):
        container = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            container, text=f"⚙  {APP_NAME} 设置",
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=theme["accent"],
        ).pack(pady=(0, 20), anchor="w")

        # ─── 城市选择 ───
        city_section = ctk.CTkFrame(container, fg_color="transparent")
        city_section.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            city_section, text="📍 城市（天气）",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=theme["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            city_section, text="输入城市名称，或从下方省→市→县选择",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=theme["subtext"],
        ).pack(anchor="w", pady=(2, 0))

        self.city_entry = ctk.CTkEntry(
            city_section, placeholder_text="输入城市名称（中文）...",
            textvariable=self._city_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13), height=36,
            fg_color=theme["card"], text_color=theme["text"],
            border_color=theme["accent_dim"],
        )
        self.city_entry.pack(fill="x", pady=(8, 0))

        self._prov_var = tk.StringVar(value="选择省份")
        self._city_list_var = tk.StringVar(value="选择城市")
        self._county_var = tk.StringVar(value="选择区县")

        prov_names = [k for k in CHINA_REGIONS.keys()]

        prov_row = ctk.CTkFrame(city_section, fg_color="transparent")
        prov_row.pack(fill="x", pady=(8, 0))

        self.prov_menu = ctk.CTkOptionMenu(
            prov_row, values=prov_names, variable=self._prov_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11), height=30,
            fg_color=theme["card"], button_color=theme["accent"],
            text_color=theme["text"], dropdown_fg_color=theme["card"],
            command=self._on_prov_select,
        )
        self.prov_menu.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.city_menu = ctk.CTkOptionMenu(
            prov_row, values=["--"], variable=self._city_list_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11), height=30,
            fg_color=theme["card"], button_color=theme["accent"],
            text_color=theme["text"], dropdown_fg_color=theme["card"],
            command=self._on_city_list_select,
        )
        self.city_menu.pack(side="left", fill="x", expand=True, padx=(2, 2))

        self.county_menu = ctk.CTkOptionMenu(
            prov_row, values=["--"], variable=self._county_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11), height=30,
            fg_color=theme["card"], button_color=theme["accent"],
            text_color=theme["text"], dropdown_fg_color=theme["card"],
            command=self._on_county_select,
        )
        self.county_menu.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # ─── 透明度 ───
        opacity_section = ctk.CTkFrame(container, fg_color="transparent")
        opacity_section.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            opacity_section, text="🔍 窗口透明度",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=theme["text"],
        ).pack(anchor="w")

        self.opacity_var = tk.DoubleVar(
            value=self.config_mgr.get("opacity", 0.85)
        )

        opacity_slider_frame = ctk.CTkFrame(opacity_section, fg_color="transparent")
        opacity_slider_frame.pack(fill="x", pady=(8, 0))

        ctk.CTkLabel(
            opacity_slider_frame, text="0.3",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=theme["subtext"],
        ).pack(side="left")

        self.opacity_slider = ctk.CTkSlider(
            opacity_slider_frame, from_=0.3, to=1.0,
            variable=self.opacity_var, number_of_steps=70,
            command=self._on_opacity_change,
            button_color=theme["accent"],
            button_hover_color=theme["accent"],
            progress_color=theme["accent"],
        )
        self.opacity_slider.pack(side="left", fill="x", expand=True, padx=8)

        ctk.CTkLabel(
            opacity_slider_frame, text="1.0",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=theme["subtext"],
        ).pack(side="left")

        self.opacity_value_label = ctk.CTkLabel(
            opacity_section,
            text=f"当前：{self.opacity_var.get():.2f}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=theme["accent"],
        )
        self.opacity_value_label.pack(anchor="e", pady=(4, 0))

        # ─── 主题色 ───
        theme_section = ctk.CTkFrame(container, fg_color="transparent")
        theme_section.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            theme_section, text="🎨 主题配色",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=theme["text"],
        ).pack(anchor="w")

        self.selected_theme = tk.StringVar(
            value=self.config_mgr.get("theme", "星空")
        )

        self.theme_buttons_frame = ctk.CTkFrame(
            theme_section, fg_color="transparent"
        )
        self.theme_buttons_frame.pack(fill="x", pady=(10, 0))

        for name, colors in THEMES.items():
            is_selected = name == self.selected_theme.get()
            btn = ctk.CTkButton(
                self.theme_buttons_frame,
                text=f"● {name}", width=90, height=38,
                font=ctk.CTkFont(family=FONT_FAMILY, size=12,
                                  weight="bold" if is_selected else "normal"),
                fg_color=colors["accent"] if is_selected else theme["card"],
                text_color=colors["button_text"] if is_selected else theme["text"],
                hover_color=colors["accent"],
                corner_radius=12,
                command=lambda n=name: self._on_theme_select(n),
            )
            btn.pack(side="left", padx=3, pady=2)

        # ─── 倒数日设置 ───
        countdown_section = ctk.CTkFrame(container, fg_color="transparent")
        countdown_section.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            countdown_section, text="📅 倒数日设置",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=theme["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            countdown_section, text="名称：",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=theme["subtext"],
        ).pack(anchor="w", pady=(10, 2))

        self.countdown_name_var = tk.StringVar(
            value=self.config_mgr.get("countdown_name", "春节")
        )
        ctk.CTkEntry(
            countdown_section,
            textvariable=self.countdown_name_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13), height=36,
            placeholder_text="倒数日名称",
            fg_color=theme["card"], text_color=theme["text"],
            border_color=theme["accent_dim"],
        ).pack(fill="x")

        ctk.CTkLabel(
            countdown_section, text="目标日期（格式：YYYY-MM-DD）：",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=theme["subtext"],
        ).pack(anchor="w", pady=(10, 2))

        self.countdown_date_var = tk.StringVar(
            value=self.config_mgr.get("countdown_date", "2027-02-06")
        )
        ctk.CTkEntry(
            countdown_section,
            textvariable=self.countdown_date_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13), height=36,
            placeholder_text="2027-02-06",
            fg_color=theme["card"], text_color=theme["text"],
            border_color=theme["accent_dim"],
        ).pack(fill="x")

        # ─── 保存按钮 ───
        ctk.CTkButton(
            container, text="💾  保存配置",
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            height=44, corner_radius=14,
            fg_color=theme["accent"],
            text_color=theme["button_text"],
            hover_color=theme["card"],
            command=self._save,
        ).pack(fill="x", pady=(10, 0))

    # ═══ 城市3级联动 ═══
    def _on_prov_select(self, prov_name):
        val = CHINA_REGIONS.get(prov_name)
        if isinstance(val, list):
            self.city_menu.configure(values=["--"])
            self._city_list_var.set("--")
            self.county_menu.configure(values=val)
            self._county_var.set(val[0] if val else "--")
            self._city_var.set(val[0] if val else prov_name)
        elif isinstance(val, dict):
            city_names = list(val.keys())
            self.city_menu.configure(values=city_names)
            self._city_list_var.set(city_names[0] if city_names else "--")
            self.county_menu.configure(values=["--"])
            self._county_var.set("--")
            self._city_var.set(city_names[0] if city_names else prov_name)
            if city_names:
                self._on_city_list_select(city_names[0])

    def _on_city_list_select(self, city_name):
        prov_name = self._prov_var.get()
        prov_data = CHINA_REGIONS.get(prov_name, {})
        if isinstance(prov_data, dict):
            counties = prov_data.get(city_name, ["--"])
            self.county_menu.configure(values=counties)
            self._county_var.set(counties[0] if counties else "--")
            self._city_var.set(city_name)

    def _on_county_select(self, county_name):
        self._city_var.set(county_name)

    def _on_opacity_change(self, value):
        self.opacity_value_label.configure(text=f"当前：{float(value):.2f}")
        self.parent.refresh_opacity(value)

    def _on_theme_select(self, name):
        self.selected_theme.set(name)
        theme = self.parent._theme
        for widget in self.theme_buttons_frame.winfo_children():
            btn_name = widget.cget("text").replace("● ", "")
            colors = THEMES.get(btn_name, {})
            is_sel = btn_name == name
            try:
                widget.configure(
                    fg_color=colors.get("accent", theme["card"]) if is_sel else theme["card"],
                    text_color=colors.get("button_text", theme["text"]) if is_sel else theme["text"],
                    font=ctk.CTkFont(
                        family=FONT_FAMILY, size=12,
                        weight="bold" if is_sel else "normal",
                    ),
                )
            except Exception:
                pass

    def _save(self):
        self.config_mgr.set("city", self._city_var.get().strip())
        self.config_mgr.set("opacity", self.opacity_var.get())
        self.config_mgr.set("theme", self.selected_theme.get())
        self.config_mgr.set("countdown_name", self.countdown_name_var.get().strip())
        self.config_mgr.set("countdown_date", self.countdown_date_var.get().strip())

        new_theme = self.selected_theme.get()
        if new_theme != self.parent.current_theme:
            self.parent.refresh_theme(new_theme)

        self.parent.refresh_weather()
        self.parent.refresh_countdown()

        self.grab_release()
        self._show_countdown_popup()
        self.destroy()

    def _show_countdown_popup(self):
        name = self.countdown_name_var.get().strip()
        date_str = self.countdown_date_var.get().strip()
        theme = self.parent._theme

        try:
            target = datetime.strptime(date_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            diff = (target - today).days
            if diff > 0:
                msg = f"距离「{name}」还有 {diff} 天\n目标日期：{date_str}"
                title_text = "📅 倒数日确认"
            elif diff == 0:
                msg = f"🎉 今天就是「{name}」！\n目标日期：{date_str}"
                title_text = "📅 倒数日确认"
            else:
                msg = f"「{name}」已过 {abs(diff)} 天\n目标日期：{date_str}"
                title_text = "📅 倒数日确认"
        except ValueError:
            msg = "日期格式错误，请使用 YYYY-MM-DD 格式"
            title_text = "⚠ 格式错误"

        popup = ctk.CTkToplevel(self)
        popup.title(title_text)
        popup.geometry("320x180+300+250")
        popup.configure(fg_color=theme["bg"])
        popup.attributes("-topmost", True)
        popup.resizable(False, False)

        ctk.CTkLabel(
            popup, text=title_text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=theme["accent"],
        ).pack(pady=(20, 8))

        ctk.CTkLabel(
            popup, text=msg,
            font=ctk.CTkFont(family=FONT_FAMILY, size=14),
            text_color=theme["text"],
            justify="center",
        ).pack(pady=(0, 16))

        ctk.CTkButton(
            popup, text="确定", width=100, height=34,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            corner_radius=10,
            fg_color=theme["accent"],
            text_color=theme["button_text"],
            hover_color=theme["card"],
            command=popup.destroy,
        ).pack(pady=(0, 16))


if __name__ == "__main__":
    app = CheeGlowWidget()
    app.mainloop()
