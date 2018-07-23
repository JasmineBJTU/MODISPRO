# coding:utf-8
'''
Created on 2018年7月16日
@author: Administrator
'''


import os, sys
import time, datetime
import Custom_MRT_2 as mrt


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
    tfiles = os.listdir(tempdir)
    if len(tfiles) > 0:
        for tfile in tfiles:
            tfile = tempdir + os.path.sep + tfile
            if os.path.exists(tfile):
                os.remove(tfile)
    os.rmdir(tempdir)
    

# 读取参数文件
def ReadConfig(configfile):
    paramstrs = [' '] * 6
    with open(configfile, 'r') as f:
        for i in range(6): 
            # 去除行尾'\n'          
            paramstr = (f.readline()).strip('\n')
            if not paramstr: break
            print paramstr  
            if len(paramstr.split('=')) != 2:
                return '参数文件格式异常!'            
            # 去除首尾空格
            paramstrs[i] = ((paramstr.split('='))[1]).strip()

    return paramstrs


# 执行程序
# 逐幅HDF投影定标,再分块局部镶嵌,最后全球镶嵌
def ExcuteProcess_MOD09A1(product_type, projection, ranges, indir, 
                          bands, typesuffixs, valid_range, fillvalue, scale_factor, resolution, 
                          tempdir, resampleexe, 
                          restxtfile, loginfofile, outfile):

    # 预设回传文件
    resdir = os.path.dirname(restxtfile)
    if os.path.exists(resdir) == False:
        os.mkdir(resdir)
    with open(restxtfile,'w') as resf:
        resf.write('0: ')
    del resf
    
    Writelog(loginfofile, '开始处理...', 1)
        
    if os.path.exists(tempdir) == False:
        os.mkdir(tempdir)
    tempdir = tempdir + os.path.sep + str(time.time()).strip()
    os.mkdir(tempdir)
    
    if os.path.exists(resampleexe) == False:
        Writelog(loginfofile, resampleexe+'工具不存在!', 0)
        Deletedir(tempdir)
        sys.exit()
    
    # 逐幅投影定标
    calfiles = mrt.MRTPRocess_Single(indir, product_type, loginfofile, tempdir, resampleexe, typesuffixs,
                                    bands, projection, ranges, resolution, valid_range, fillvalue, scale_factor)

    if len(calfiles) < 1:
        Writelog(loginfofile, '指定路径下所有数据文件MRT处理失败!', 0)
        print '指定路径下所有数据文件MRT处理失败!'
        Deletedir(tempdir)
        sys.exit()

    # 层级镶嵌 
    with open(restxtfile,'w+') as resf:
        restrs = resf.readlines(len(typesuffixs))
    for i in range(len(calfiles)):        
        res = mrt.Hierarchical_Mosaic(calfiles[i], loginfofile, tempdir, product_type, fillvalue[i], outfile[i])
        if res != 1:
            print typesuffixs[i] + '层级镶嵌失败!'
            with open(restxtfile,'w') as resf:
                restrs[i] = '0; ' + typesuffixs[i] + '处理失败!' + '\n'
                resf.writelines(restrs)
        else:
            print typesuffixs[i] + '层级镶嵌完成!'
            with open(restxtfile,'w') as resf:
                restrs[i] = '1; '+outfile[i] + '\n'
                resf.writelines(restrs)            
        del resf
        
    Deletedir(tempdir)

    Writelog(loginfofile, '全部处理完成!', 1) 
    return 1


