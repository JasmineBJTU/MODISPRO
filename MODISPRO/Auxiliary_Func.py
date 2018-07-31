#coding:utf-8
'''
Created on 2018年7月17日
@author: Administrator
'''


import os, shutil
import time, datetime
import xml.dom.minidom as xmldom
import Custom_MRT as mrt
try:
    from osgeo import gdal
except ImportError:
    import gdal
from copy import deepcopy


# 获取毫秒 
def Get_current_time():
    ct = time.time()
    local_time = datetime.datetime.now()
    date_head = local_time.strftime("%Y-%m-%d %H:%M:%S")
    date_secs = (ct - long(ct)) * 1000
    time_str = "%s,%03d" % (date_head, date_secs)
    
    return time_str


# 输出日志
#===============================================================================
# def Writelog(loginfofile, loginfostr, t):    
#     if t == 1:
#         with open(loginfofile, 'a+') as logf:            
#             logf.write(Get_current_time() + ' INFO ' + loginfostr + '\n')
#     else:
#         with open(loginfofile, 'a+') as logf:
#             logf.write(Get_current_time() + ' ERROR ' + loginfostr + '\n')        
#     del logf
#===============================================================================

def Writelog(loginfostr, t):    
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
    else:
        pass
    

# 读取参数文件
#===============================================================================
# def ReadConfig(configfile):
#     paramstrs = [' ' for i in range(7)]
#     with open(configfile, 'r') as f:
#         for i in range(7): 
#             # 去除行尾'\n'          
#             paramstr = (f.readline()).strip('\n')
#             if not paramstr: break
#             print paramstr  
#             if len(paramstr.split('=')) != 2:
#                 return '参数文件格式异常!'            
#             # 去除首尾空格
#             paramstrs[i] = ((paramstr.split('='))[1]).strip()
# 
#     return paramstrs
#===============================================================================

def ReadConfig(configfile, param_name):
    res = None
    with open(configfile, 'r') as f:
        while True:
            temp_str = (f.readline()).strip('\n')
            if temp_str == '':
                continue
            temp_strs = temp_str.split('=')
            if len(temp_strs) != 2:
                Writelog('参数文件格式有误!', 0)
                break
            if temp_strs[0] == param_name == 'InputFiles':
                res = ['' for i in range(int(temp_strs[1]))]
                res = f.readlines()
                for i in range(int(temp_strs[1])):
                    res[i] = res[i].strip('\n')
                break            
            elif temp_strs[0] == param_name:
                res = temp_strs[1]
                break
            
    if res != None:
        return res
    else:
        Writelog('参数文件读取失败!', 0)


