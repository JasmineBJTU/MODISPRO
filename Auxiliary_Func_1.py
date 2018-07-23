#coding:utf-8
'''
Created on 2018年7月17日
@author: Administrator
'''


import os
import time, datetime
import xml.dom.minidom as xmldom
import Custom_MRT_1 as mrt


# 获取毫秒 
def Get_current_time():
    ct = time.time()
    local_time = datetime.datetime.now()
    date_head = local_time.strftime("%Y-%m-%d %H:%M:%S")
    date_secs = (ct - long(ct)) * 1000
    time_str = "%s,%03d" % (date_head, date_secs)
    
    return time_str


# 输出日志
def Writelog(loginfofile, loginfostr, t):    
    if t == 1:
        with open(loginfofile, 'a+') as logf:            
            logf.write(Get_current_time() + ' INFO ' + loginfostr + '\n')
    else:
        with open(loginfofile, 'a+') as logf:
            logf.write(Get_current_time() + ' ERROR ' + loginfostr + '\n')        
    del logf
    

# 删除临时路径
def Deletedir(tempdir):
    if os.path.exists(tempdir):        
        tfiles = os.listdir(tempdir)
        if len(tfiles) > 0:
            for tfile in tfiles:
                tfile = tempdir + os.path.sep + tfile
                if os.path.exists(tfile):
                    os.remove(tfile)
        os.rmdir(tempdir)
    

# 读取参数文件
def ReadConfig(configfile):
    paramstrs = [' ' for i in range(7)]
    with open(configfile, 'r') as f:
        for i in range(7): 
            # 去除行尾'\n'          
            paramstr = (f.readline()).strip('\n')
            if not paramstr: break
            print paramstr  
            if len(paramstr.split('=')) != 2:
                return '参数文件格式异常!'            
            # 去除首尾空格
            paramstrs[i] = ((paramstr.split('='))[1]).strip()

    return paramstrs


# 读取系统配置文件
def ReadSystemConfig(sysxmlfile, product_type, error):
    
    domxml = xmldom.parse(sysxmlfile)
    # 根节点
    rootElement = domxml.documentElement
    # properties节点
    propertiesElements = rootElement.getElementsByTagName('Properties')
    if len(propertiesElements) != 1:
        del domxml, rootElement, propertiesElements
        error = 'XML文件格式异常!'
        print error
        return 0
    for propertiesElement in propertiesElements:
        # Product_Type节点
        productElements = propertiesElement.getElementsByTagName('Product_Type')
        if len(productElements) != 5:
            del domxml, rootElement, propertiesElements
            del productElements
        for productElement in productElements:
            name = productElement.getAttribute('name')
            if name == product_type:
                
                # 读取Bands
                bandsElements = productElement.getElementsByTagName('Bands')
                if len(bandsElements) != 1:
                    del domxml, rootElement, propertiesElements
                    error = product_type + 'Bands节点格式异常!'
                    print error
                    return 0 
                bands = bandsElements[0].getAttribute('value')
                bands_num = bands.split(' ').count('1')
                del bandsElements
                
                # 读取Typesuffixs
                typesuffixs = [[] for i in range(bands_num)]
                typesuffixsElements = productElement.getElementsByTagName('Typesuffixs')
                if len(typesuffixsElements) != 1:
                    del domxml, rootElement, propertiesElements
                    del bandsElements
                    error = product_type + 'Typesuffixs节点格式异常!'
                    print error
                    return 0
                typesuffixs_ = typesuffixsElements[0].getAttribute('value')
                typesuffixs_values = typesuffixs_.split(',')
                if len(typesuffixs_values) != bands_num:
                    del domxml, rootElement, propertiesElements
                    del typesuffixsElements
                    error = product_type + 'Typesuffixs与波段数不一致!'
                    print error
                    return 0
                else:
                    for j in range(len(typesuffixs_values)):
                        typesuffixs[j] = typesuffixs_values[j]
                    del typesuffixsElements
                
                # 读取Valid_range
                valid_range = []
                valid_rangeElements = productElement.getElementsByTagName('Valid_range')
                if len(valid_rangeElements) != 1:
                    del domxml, rootElement, propertiesElements
                    del valid_rangeElements
                    error = product_type + 'Valid_range节点格式异常!'
                    print error
                    return 0
                elements = valid_rangeElements[0].getElementsByTagName('Element')
                if len(elements) != bands_num:
                    del domxml, rootElement, propertiesElements
                    del valid_rangeElements, elements
                    error = product_type + 'Valid_range节点格式异常!'
                    print error
                    return 0
                else:
                    for element_ in elements:
                        valid_range.append(map(int, element_.getAttribute('value').split(',')))
                    del valid_rangeElements, elements
                
                # 读取Fillvalue
                fillvalue = []
                fillvalueElements = productElement.getElementsByTagName('Fillvalue')
                if len(fillvalueElements) != 1:
                    del domxml, rootElement, propertiesElements
                    error = product_type + 'Fillvalue节点格式异常!'
                    print error
                    return 0
                elements = fillvalueElements[0].getElementsByTagName('Element')
                if len(elements) != bands_num:
                    del domxml, rootElement, propertiesElements
                    del fillvalueElements, elements
                    error = product_type + 'Fillvalue与波段数不一致!'
                    print error
                    return 0
                else:
                    for element_ in elements:
                        fillvalue.append(map(int, element_.getAttribute('value').split(',')))
                    del fillvalueElements, elements
                
                # 读取Scale_factor
                scale_factorElements = productElement.getElementsByTagName('Scale_factor')
                if len(scale_factorElements) != 1:
                    del domxml, rootElement, propertiesElements
                    error = product_type + 'Scale_factor节点格式异常!'
                    print error
                    return 0
                scale_factors = map(float, scale_factorElements[0].getAttribute('value').split(','))
                if len(scale_factors) != bands_num:
                    del domxml, rootElement, propertiesElements
                    error = product_type + 'Scale_factor与波段数不一致!'
                    print error
                    return 0
                
                # 读取Resolution
                resolutionElements = productElement.getElementsByTagName('Resolution')
                if len(resolutionElements) != 1:
                    del domxml, rootElement, propertiesElements
                    error = product_type + 'Resolution节点异常!'
                    print error
                    return 0
                resolution = resolutionElements[0].getAttribute('value')
                del resolutionElements
                
                return [bands, typesuffixs, valid_range, fillvalue, scale_factors, resolution]
                
                break
            else:
                continue