# 执行程序
# 逐幅HDF投影定标,再分块局部镶嵌,最后全球镶嵌
def ExcuteProcess_MOD15A2H(product_type, projection, ranges, indir, 
                          bands, typesuffixs, valid_range, fillvalue, scale_factor, resolution, 
                          tempdir, resampleexe, 
                          restxtfile, loginfofile, outfile):

    # 预设回传文件
    resdir = os.path.dirname(restxtfile)
    if os.path.exists(resdir) == False:
        os.mkdir(resdir)
        
    with open(restxtfile,'w') as resf:
        for i in range(len(typesuffixs)):
            resf.write('0: \n')
    del resf
    
    Writelog(loginfofile, '开始处理...', 1)
        
    if os.path.exists(tempdir) == False:
        os.mkdir(tempdir)
    tempdir = tempdir + os.path.sep + str(time.time()).strip()
    os.mkdir(tempdir)
    
    if os.path.exists(resampleexe) == False:
        Writelog(loginfofile, resampleexe+'工具不存在!', 0)
        Deletedir(tempdir)
        sys.exit()
    
    # 逐幅投影定标
    calfiles = mrt.MRTPRocess_Single(indir, product_type, loginfofile, tempdir, resampleexe, typesuffixs,
                                    bands, projection, ranges, resolution, valid_range, fillvalue, scale_factor)

    if len(calfiles) < 1:
        Writelog(loginfofile, '指定路径下所有数据文件MRT处理失败!', 0)
        print '指定路径下所有数据文件MRT处理失败!'
        Deletedir(tempdir)
        sys.exit()
    
    # 层级镶嵌 
    with open(restxtfile,'r+') as resf:
        restrs = resf.readlines(len(typesuffixs))
    for i in range(len(calfiles)):        
        res = mrt.Hierarchical_Mosaic(calfiles[i], loginfofile, tempdir, product_type, fillvalue[i], outfile[i])
        if res != 1:
            print typesuffixs[i] + '层级镶嵌失败!'
            with open(restxtfile,'w') as resf:
                restrs[i] = '0; ' + typesuffixs[i] + '处理失败!' + '\n'
                resf.writelines(restrs)
        else:
            print typesuffixs[i] + '层级镶嵌完成!'
            with open(restxtfile,'w') as resf:
                restrs[i] = '1; ' + outfile[i] + '\n'
                resf.writelines(restrs)            
        del resf
        
    Deletedir(tempdir)

    Writelog(loginfofile, '全部处理完成!', 1) 
    return 1