# 读取系统配置文件
def ReadSystemConfig(sysxmlfile, product_type):
    
    domxml = xmldom.parse(sysxmlfile)
    # 根节点
    rootElement = domxml.documentElement
    # properties节点
    propertiesElements = rootElement.getElementsByTagName('Properties')
    if len(propertiesElements) != 1:
        del domxml, rootElement, propertiesElements
        Writelog('XML文件格式异常!', 0)
        print 'XML文件格式异常!'
        return 0
    for propertiesElement in propertiesElements:
        # Product_Type节点
        productElements = propertiesElement.getElementsByTagName('Product_Type')
        if len(productElements) != 5:
            del domxml, rootElement, propertiesElements
            del productElements
            Writelog('XML文件格式异常!', 0)
            print 'XML文件格式异常!'
            return 0
        for productElement in productElements:
            name = productElement.getAttribute('name')
            if name == product_type:
                
                # 读取Bands
                bandsElements = productElement.getElementsByTagName('Bands')
                if len(bandsElements) != 1:
                    del domxml, rootElement, propertiesElements
                    Writelog(product_type + 'Bands节点格式异常!', 0)
                    print product_type + 'Bands节点格式异常!'
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
                    Writelog(product_type + 'Typesuffixs节点格式异常!', 0)
                    print product_type + 'Typesuffixs节点格式异常!'
                    return 0
                typesuffixs_ = typesuffixsElements[0].getAttribute('value')
                typesuffixs_values = typesuffixs_.split(',')
                if len(typesuffixs_values) != bands_num:
                    del domxml, rootElement, propertiesElements
                    del typesuffixsElements
                    Writelog(product_type + 'Typesuffixs与波段数不一致!', 0)
                    print product_type + 'Typesuffixs与波段数不一致!'
                    return 0
                else:
                    for j in range(len(typesuffixs_values)):
                        typesuffixs[j] = typesuffixs_values[j]
                    del typesuffixsElements
                
                # 读取QAsuffixs
                QAsuffixElements = productElement.getElementsByTagName('QAsuffix')
                if len(QAsuffixElements) != 1:
                    del domxml, rootElement, propertiesElements
                    del QAsuffixElements
                    Writelog(product_type + 'QAsuffix节点格式异常!', 0)
                    print product_type + 'QAsuffix节点格式异常!'
                    return 0 
                QAsuffix = QAsuffixElements[0].getAttribute('value')   
                del QAsuffixElements                
                
                # 读取Valid_range
                valid_range = []
                valid_rangeElements = productElement.getElementsByTagName('Valid_range')
                if len(valid_rangeElements) != 1:
                    del domxml, rootElement, propertiesElements
                    del valid_rangeElements
                    Writelog(product_type + 'Valid_range节点格式异常!', 0)
                    print product_type + 'Valid_range节点格式异常!'
                    return 0
                elements = valid_rangeElements[0].getElementsByTagName('Element')
                if len(elements) != (bands_num-1):
                    del domxml, rootElement, propertiesElements
                    del valid_rangeElements, elements
                    Writelog(product_type + 'Valid_range节点格式异常!', 0)
                    print product_type + 'Valid_range节点格式异常!'
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
                    Writelog(product_type + 'Fillvalue节点格式异常!', 0)
                    print product_type + 'Fillvalue节点格式异常!'
                    return 0
                elements = fillvalueElements[0].getElementsByTagName('Element')
                if len(elements) != bands_num:
                    del domxml, rootElement, propertiesElements
                    del fillvalueElements, elements
                    Writelog(product_type + 'Fillvalue与波段数不一致!', 0)
                    print product_type + 'Fillvalue与波段数不一致!'
                    return 0
                else:
                    for element_ in elements:
                        fillvalue.append(map(int, element_.getAttribute('value').split(',')))
                    del fillvalueElements, elements
                
                # 读取Scale_factor
                scale_factorElements = productElement.getElementsByTagName('Scale_factor')
                if len(scale_factorElements) != 1:
                    del domxml, rootElement, propertiesElements
                    Writelog(product_type + 'Scale_factor节点格式异常!', 0)
                    print product_type + 'Scale_factor节点格式异常!'
                    return 0
                scale_factors = map(float, scale_factorElements[0].getAttribute('value').split(','))
                if len(scale_factors) != (bands_num-1):
                    del domxml, rootElement, propertiesElements
                    Writelog(product_type + 'Scale_factor与波段数不一致!', 0)
                    print product_type + 'Scale_factor与波段数不一致!'
                    return 0
                
                # 读取Resolution
                resolutionElements = productElement.getElementsByTagName('Resolution')
                if len(resolutionElements) != 1:
                    del domxml, rootElement, propertiesElements
                    Writelog(product_type + 'Resolution节点异常!', 0)
                    print product_type + 'Resolution节点异常!'
                    return 0
                resolution = resolutionElements[0].getAttribute('value')
                del resolutionElements
                
                return [bands, typesuffixs, QAsuffix, valid_range, fillvalue, scale_factors, resolution]
                
                break
            else:
                continue


# 预设回传文件
def PreReceiptXML(xmlfile, QA, product_type, typesuffixs):
    
    doc = xmldom.Document()    
    rootnode = doc.createElement('Configurations')
    doc.appendChild(rootnode)
    propertynodes = doc.createElement('Properties')
    rootnode.appendChild(propertynodes)
    
    if QA == 'ON':
        
        for typesuffix in typesuffixs:
            element = doc.createElement(product_type+'_'+typesuffix)
            propertynodes.appendChild(element)
            element.setAttribute('path', ' ')
            element.setAttribute('status', '0')
            
            Qelement = doc.createElement(product_type+'_'+typesuffix+'_Q')
            propertynodes.appendChild(Qelement)
            Qelement.setAttribute('path', ' ')
            Qelement.setAttribute('status', '0')
            
    else: 
        
        for typesuffix in typesuffixs:
            element = doc.createElement(product_type+'_'+typesuffix)
            propertynodes.appendChild(element)
            element.setAttribute('path', ' ')
            element.setAttribute('status', '0')


    with open(xmlfile, 'w') as f:
        f.write(doc.toprettyxml(indent = '\t', encoding='UTF-8'))
        
    del propertynodes, rootnode, doc
    
    if os.path.exists(xmlfile):
        return 1
    else:
        return 0
    