# 执行程序
def ExcuteProcess_MOD09A1(indir, product_type, bands,
                       projection ,resolution, ranges, typesuffixs,
                       valid_range, fillvalue, scale_factor,
                       tempdir, loginfofile, restxtfile, outfile, ndwifile):
    
    # 预设回传文件
    resdir = os.path.dirname(restxtfile)
    if os.path.exists(resdir) == False:
        os.mkdir(resdir)
        
    with open(restxtfile,'w') as resf:
        resf.write('0: \n')
    del resf    
    
    Writelog(loginfofile, '开始处理...', 1)    
    
    # 全球HDF数据分组
    Writelog(loginfofile, '开始对全球HDF数据分组...', 1)
    error = ''  
    res = mrt.GetSlice_HDF(indir, product_type, error)
    if res == 0:
        Writelog(loginfofile, '全球HDF数据分组失败!' + error, 0)
        return 0
    else:
        Writelog(loginfofile, '全球HDF数据分组完成!', 1)
        localfiles = res           

    # 分组HDF数据镶嵌投影
    Writelog(loginfofile, '开始对分组数据镶嵌投影...', 1)
    error = ''
    res = mrt.MRTProcess(indir, tempdir, localfiles, bands, projection, resolution, ranges, typesuffixs, loginfofile, error)
    if res == 0 :
        Writelog(loginfofile, '分组数据镶嵌投影失败！' + error, 0)
        print error
        return 0
    else:
        Writelog(loginfofile, '分组数据镶嵌投影完成！', 1)
        localregisterfiles = res               
    
    globalfiles = []    
    for i in range(len(localregisterfiles)):        
        # 全球数据拼接   
        Writelog(loginfofile, '开始镶嵌' + typesuffixs[i] + '分组数据...', 1)
        strs = os.path.basename(outfile[i]).split('.')
        globalfile = os.path.dirname(outfile[i]) + os.path.sep + strs[0] + '_.' + strs[1] 
        ret = mrt.Mosaic(globalfile, localregisterfiles[i], fillvalue[i][0])
        if ret == 1 :
            globalfiles.append(globalfile)
            Writelog(loginfofile, typesuffixs[i] + '全球分组数据镶嵌完成!', 1)
        else:
            Writelog(loginfofile, typesuffixs[i] + '全球分组数据镶嵌失败!', 0)
            return 0

    
    # 分块计算NDWI
    Writelog(loginfofile, '开始计算NDWI...', 1)
    error = ''
    ret = mrt.Computendwi_Block(globalfiles, valid_range, fillvalue, scale_factor, ndwifile, error)
    if ret == 1:
        Deletedir(tempdir)
        Writelog(loginfofile, 'NDWI计算完成!', 1)
        Writelog(loginfofile, '处理全部完成!', 1)
        # 修改回传文件
        with open(restxtfile,'w') as resf:
            resf.write('1; '+ndwifile)
        del resf  
              
        return 1
    else:
        Deletedir(tempdir)
        Writelog(loginfofile, 'NDWI计算失败!'+error, 0)
        Writelog(loginfofile, '处理全部完成!', 1)
        return 0


