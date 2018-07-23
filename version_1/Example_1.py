#coding:utf-8
'''
Created on 2018年7月14日
Description:
    HDF文件分块镶嵌投影转换,得到tif数据格式,再利用GDAL镶嵌得到全球数据,最后对全球数据进行定标过滤无效值
    1000m数据单波段处理需6min,500m数据单波段处理需30min,NDWI500m需1h
@author: Administrator
'''

import datetime
import Auxiliary_Func_1 as aux


if __name__ == '__main__':
    
    # config_MOD09A1, config_MOD13A2, config_MOD15A2H, config_MOD16A2, config_MYD13A2
    configfile = 'F:\\AutoDownload\\config_MOD16A2.txt'
    currentdate = datetime.datetime.now().strftime('%Y%m%d')
    loginfofile = 'F:\\Eclipse_workspace\\MODISPRO\\log\\'+currentdate+'.log'

    ret = aux.MODISPRO_1(configfile, loginfofile)
    if ret != 1:
        print 'failed!'
    else:
        print 'finished!'
    
    