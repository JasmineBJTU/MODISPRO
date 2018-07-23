#coding:utf-8
'''
Created on 2018年7月16日
Description:
            指定路径下HDF文件单个投影转换并定标,后分块拼接(一级镶嵌),最后再将分块拼接(二级镶嵌)结果镶嵌为全球数据
            不足:1000m数据处理时长20min,500m数据处理时长4h
@author: Administrator
'''

import datetime
import Auxiliary_Func_2 as aux


if __name__ == '__main__':    
    
    # config_MOD13A2, config_MOD15A2H, config_MOD16A2
    configfile = 'F:\\AutoDownload\\config_MOD13A2.txt'
    restxtfile = 'F:\\AutoDownload\\receipt.txt'
    currentdate = datetime.datetime.now().strftime('%Y%m%d')
    loginfofile = 'F:\\AutoDownload\\'+currentdate+'.log'
    
    aux.MODISPRO_2(configfile, restxtfile, loginfofile)