# 执行程序
def ExcuteProcess_MOD15A2H(indir, product_type, bands,
                           projection ,resolution, ranges, typesuffixs,
                           valid_range, fillvalue, scale_factor,
                           tempdir, loginfofile, restxtfile, outfile):
    
    # 预设回传文件
    resdir = os.path.dirname(restxtfile)
    if os.path.exists(resdir) == False:
        os.mkdir(resdir)
        
    with open(restxtfile,'w') as resf:
        for i in range(len(typesuffixs)):
            resf.write('0: \n')
    del resf    
    
    Writelog(loginfofile, '开始处理...', 1)    
    
    # 全球HDF数据分组
    Writelog(loginfofile, '开始对全球HDF数据分组...', 1)
    error = ''  
    res = mrt.GetSlice_HDF(indir, product_type, error)
    if res == 0:
        Writelog(loginfofile, '全球HDF数据分组失败!' + error, 0)
        return 0
    else:
        Writelog(loginfofile, '全球HDF数据分组完成!', 1)
        localfiles = res 
        
    # 分组HDF数据镶嵌投影
    Writelog(loginfofile, '开始对分组数据镶嵌投影...', 1)
    error = ''
    res = mrt.MRTProcess(indir, tempdir, localfiles, bands, projection, resolution, ranges, typesuffixs, loginfofile, error)
    if res == 0 :
        Writelog(loginfofile, '分组数据镶嵌投影失败！' + error, 0)
        return 0
    else:
        Writelog(loginfofile, '分组数据镶嵌投影完成！', 1)
        localregisterfiles = res 
    
    with open(restxtfile,'r+') as resf:
        restrs = resf.readlines(len(typesuffixs))  
    for i in range(len(localregisterfiles)):        
        # 全球数据拼接   
        Writelog(loginfofile, '开始镶嵌全球' + str(typesuffixs[i]) + '数据...', 1)
        strs = os.path.basename(outfile[i]).split('.')
        globalfile = os.path.dirname(outfile[i]) + os.path.sep + strs[0] + '_.' + strs[1] 
        ret = mrt.Mosaic(globalfile, localregisterfiles[i], fillvalue[i][0])
        if ret == 1 :
            Writelog(loginfofile, '全球' + str(typesuffixs[i]) + '数据镶嵌完成!', 1)
        else:
            Writelog(loginfofile, '全球' + str(typesuffixs[i]) + '数据镶嵌失败!', 0)
            continue
       
        # 定标过滤无效值    
        Writelog(loginfofile, '开始对' + str(typesuffixs[i]) + '全球数据定标过滤无效值...', 1)
        ret = mrt.Valid_block(globalfile, valid_range[i], fillvalue[i], scale_factor[i], outfile[i])
        if ret == 1:
            Writelog(loginfofile, str(typesuffixs[i]) + '全球数据定标过滤无效值完成!', 1)
            with open(restxtfile,'w') as resf:
                restrs[i] = '1; ' + outfile[i] + '\n'
                resf.writelines(restrs)   
        else:
            Writelog(loginfofile, str(typesuffixs[i]) + '全球数据定标过滤无效值失败!', 0)
            with open(restxtfile,'w') as resf:
                restrs[i] = '0; ' + str(typesuffixs[i]) + '处理失败!' + '\n'
                resf.writelines(restrs)
                    
    del resf, restrs
    Deletedir(tempdir)
    Writelog(loginfofile, '处理全部完成!', 1)    
    return 1
    