# 修改回传文件
def ModifiedReceiptXML(xmlfile, QA, product_type, typesuffix, outfile, Qoutfile):
    
    domxml = xmldom.parse(xmlfile)
    # 根节点
    rootElement = domxml.documentElement
    # properties节点
    propertiesElements = rootElement.getElementsByTagName('Properties')    
    if len(propertiesElements) != 1:
        del domxml, rootElement, propertiesElements
        Writelog('XML文件格式异常!', 0)
        print 'XML文件格式异常!'
        return 0
    propertiesElement = propertiesElements[0]
    
    typesuffix_Element = propertiesElement.getElementsByTagName(product_type+'_'+typesuffix)
    if len(typesuffix_Element) != 1:
        del domxml, rootElement, propertiesElements, typesuffix_Element 
        Writelog('XML文件格式异常!', 0)
        print 'XML文件格式异常!'
        return 0
    typesuffix_Element[0].setAttribute('path', outfile)
    typesuffix_Element[0].setAttribute('status', '1')
    
    if QA == 'ON':
        typesuffix_Element = propertiesElement.getElementsByTagName(product_type+'_'+typesuffix+'_Q')
        if len(typesuffix_Element) != 1:
            del domxml, rootElement, propertiesElements, typesuffix_Element 
            Writelog('XML文件格式异常!', 0)
            print 'XML文件格式异常!'
            return 0
        typesuffix_Element[0].setAttribute('path', Qoutfile)
        typesuffix_Element[0].setAttribute('status', '1')        
        pass
    
    with open(xmlfile, 'w') as f:
        f.write(domxml.toxml('UTF-8'))     

    del domxml, rootElement, propertiesElements, propertiesElement
    del typesuffix_Element 
    
    return 1       


# 执行程序
def ExcuteProcess_MOD09A1(inputfiles, product_type, bands,
                       projection ,resolution, ranges, typesuffixs,
                       valid_range, fillvalue, scale_factor,
                       tempdir, restxtfile, outfile, ndwifile):
    
    # 预设回传文件
    resdir = os.path.dirname(restxtfile)
    if os.path.exists(resdir) == False:
        os.mkdir(resdir)
        
    with open(restxtfile,'w') as resf:
        resf.write('0: \n')
    del resf    
    
    Writelog('开始处理...', 1)    
    
    # 全球HDF数据分组
    Writelog('开始对全球HDF数据分组...', 1)
    res = mrt.GetSlice_HDF(inputfiles, product_type)
    if res == 0:
        Writelog('全球HDF数据分组失败!', 0)
        return 0
    else:
        Writelog('全球HDF数据分组完成!', 1)
        localfiles = res           

    # 分组HDF数据镶嵌投影
    Writelog('开始对分组数据镶嵌投影...', 1)
    res = mrt.MRTProcess(inputfiles, tempdir, localfiles, bands, projection, resolution, ranges, typesuffixs)
    if res == 0 :
        Writelog(loginfofile, '分组数据镶嵌投影失败！', 0)
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
        Writelog('NDWI计算完成!', 1)
        Writelog('处理全部完成!', 1)
        # 修改回传文件
        with open(restxtfile,'w') as resf:
            resf.write('1; '+ndwifile)
        del resf  
              
        return 1
    else:
        Deletedir(tempdir)
        Writelog('NDWI计算失败!'+error, 0)
        Writelog('处理全部完成!', 1)
        return 0


