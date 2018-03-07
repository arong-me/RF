#coding=utf-8
import requests
import json
import re

from check_response_data import *
import sys,os
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding) 
    
'''
已支持分类：一季度报告、三季度报告、半年度报告、年度报告
目前只支持验证响应状态码、code及data为空验证
后期计划加入连表验证
'''
# dict_cate={'T004001001':'年度报告','T004001002':'半年度报告','T004001003':'一季度报告','T004001004':'三季度报告','T004001005':'业绩预告','T004001006':'业绩快报','T004002002':'股份增减持'}

#设置执行环境
url='https://www.analyst.ai'

# 设置开始结束日期
start_time="2017-01-01"
end_time="2018-01-16"

#limit，每次查询公告列表数，由于公共列表api是连mongo查询，故limit最大限制为120
limit=100

#已支持分类：一季度报告、三季度报告、半年度报告、年度报告
# check_toushi_api(url,'T004001003',u'一季度报告',start_time,end_time,limit)
check_toushi_api(url,'T004001004',u'三季度报告',start_time,end_time,limit)
# check_toushi_api(url,'T004001002',u'半年度报告',start_time,end_time,limit)
# check_toushi_api(url,'T004001001',u'年度报告',start_time,end_time,limit)

#目前未支持如下分类
# check_toushi_api(url,'T004001005',u'业绩预告',start_time,end_time,limit)
# check_toushi_api(url,"T004001006",u"业绩快报",start_time,end_time,limit)
# check_toushi_api(url,'T004002002',u'股份增减持',start_time,end_time,limit)
# check_toushi_api(url,'S004004',u'IPO',start_time,end_time,limit)
# check_toushi_api(url,'S004005',u'增发',start_time,end_time,limit)




    
