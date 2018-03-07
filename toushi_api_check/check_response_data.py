#coding=utf-8
import requests,re,os


def remove_old_report():
    for f in os.listdir('.'):
        if f.split('.')[1]=='txt':
            os.remove(f)    

def UserCookie(url,email,pwd):
    payload={'email':email, 'pwd':pwd}
    user_cookie = requests.request("POST", url+'/ajax/account2/login', data=payload,timeout=30)
    cookie_str='userid='+user_cookie.cookies['userid']+';PHPSESSID='+user_cookie.cookies['PHPSESSID']+';_identity='+user_cookie.cookies['_identity']
    return cookie_str

#获取ajax-sign
def AjaxSign(url):
    data=requests.get(url+'/account/login')
#     print(data.text)
    ajax_sign=re.findall(r"_AJAX_SIGN_KEY_'] = '(.+?)';",data.text)
    return ajax_sign[0]


def check_response_data(api_path,result,playload,notice_dict,file_list):    
    if 200!=result.status_code:
        msg1=u'所在的公告id：'+notice_dict['src_id']+'，'+api_path+'接口返回状态码：'+result.status_code+'\n'
        print(msg1)
        msg2=u'接口为：'+api_path+'，参数为：'+str(playload)+'\n'
        print(msg2)
        file_list[1].write(msg1)
        file_list[1].write(msg2)
        
    elif 0!=result.json()['code']:
        msg1=u'所在的公告id：'+notice_dict['src_id']+','+api_path+'，%s接口返回code：'+str(result.json()['code'])+'\n'
        msg2=u'接口为：'+api_path+'，参数为：'+str(playload)+'\n'
        file_list[1].write(msg1)
        file_list[1].write(msg2)        
             
    elif {}==result.json()['data'] or []==result.json()['data']:
#       print(result.text)
        msg1=u'所在的公告id：'+notice_dict['src_id']+','+api_path+'，%s接口返回data：'+str(result.json()['data'])+'\n'
        msg2=u'接口为：'+api_path+'，参数为：'+str(playload)+'\n'
        file_list[1].write(msg1)
        file_list[1].write(msg2) 

    else:
        msg1=u'所在的公告id：'+notice_dict['src_id']+','+api_path+'，%s接口返回code：'+str(result.json()['code'])+'\n'
        msg2=u'接口为：'+api_path+'，参数为：'+str(playload)+'\n'
        file_list[0].write(msg1)
        file_list[0].write(msg2)        

    print(u'%s接口检测结果：返回状态码：%d，返回code：%d'%(api_path,result.status_code,result.json()['code']))

def get_headers(url):
#     url='https://www.analyst.ai'
    ajax_sign=AjaxSign(url)
    cookie_str=UserCookie(url,'test1@abcft.com','H7qol/zb3Q5urGSwepp4vec6+eqXYAIZwK7sfJcP3D6KvGHHA2bpa7ixKHfpuGo2/oyqaX9aC+6TqOVfcQn8Ag==')

    headers = {'Ajax-Sign':ajax_sign,'Cookie':cookie_str}
#     print headers
    return headers
    # print('----------------------')
    # print(headers)
    # res = requests.get(url,headers=get_headers(url),timeout=30)

#获取default_data
def DefaultData(url,category,src_id):
    default_data_dict={}
    detail_url=url+'/notice/notice-detail?src_id='+src_id
    # print(detail_url)
    data=requests.get(detail_url,headers=get_headers(url),timeout=30)
    # print(data.text)
    default_data=re.findall(r"_DEFAULT_DATA_={(.+?)};",data.text,re.S)    

    if '年度报告'==category or '半年度报告'==category or '一季度报告'==category or '三季度报告'==category:          
        default_data=default_data[0].replace('\n','').replace("'","").replace('"','').replace(' - 1,','').replace(u'//证券唯一代码','') .replace('\t','')

    for x in default_data.split(','):
        default_data_dict[x.split(':')[0].strip()]=x.split(':')[1].strip()
        
    return default_data_dict