# 主函数
def MODISPRO_2(configfile, restxtfile, loginfofile):
    
    starttime_ = datetime.datetime.now()
    pwdpath = os.path.realpath(__file__)
        
    resampleexe = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'resource' + os.path.sep + \
                    'MRT' + os.path.sep + 'bin' + os.path.sep + 'resample.exe'    
    if os.path.exists(resampleexe) == False:
        print resampleexe+'工具不存在!'
        sys.exit()
        
    mrtmosaicexe = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'resource' + os.path.sep + \
                    'MRT' + os.path.sep + 'bin' + os.path.sep + 'mrtmosaic.exe'
    if os.path.exists(mrtmosaicexe) == False:
        print mrtmosaicexe+'工具不存在!'
        sys.exit()
        
    mrtdatadir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'resource' + os.path.sep + \
                    'MRT' + os.path.sep + 'data'
    if os.path.exists(mrtdatadir) == False:
        print mrtdatadir + '路径不存在!'
        sys.exit()  
    
    tempdir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'temp'
    if os.path.exists(tempdir) == False:
        os.mkdir(tempdir)
    
    # 读取参数文件
    # 返回参数依次是产品类型(Product_Type),日期(DataDate),投影(Projection),地理范围(Ranges),输入路径(InputFolder),输出路径(OutputFolder)
    paramstrs = ReadConfig(configfile)
    if len(paramstrs) != 6:
        print '参数文件读取失败!'
        sys.exit()
    
    Product_Type = paramstrs[0]
    DataDate = paramstrs[1]
    Projection = paramstrs[2]
    Ranges = paramstrs[3]
    InputFolder = paramstrs[4]
    OutputFolder = paramstrs[5]
    
    # 判断输出路径是否存在
    if os.path.exists(OutputFolder) == False:
        os.mkdir(OutputFolder)
        
    if Product_Type == 'MOD09A1':
        bands = '1 1 0 0 0 0 0 0 0 0 0 0 0' 
        typesuffixs = ['sur_refl_b01', 'sur_refl_b02']
        valid_range = [[-100,16000], [-100,16000]]
        fillvalue = [[-28672,-999], [-28672,-999]] 
        scale_factor = [0.0001, 0.0001]
        resolution = '0.005'
        #outfile = OutputFolder + os.path.sep + Product_Type + '_' + DataDate + '_Global_NDWI_500m_GEO.tif'
        outfile = [OutputFolder + os.path.sep + Product_Type + '_' + DataDate + '_Global_SUR1_500m_GEO.tif',
                   OutputFolder + os.path.sep + Product_Type + '_' + DataDate + '_Global_SUR2_500m_GEO.tif']
        
        ret = ExcuteProcess_MOD15A2H(Product_Type, Projection, Ranges, InputFolder,
                                        bands, typesuffixs, valid_range, fillvalue, scale_factor, resolution, 
                                        tempdir, resampleexe, 
                                        restxtfile, loginfofile, outfile)
        
    elif Product_Type == 'MOD13A2':
        bands = '1 0 0 0 0 0 0 0 0 0 0 0' 
        typesuffixs = ['1_km_16_days_NDVI']
        valid_range = [[-2000,10000]]
        fillvalue = [[-3000,-999]] 
        scale_factor = [0.0001]
        resolution = '0.01'
        outfile = [OutputFolder + os.path.sep + Product_Type + '_' + DataDate + '_Global_NDVI_1000m_GEO.tif']
        
        ret = ExcuteProcess_MOD15A2H(Product_Type, Projection, Ranges, InputFolder,
                                        bands, typesuffixs, valid_range, fillvalue, scale_factor, resolution, 
                                        tempdir, resampleexe, 
                                        restxtfile, loginfofile, outfile)
        
    elif Product_Type == 'MOD15A2H':
        bands = '1 1 0 0 0 0' 
        typesuffixs = ['Fpar_500m', 'Lai_500m']
        valid_range = [[0,100], [0,100]]
        fillvalue = [[255,-999], [255,-999]]
        scale_factor = [0.01, 0.1]
        resolution = '0.005'
        outfile = [OutputFolder + os.path.sep + Product_Type + '_' + DataDate + '_Global_FPAR_500m_GEO.tif',
                   OutputFolder + os.path.sep + Product_Type + '_' + DataDate + '_Global_LAI_500m_GEO.tif']
        
        ret = ExcuteProcess_MOD15A2H(Product_Type, Projection, Ranges, InputFolder,
                                        bands, typesuffixs, valid_range, fillvalue, scale_factor, resolution, 
                                        tempdir, resampleexe, 
                                        restxtfile, loginfofile, outfile)        
        
    elif Product_Type == 'MOD16A2':
        bands = '1 0 0 0 0' 
        typesuffixs = ['ET_500m']
        valid_range = [[-32767,32700]]
        fillvalue = [[32767,-999]] 
        scale_factor = [0.1]
        resolution = '0.005'
        outfile = [OutputFolder + os.path.sep + Product_Type + '_' + DataDate + '_Global_ET_500m_GEO.tif']
        
        ret = ExcuteProcess_MOD15A2H(Product_Type, Projection, Ranges, InputFolder,
                                        bands, typesuffixs, valid_range, fillvalue, scale_factor, resolution, 
                                        tempdir, resampleexe, 
                                        restxtfile, loginfofile, outfile)        

    elif Product_Type == 'MYD13A2':
        bands = '1 0 0 0 0 0 0 0 0 0 0 0' 
        typesuffixs = ['1_km_16_days_NDVI']
        valid_range = [[-2000,10000]]
        fillvalue = [[-3000,-999]] 
        scale_factor = [0.0001]
        resolution = '0.01'
        outfile = [OutputFolder + os.path.sep + Product_Type + '_' + DataDate + '_Global_NDVI_1000m_GEO.tif']
        
        ret = ExcuteProcess_MOD15A2H(Product_Type, Projection, Ranges, InputFolder,
                                        bands, typesuffixs, valid_range, fillvalue, scale_factor, resolution, 
                                        tempdir, resampleexe, 
                                        restxtfile, loginfofile, outfile)        

    else:
        print '产品类型设置有误!'
        sys.exit()
    
    if ret != 1:
        print '最终处理失败!'
    else:
        print '开始时间: ', starttime_
        print '结束时间: ', datetime.datetime.now()
        print 'finished!'    