# 主函数
def MODISPRO_1(configfile, loginfofile):
    
    starttime_ = datetime.datetime.now()
    pwdpath = os.path.realpath(__file__)
        
    resampleexe = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'resource' + os.path.sep + \
                    'MRT' + os.path.sep + 'bin' + os.path.sep + 'resample.exe'    
    if os.path.exists(resampleexe) == False:
        Writelog(loginfofile, resampleexe + '工具不存在!', 0)
        print resampleexe + '工具不存在!'
        return 0
        
    mrtmosaicexe = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'resource' + os.path.sep + \
                    'MRT' + os.path.sep + 'bin' + os.path.sep + 'mrtmosaic.exe'
    if os.path.exists(mrtmosaicexe) == False:
        Writelog(loginfofile, mrtmosaicexe + '工具不存在!', 0)
        print mrtmosaicexe + '工具不存在!'
        return 0
        
    mrtdatadir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'resource' + os.path.sep + \
                    'MRT' + os.path.sep + 'data'
    if os.path.exists(mrtdatadir) == False:
        Writelog(loginfofile, mrtdatadir + '路径不存在!', 0)
        print mrtdatadir + '路径不存在!'
        return 0
    
    # 创建临时路径
    tempdir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'temp'
    if os.path.exists(tempdir) == False:
        os.mkdir(tempdir)
    tempdir = tempdir + os.path.sep + str(time.time()).strip()
    os.mkdir(tempdir)
    
    # 读取参数文件
    # 返回参数依次是产品类型(Product_Type),日期(DataDate),投影(Projection),地理范围(Ranges),输入路径(InputFolder),输出路径(OutputFolder)
    if os.path.exists(configfile) == False:
        Writelog(loginfofile, configfile + '参数文件不存在!', 0)
        print configfile + '参数文件不存在!'
        return 0
    paramstrs = ReadConfig(configfile)
    if len(paramstrs) != 7:
        Writelog(loginfofile, '参数文件读取失败!', 0)
        print '参数文件读取失败!'
        return 0
    
    Product_Type = paramstrs[0]
    DataDate = paramstrs[1]
    Projection = paramstrs[2]
    Ranges = paramstrs[3]
    InputFolder = paramstrs[4]
    OutputFolder = paramstrs[5]
    Receiptfile = paramstrs[6]
    
    # 判断输出路径是否存在
    if os.path.exists(OutputFolder) == False:
        os.mkdir(OutputFolder)  

    # 读取系统配置文件
    sysconfigfile = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'system' + os.path.sep + 'system.xml'
    if os.path.exists(sysconfigfile) == False:
        Writelog(loginfofile, sysconfigfile+'文件不存在!', 0)
        print sysconfigfile+'不存在!'
        return 0
    error = ''
    systeminfo = ReadSystemConfig(sysconfigfile, Product_Type, error)
    if systeminfo == 0:
        Writelog(loginfofile, error, 0)
        print sysconfigfile + '读取失败! ' + error
        return 0
    elif systeminfo == None:
        Writelog(loginfofile, '参数文件设置的产品类型与系统配置文件中不匹配!', 0)
        print '参数文件设置的产品类型与系统配置文件中不匹配!'
        return 0
    else:
        bands = systeminfo[0]
        typesuffixs = systeminfo[1]
        valid_range = systeminfo[2]
        fillvalue = systeminfo[3]
        scale_factor = systeminfo[4]
        resolution = systeminfo[5]
    print 'bands: ', bands
    print 'typesuffixs: ', typesuffixs
    print 'valid_range: ', valid_range
    print 'fillvalue: ', fillvalue
    print 'scale_factor: ', scale_factor
    print 'resolution: ', resolution

    try:
        if Product_Type == 'MOD09A1':
            bands = '0 1 0 0 0 0 1 0 0 0 0 0 0' 
            typesuffixs = ['sur_refl_b02', 'sur_refl_b07']
            valid_range = [[-100,16000], [-100,16000]]
            fillvalue = [[-28672,-999], [-28672,-999]] 
            scale_factor = [0.0001, 0.0001]
            resolution = '0.005'
            tempfile = [OutputFolder + os.path.sep + Product_Type + '_' + DataDate + '_GEO_500m_SUR2.tif',
                       OutputFolder + os.path.sep + Product_Type + '_' + DataDate + '_GEO_500m_SUR7.tif']
            ndwifile = OutputFolder + os.path.sep + Product_Type + '_' + DataDate + '_GEO_500m_NDWI.tif'
            
            ret = ExcuteProcess_MOD09A1(InputFolder, Product_Type, bands,
                                           Projection ,resolution, Ranges, typesuffixs,
                                           valid_range, fillvalue, scale_factor,
                                           tempdir, loginfofile, Receiptfile, tempfile, ndwifile)
            
        else:
            #===================================================================
            # bands = '1 0 0 0 0 0 0 0 0 0 0 0' 
            # typesuffixs = ['1_km_16_days_NDVI']
            # valid_range = [[-2000,10000]]
            # fillvalue = [[-3000,-999]] 
            # scale_factor = [0.0001]
            # resolution = '0.01'
            #===================================================================
            outfile = []
            for i in range(len(typesuffixs)):
                outfile.append(OutputFolder + os.path.sep + Product_Type + '_' + DataDate + '_' + Projection + '_' + typesuffixs[i] + '.tif')
            ret = ExcuteProcess_MOD15A2H(InputFolder, Product_Type, bands,
                                           Projection ,resolution, Ranges, typesuffixs,
                                           valid_range, fillvalue, scale_factor,
                                           tempdir, loginfofile, Receiptfile, outfile)
        if ret != 1:
            print '最终处理失败!'            
            return 0
        else:
            print '开始时间: ', starttime_
            print '结束时间: ', datetime.datetime.now()
            print 'finished!'  
            return 1 
    except Exception,e:
        Writelog(loginfofile, e, 0)
        print e
        return 0
    finally:
        Deletedir(tempdir)