def check_toushi_api(url,categories,category,start_time,end_time,limit):    
    year_report_success = open(category+'_report_success.txt', 'a')
    year_report_fail = open(category+'_report_fail.txt', 'a')
    year_report_summary = open(category+'_report_summary.txt', 'a')
    
    file_list=[year_report_success,year_report_fail,year_report_summary]
    
    payload = {'categories':categories , 'category':category, 'start_time': start_time,'end_time': end_time, 'limit': limit,'order_by': 'all_score','group_by': 'default','offset': 0}
    
    result = requests.post(url+'/ajax/notice/reading',headers=get_headers(url),timeout=30,data=payload)# 注意是data参数    
    # print(result.text) 
    print('##############################################################################')
    print('执行环境：%s'%url)  
    print('查询从%s到%s前%d条的【%s】公告列表，接口响应code：%d'%(start_time,end_time,limit,category,result.status_code))    
    print('##############################################################################\n')
    json_data = result.json()   
    
    #第一条公告参数

    for x in xrange(0,len(json_data['data']['items'])):
        print('开始验证【%s】透视API...'%category)        
        print('-----------------------------------【第%d条公告】-------------------------------------'%(x+1))
    
        src_id=json_data['data']['items'][x]['src_id']
        title=json_data['data']['items'][x]['title']
    
        notice_dict={'src_id':src_id,'title': title}    
        # print(notice_dict)
    
        default_data_dict=DefaultData(url,payload['category'],json_data['data']['items'][x]['src_id'])
    
        # /ajax/notice/profit-top6接口
        payload1 = {'stockCode':default_data_dict['stockcode'],'endDate':default_data_dict['endDate'],'induCode':default_data_dict['thirdInduCode'],'comUniCode':default_data_dict['comUniCode']}
        profit_top6_result = requests.get(url+"/ajax/notice/profit-top6",params=payload1,headers=get_headers(url),timeout=30)
        # print(profit_top6_result.text)
        
        check_response_data('/ajax/notice/profit-top6',profit_top6_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')
    
         # /ajax/notice/share-price接口
        payload1 = {'stockCode':default_data_dict['stockcode']}
        share_price_result = requests.get(url+"/ajax/notice/share-price",params=payload1,headers=get_headers(url),timeout=30)
        # print(share_price_result.text)
        check_response_data('/ajax/notice/share-price',share_price_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')
     
        # /ajax/notice/quarter-fin接口
        payload1 = {'endDate':default_data_dict['endDate'],'induCode':default_data_dict['thirdInduCode'],'comUniCode':default_data_dict['comUniCode']}
        quarter_fin_result = requests.get(url+"/ajax/notice/quarter-fin",params=payload1,headers=get_headers(url),timeout=30)
        # print(share_price_result.json())
        check_response_data('/ajax/notice/quarter-fin',quarter_fin_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')
    
        # /ajax/notice/perstock-chg接口
        payload1 = {'endDate':default_data_dict['endDate'],'comUniCode':default_data_dict['comUniCode']}
        perstock_chg_result = requests.get(url+"/ajax/notice/perstock-chg",params=payload1,headers=get_headers(url),timeout=30)
        # print(share_price_result.json())
        check_response_data('/ajax/notice/perstock-chg',perstock_chg_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')
        
        # /ajax/notice/quarter-valuation接口
        payload1 = {'endDate':default_data_dict['endDate'],'induCode':default_data_dict['thirdInduCode'],'secUniCode':default_data_dict['secUniCode']}
        quarter_valuation_result = requests.get(url+"/ajax/notice/quarter-valuation",params=payload1,headers=get_headers(url),timeout=30)
        # print(share_price_result.json())
        check_response_data('/ajax/notice/quarter-valuation',quarter_valuation_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')
        
        # /ajax/notice/quarter-dupont接口-行业
        payload1 = {'endDate':default_data_dict['endDate'],'induCode':default_data_dict['thirdInduCode'],'comUniCode':default_data_dict['comUniCode'],'type':'indu'}
        quarter_dupont_result = requests.get(url+"/ajax/notice/quarter-dupont",params=payload1,headers=get_headers(url),timeout=30)
        # print(share_price_result.json())
        check_response_data('/ajax/notice/quarter-dupont',quarter_dupont_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')
        
        # /ajax/notice/quarter-dupont接口-概念
        # 先调用/ajax/notice/plate接口    
        payload1 = {'stockCode':default_data_dict['stockcode']}
        plate_result = requests.get(url+"/ajax/notice/plate",params=payload1,headers=get_headers(url),timeout=30)    
        # print(plate_result.json())
        for plate in plate_result.json()['data']:
            payload1 = {'endDate':default_data_dict['endDate'],'plateCode':plate['plateUniCode'],'comUniCode':default_data_dict['comUniCode'],'type':'plate'}
            quarter_dupont_result = requests.get(url+"/ajax/notice/quarter-dupont",params=payload1,headers=get_headers(url),timeout=30)
            # print(share_price_result.json())
            check_response_data('/ajax/notice/quarter-dupont',quarter_dupont_result,payload1,notice_dict,file_list)
            print('-----------------------------------------')
        
        # /ajax/notice/quarter-profitability接口
        payload1 = {'endDate':default_data_dict['endDate'],'induCode':default_data_dict['thirdInduCode'],'comUniCode':default_data_dict['comUniCode']}
        quarter_profitability_result = requests.get(url+"/ajax/notice/quarter-profitability",params=payload1,headers=get_headers(url),timeout=30)
        # print(share_price_result.json())
        check_response_data('/ajax/notice/quarter-profitability',quarter_profitability_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')
        
        # /ajax/notice/quarter-profit接口-同比
        payload1 = {'comUniCode':default_data_dict['comUniCode'],'type':'yoy','count':5}
        quarter_profit_result = requests.get(url+"/ajax/notice/quarter-profit",params=payload1,headers=get_headers(url),timeout=30)
        # print(share_price_result.json())
        check_response_data('/ajax/notice/quarter-profit',quarter_profit_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')
        
        
        # /ajax/notice/quarter-profit接口-环比
        payload1 = {'comUniCode':default_data_dict['comUniCode'],'type':'lrr','count':20}
        quarter_profit_result = requests.get(url+"/ajax/notice/quarter-profit",params=payload1,headers=get_headers(url),timeout=30)
        # print(share_price_result.json())
        check_response_data('/ajax/notice/quarter-profit',quarter_profit_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')
        
        # /ajax/notice/quarter-threefee接口
        payload1 = {'comUniCode':default_data_dict['comUniCode']}
        quarter_threefee_result = requests.get(url+"/ajax/notice/quarter-threefee",params=payload1,headers=get_headers(url),timeout=30)
        # print(share_price_result.json())
        check_response_data('/ajax/notice/quarter-threefee',quarter_threefee_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')
        
        # /ajax/notice/quarter-pepb接口
        payload1 = {'secUniCode':default_data_dict['secUniCode']}
        quarter_pepb_result = requests.get(url+"/ajax/notice/quarter-pepb",params=payload1,headers=get_headers(url),timeout=30)
        # print(share_price_result.json())
        check_response_data('/ajax/notice/quarter-pepb',quarter_pepb_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')
     
        # /ajax/notice/quarter-peg接口
        payload1 = {'secUniCode':default_data_dict['secUniCode']}
        quarter_peg_result = requests.get(url+"/ajax/notice/quarter-peg",params=payload1,headers=get_headers(url),timeout=30)
        # print(share_price_result.json())
        check_response_data('/ajax/notice/quarter-peg',quarter_peg_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')
           
        # /ajax/notice/quarter-indu-list系列接口(type)
        for type in (2,3,4,7,8,9,10,12,13,14,15,16,17,18,19,20,21,32,33,34):
            payload1 = {'endDate':default_data_dict['endDate'],'induCode':default_data_dict['thirdInduCode'],'comUniCode':default_data_dict['comUniCode'],'type':type}
            quarter_indu_list_result = requests.get(url+"/ajax/notice/quarter-indu-list",params=payload1,headers=get_headers(url),timeout=30)
            # print(share_price_result.json())
            check_response_data('/ajax/notice/quarter-indu-list',quarter_indu_list_result,payload1,notice_dict,file_list)
            print('-----------------------------------------')        
            
            
        # /ajax/notice/plate接口    
        payload1 = {'stockCode':default_data_dict['stockcode']}
        plate_result = requests.get(url+"/ajax/notice/plate",params=payload1,headers=get_headers(url),timeout=30)
    #     print(share_price_result.json())
        check_response_data('/ajax/notice/plate',plate_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')    
        
        # /ajax/notice/quarter-cashflow接口    
        payload1 = {'endDate':default_data_dict['endDate'],'comUniCode':default_data_dict['comUniCode']}
        quarter_cashflow_result = requests.get(url+"/ajax/notice/quarter-cashflow",params=payload1,headers=get_headers(url),timeout=30)
    #     print(share_price_result.text)
        check_response_data('/ajax/notice/quarter-cashflow',quarter_cashflow_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')   
    
        # /ajax/notice/quarter-cash-comp接口    
        payload1 = {'endDate':default_data_dict['endDate'],'comUniCode':default_data_dict['comUniCode']}
        quarter_cash_comp_result = requests.get(url+"/ajax/notice/quarter-cash-comp",params=payload1,headers=get_headers(url),timeout=30)
         
        check_response_data('/ajax/notice/quarter-cash-comp',quarter_cash_comp_result,payload1,notice_dict,file_list)
        print('-----------------------------------------') 
        
        # /ajax/notice/quarter-roe-yoy接口    
        payload1 = {'endDate':default_data_dict['endDate'],'induCode':default_data_dict['thirdInduCode'],'comUniCode':default_data_dict['comUniCode'],'type':type}
        quarter_roe_yoy_result = requests.get(url+"/ajax/notice/quarter-roe-yoy",params=payload1,headers=get_headers(url),timeout=30)
        # print(share_price_result.json())
        check_response_data('/ajax/notice/quarter-roe-yoy',quarter_roe_yoy_result,payload1,notice_dict,file_list)
        print('-----------------------------------------')   
        
        if '年度报告'==category or '半年度报告'==category:
            for projectType in ('1517001','1517002','1517003 ','1517000'):
                for year in (2,5):        
                    # /ajax/notice/year-structure接口    
                    payload1 = {'endDate':default_data_dict['endDate'],'comUniCode':default_data_dict['comUniCode'],'year':year,'projectType':projectType}
                    year_structure_result = requests.get(url+"/ajax/notice/year-structure",params=payload1,headers=get_headers(url),timeout=30)
                    # print(share_price_result.json())
                    check_response_data('/ajax/notice/year-structure',year_structure_result,payload1,notice_dict,file_list)
                    print('-----------------------------------------')    
            
                for type in ('yoy','lrr'):
                    for projectName in year_structure_result.json()['data']['allProject']:
                        # /ajax/notice/year-profit接口    
                        payload1 = {'endDate':default_data_dict['endDate'],'comUniCode':default_data_dict['comUniCode'],'type':type,'projectType':projectType,'projectName':projectName}
                        year_profit_result = requests.get(url+"/ajax/notice/year-profit",params=payload1,headers=get_headers(url),timeout=30)
                        # print(share_price_result.json())
                        check_response_data('/ajax/notice/year-profit',year_profit_result,payload1,notice_dict,file_list)
                        print('-----------------------------------------')  
       
    year_report_fail.close()
    year_report_success.close()
    year_report_summary.close()