# 执行程序
def ExcuteProcess_MOD15A2H(inputfiles, product_type, bands,
                           projection ,resolution, ranges, typesuffixs, QAsuffix,
                           valid_range, fillvalue, scale_factor, QA,
                           tempdir, restxtfile, outfile, outfileq):
    
    Writelog('开始处理...', 1)    
    
    # 全球HDF数据分组
    Writelog('开始对全球HDF数据分组...', 1)
    res = mrt.GetSlice_HDF(inputfiles, product_type)
    if res == 0:
        Writelog('全球HDF数据分组失败!', 0)
        return 0
    else:
        Writelog('全球HDF数据分组完成!', 1)
        localfiles = res 
    del res, inputfiles
        
    # 分组HDF数据镶嵌投影
    Writelog('开始对分组数据镶嵌投影...', 1)
    res = mrt.MRTProcess(tempdir, localfiles, bands, projection, resolution, ranges, typesuffixs)
    if res == 0 :
        Writelog('分组数据镶嵌投影失败！', 0)
        return 0
    else:
        Writelog('分组数据镶嵌投影完成！', 1)
        localregisterfiles = res
    del res, localfiles
    
    # 筛选出质量码波段
    index_ = typesuffixs.index(QAsuffix)
    QAregisterfiles = localregisterfiles.pop(index_)
    typesuffixs.pop(index_)

    # 全球数据拼接并裁剪
    globalfiles = []
    for i in range(len(localregisterfiles)):      
        Writelog('开始镶嵌全球' + str(typesuffixs[i]) + '数据...', 1)
        strs = os.path.basename(outfile[i]).split('.')
        globalfile = tempdir + os.path.sep + strs[0] + '_.' + strs[1] 
        ret = mrt.Mosaic(globalfile, localregisterfiles[i], fillvalue[i][0])
        if ret == 1 :
            Writelog('全球' + str(typesuffixs[i]) + '数据镶嵌完成!', 1)
        else:
            Writelog('全球' + str(typesuffixs[i]) + '数据镶嵌失败!', 0)
            continue
       
        # 定标过滤无效值    
        Writelog('开始对' + str(typesuffixs[i]) + '全球数据定标过滤无效值...', 1)
        globalvalidfile = tempdir + os.path.sep + strs[0] + '_valid.' + strs[1]
        ret = mrt.Valid_block(globalfile, valid_range[i], fillvalue[i], scale_factor[i], globalvalidfile)
        if ret == 1 :
            globalfiles.append(globalvalidfile)
            Writelog(str(typesuffixs[i]) + '全球数据定标过滤无效值完成!', 1)
        else:
            Writelog(str(typesuffixs[i]) + '全球数据定标过滤无效值失败!', 0)
            continue
        
        #=======================================================================
        # # 按照Ranges范围裁剪输出
        # Writelog('开始裁剪' + globalvalidfile + '...', 0)
        # subfile = tempdir + os.path.sep + strs[0] + '_valid_sub.' + strs[1]
        # gdal.Translate(subfile, globalvalidfile, projWin=ranges)
        # if os.path.exists(subfile):
        #     globalfiles.append(subfile)
        #     Writelog(globalvalidfile + '裁剪完成!', 1)
        # else:
        #     Writelog(globalvalidfile + '裁剪失败!', 0)
        #     continue
        # os.remove(globalvalidfile)
        #=======================================================================
    
    if len(globalfiles) == 0:
        Writelog('所有数据裁剪失败!', 0)
        return 0

    # 筛选质量码波段
    if QA == 'ON':
        Writelog('开始镶嵌全球' + str(QAsuffix) + '数据...', 1)
        QAfile = tempdir + os.path.sep + product_type + '_' + QAsuffix + '.tif'
        ret = mrt.Mosaic(QAfile, QAregisterfiles, fillvalue[index_][0])
        if ret == 1:
            Writelog('全球' + str(QAsuffix) + '数据镶嵌完成!', 1)
        else:
            Writelog('全球' + str(QAsuffix) + '数据镶嵌失败!', 0)
            return 0
            
        #=======================================================================
        # # 按照Ranges范围裁剪输出
        # Writelog('开始裁剪' + str(QAsuffix), 0)
        # subQAfile = tempdir + os.path.sep + product_type + '_' + QAsuffix + '_sub.tif'
        # gdal.Translate(subQAfile, QAfile, projWin=ranges)
        # if os.path.exists(subQAfile):
        #     Writelog(str(QAsuffix) + '裁剪完成!', 1)
        # else:
        #     Writelog(str(QAsuffix) + '裁剪失败!', 0)
        #     return 0
        # os.remove(QAfile)
        #=======================================================================
        
        subQAfile = QAfile
        
        for i in range(len(globalfiles)) :
            Writelog('开始对' + globalfiles[i] + '执行质量控制..', 1)
            ret = mrt.QualityControl_MOD13A2(subQAfile, globalfiles[i], outfileq[i])
            if ret == 1:
                Writelog(globalfiles[i] + '质量控制完成!', 1)
            else:
                Writelog(globalfiles[i] + '质量控制失败!', 0)
                continue
            
            # 同时保留未执行质量控制的数据
            shutil.move(globalfiles[i], outfile[i])
            
            Writelog('开始修改' + str(typesuffixs[i]) + '回传文件...', 1)
            ret = ModifiedReceiptXML(restxtfile, QA, product_type, typesuffixs[i], outfile[i], outfileq[i])
            if ret == 1:
                Writelog(str(typesuffixs[i]) + '回传文件修改完成!', 1)
            else:
                Writelog(str(typesuffixs[i]) + '回传文件修改失败!', 0)
            
    else:
        for i in range(len(globalfiles)) :
            shutil.move(globalfiles[i], outfile[i])
            
            Writelog('开始修改' + str(typesuffixs[i]) + '回传文件...', 1)
            ret = ModifiedReceiptXML(restxtfile, QA, product_type, typesuffixs[i], outfile[i], '')
            if ret == 1:
                Writelog(str(typesuffixs[i]) + '回传文件修改完成!', 1)
            else:
                Writelog(str(typesuffixs[i]) + '回传文件修改失败!', 0)

    # Deletedir(tempdir)
    Writelog('处理全部完成!', 1)    
    return 1
    

# 主函数
def MODISPRO(configfile, loginfofile_):
    '''
    # 执行MODIS数据预处理
    :param configfile:    参数文件
    :param loginfofile_:    传入的日志文件
    :return: 1--执行成功, 0--执行失败
    '''
    
    # 将日志文件设为全局变量
    global loginfofile
    loginfofile = loginfofile_
    if os.path.exists(os.path.dirname(loginfofile)) == False:
        os.makedirs(os.path.dirname(loginfofile))    
    
    # 记录开始时间    
    starttime_ = datetime.datetime.now()        

    # 判断MRT工具是否存在    
    pwdpath = os.path.realpath(__file__)
    resampleexe = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'MRT' + os.path.sep + \
                    'bin' + os.path.sep + 'resample.exe'    
    if os.path.exists(resampleexe) == False:
        Writelog(resampleexe + '工具不存在!', 0)
        print resampleexe + '工具不存在!'
        return 0
        
    mrtmosaicexe = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'MRT' + os.path.sep + \
                    'bin' + os.path.sep + 'mrtmosaic.exe'
    if os.path.exists(mrtmosaicexe) == False:
        Writelog(mrtmosaicexe + '工具不存在!', 0)
        print mrtmosaicexe + '工具不存在!'
        return 0
        
    mrtdatadir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'MRT' + os.path.sep + 'data'
    if os.path.exists(mrtdatadir) == False:
        Writelog(mrtdatadir + '路径不存在!', 0)
        print mrtdatadir + '路径不存在!'
        return 0
       
    # 读取参数文件
    # 返回参数依次是产品类型(Product_Type),投影(Projection),地理范围(Ranges),质量控制标识(QA),输出文件名(OutputFiles),
    #          输出文件名(OutputFilesQ),回传文件(ReceiptFile),输入文件列表(InputFiles)
    if os.path.exists(configfile) == False:
        Writelog(configfile + '参数文件不存在!', 0)
        print configfile + '参数文件不存在!'
        return 0
    Product_Type = ReadConfig(configfile, 'Product_Type')
    if Product_Type == None:
        print configfile + '读取Product_Type失败!'
        return 0
    Projection = ReadConfig(configfile, 'Projection')
    if Projection == None:
        print configfile + '读取Projection失败!'
        return 0    
    Ranges = ReadConfig(configfile, 'Ranges')
    if Ranges == None:
        print configfile + '读取Ranges失败!'
        return 0
    Ranges = map(float, ((Ranges.strip(']')).strip('[')).split(','))
    QA = ReadConfig(configfile, 'QA')
    if QA == None:
        print configfile + '读取QA失败!'
        return 0    
    OutputFiles = ReadConfig(configfile, 'OutputFiles')
    if OutputFiles == None:
        print configfile + '读取OutputFiles失败!'
        return 0    
    OutputFilesQ = ReadConfig(configfile, 'OutputFilesQ')
    if OutputFilesQ == None:
        print configfile + '读取OutputFilesQ失败!'
        return 0
    ReceiptFile = ReadConfig(configfile, 'ReceiptFile')
    if ReceiptFile == None:
        print configfile + '读取ReceiptFile失败!'
        return 0    
    InputFiles = ReadConfig(configfile, 'InputFiles')
    if InputFiles == None:
        print configfile + '读取InputFiles失败!'
        return 0
    
    OutputFiles = OutputFiles.split(';')
    OutputFilesQ = OutputFilesQ.split(';')
    if (len(OutputFiles) != 2 or len(OutputFilesQ) != 2) and (Product_Type == 'MOD15A2H'):
        Writelog(configfile + '参数文件输出文件名数量有误!', 0)
        print configfile + '参数文件输出文件名数量有误!'
        return 0
    
    print 'Product_Type: ', Product_Type
    print 'Projection: ', Projection
    print 'Ranges: ', Ranges
    print 'QA: ', QA
    print 'ReceiptFile: ', ReceiptFile
    print 'OutputFiles: ', OutputFiles
    print 'OutputFilesQ: ', OutputFilesQ
    print 'InputFiles: ', InputFiles
    
    # 判断输出路径是否存在,不存在则创建
    for outfile in OutputFiles:
        if os.path.exists(os.path.dirname(outfile)) == False:
            os.makedirs(os.path.dirname(outfile))
    if QA == 'ON' :
        for outfile in OutputFilesQ:
            if os.path.exists(os.path.dirname(outfile)) == False:
                os.makedirs(os.path.dirname(outfile))     

    # 读取系统配置文件
    sysconfigfile = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'system' + os.path.sep + 'system.xml'
    if os.path.exists(sysconfigfile) == False:
        Writelog(sysconfigfile+'文件不存在!', 0)
        print sysconfigfile+'不存在!'
        return 0
    systeminfo = ReadSystemConfig(sysconfigfile, Product_Type)
    if systeminfo == 0:
        Writelog(sysconfigfile + '读取失败! ', 0)
        print sysconfigfile + '读取失败! '
        return 0
    elif systeminfo == None:
        Writelog('参数文件设置的产品类型与系统配置文件中不匹配!', 0)
        print '参数文件设置的产品类型与系统配置文件中不匹配!'
        return 0
    else:
        bands = systeminfo[0]
        typesuffixs = systeminfo[1]
        QAsuffix = systeminfo[2]
        valid_range = systeminfo[3]
        fillvalue = systeminfo[4]
        scale_factor = systeminfo[5]
        resolution = systeminfo[6]
        
    print 'bands: ', bands
    print 'typesuffixs: ', typesuffixs
    print 'QAsuffix: ', QAsuffix
    print 'valid_range: ', valid_range
    print 'fillvalue: ', fillvalue
    print 'scale_factor: ', scale_factor
    print 'resolution: ', resolution
    
    # 预设回传文件
    resdir = os.path.dirname(ReceiptFile)
    if os.path.exists(resdir) == False:
        os.makedirs(resdir)   
    
    typesuffixs_ = deepcopy(typesuffixs)
    res = typesuffixs_.pop(typesuffixs_.index(QAsuffix))
    
    Writelog('开始预设回传文件' + ReceiptFile + '...', 1)
    ret = PreReceiptXML(ReceiptFile, QA, Product_Type, typesuffixs_)
    if ret == 1:
        Writelog(ReceiptFile + '回传文件预设完成!', 1)
    else:
        Writelog(ReceiptFile + '回传文件预设失败!', 0)
        return 0
    
    del res, typesuffixs_ 
 
    
    # 创建临时路径
    tempdir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'temp'
    if os.path.exists(tempdir) == False:
        os.mkdir(tempdir)
    tempdir = tempdir + os.path.sep + str(time.time()).strip()
    os.mkdir(tempdir)

    try:
        if Product_Type == 'MOD09A1':
            tempfile = [tempdir + (os.path.basename(OutputFiles[0]).split('.'))[0] + '_GEO_500m_SUR2.tif',
                        tempdir + (os.path.basename(OutputFiles[0]).split('.'))[0] + '_GEO_500m_SUR7.tif']
            
            ret = ExcuteProcess_MOD09A1(InputFiles, Product_Type, bands,
                                           Projection ,resolution, Ranges, typesuffixs, QAsuffix, 
                                           valid_range, fillvalue, scale_factor, QA,
                                           tempdir, loginfofile, ReceiptFile, tempfile, OutputFiles, OutputFilesQ)
            
        else:
            ret = ExcuteProcess_MOD15A2H(InputFiles, Product_Type, bands,
                                           Projection ,resolution, Ranges, typesuffixs, QAsuffix,
                                           valid_range, fillvalue, scale_factor, QA, 
                                           tempdir, ReceiptFile, OutputFiles, OutputFilesQ)
        if ret != 1:
            print '最终处理失败!'            
            return 0
        else:
            print '开始时间: ', starttime_
            print '结束时间: ', datetime.datetime.now()
            return 1 
    except Exception,e:
        Writelog(e.message, 0)
        print e
        return 0
    finally:
        Deletedir(tempdir)

    
if __name__ == '__main__':
    MODISPRO( )
    
