# coding:utf-8
'''
Created on 2018年7月5日
@author: Administrator
'''

import os
from osgeo import gdal_array
try:
    from osgeo import gdal
except ImportError:
    import gdal
import numpy as np
import math, re
import Auxiliary_Func as aux


# 获取指定路径下hdf格式数据文件名
def GetFilename(path):
    list_name = []
    for tfile in os.listdir(path):
        file_path = os.path.join(path, tfile)
        if os.path.isdir(file_path):
            pass
        elif os.path.splitext(file_path)[1] == '.hdf':
            list_name.append(file_path)
    if len(list_name) > 0:
        return list_name
    else:        
        return 0
    

# 生成MRT镶嵌配置文件
def Writemosaicprm(mosfname, indir):
    fobj = open(mosfname, 'w')
    hdffiles = GetFilename(indir)
    
    if hdffiles == 0:
        return 0
    
    for tfile in hdffiles:
        fobj.write(tfile + '\n')
        
    fobj.close()
    del fobj, hdffiles    
    return 1


# MRT执行Mosaic操作    
def Excutemosaic(mosfile, mosaicfile, bands):
    
    pwdpath = os.path.realpath(__file__)
        
    mrtbindir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'MRT' + os.path.sep + 'bin' 
    mrtdatadir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'MRT' + os.path.sep + 'data'

    os.system('set MRT_DATA_DIR=' + mrtdatadir + '&&' + \
              mrtbindir + os.path.sep + 'mrtmosaic.exe -i ' + mosfile + ' -s ' + '"' + bands + '"' + ' -o ' + mosaicfile)  
    
    if os.path.exists(mosaicfile):
        if os.path.exists(mosfile): os.remove(mosfile)
        return 1
    else:
        return 0

    
# 生成MRT几何校正配置文件  
def Writeresampleprm(regfname, mosaicfile, registerfile, projection, resolution, ranges):
    fobj = open(regfname, 'w')
    fobj.write('INPUT_FILENAME = ' + mosaicfile + '\n')
#    fobj.write('SPECTRAL_SUBSET = ( ' + bands + ' )' + '\n')
    fobj.write('SPATIAL_SUBSET_TYPE = INPUT_LAT_LONG' + '\n')
#    fobj.write('SPATIAL_SUBSET_UL_CORNER = (' + ranges[1] + ' ' + ranges[0] + ')\n')
#    fobj.write('SPATIAL_SUBSET_LR_CORNER = (' + ranges[3] + ' ' + ranges[2] + ')\n')
    fobj.write('OUTPUT_FILENAME = ' + registerfile + '\n')
    fobj.write('RESAMPLING_TYPE = NEAREST_NEIGHBOR' + '\n')
        
    if projection == 'Albers':
        smajor=0.0;sminor=0.0;stdpr1=0.0;stdpr2=0.0
        centmer=0.0;originlat=0.0;fe=0.0;fn=0.0
        fobj.write('OUTPUT_PROJECTION_TYPE = ' + projection + '\n')
        fobj.write('OUTPUT_PROJECTION_PARAMETERS = (' + '\n')
        fobj.write(' '+str(smajor)+' '+str(sminor)+' '+str(stdpr1)+' '+ '\n')
        fobj.write(' '+str(stdpr2)+' '+str(centmer)+' '+str(originlat)+' '+ '\n')
        fobj.write(' '+str(fe)+' '+str(fn)+' 0.0'+ '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0 )' + '\n')
        fobj.write('DATUM = NoDatum' + '\n')
    elif projection == 'Lambert':
        smajor=0.0;sminor=0.0;stdpr1=0.0;stdpr2=0.0
        centmer=0.0;originlat=0.0;fe=0.0;fn=0.0        
        fobj.write('OUTPUT_PROJECTION_TYPE = ' + projection + '\n')
        fobj.write('OUTPUT_PROJECTION_PARAMETERS = (' + '\n')
        fobj.write(' '+str(smajor)+' '+str(sminor)+' '+str(stdpr1)+' '+ '\n')
        fobj.write(' '+str(stdpr2)+' '+str(centmer)+' '+str(originlat)+' '+ '\n')
        fobj.write(' '+str(fe)+' '+str(fn)+' 0.0'+ '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0 )' + '\n')
        fobj.write('DATUM = NoDatum' + '\n')
    elif projection == 'Mercator':
        ranges=map(float,ranges)
        centmer=(ranges[0]+ranges[2])/2.0;fe=0.0;fn=0.0
        truescale=1.0/(math.cos(math.radians((ranges[1]+ranges[3])/2.0)))
        fobj.write('OUTPUT_PROJECTION_TYPE = ' + projection + '\n')
        fobj.write('OUTPUT_PROJECTION_PARAMETERS = (' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n') 
        fobj.write(' 0.0 '+str(centmer)+' '+str(truescale)+ '\n')
        fobj.write(' '+str(fe)+' '+str(fn)+' 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0 )' + '\n')
        fobj.write('DATUM = WGS84' + '\n')
    elif projection == 'TM':
        smajor=0.0;sminor=0.0;factor=0.0;centmer=0.0;originlat=0.0;fe=0.0;fn=0.0
        fobj.write('OUTPUT_PROJECTION_TYPE = ' + projection + '\n')
        fobj.write('OUTPUT_PROJECTION_PARAMETERS = (' + '\n')
        fobj.write(' '+str(smajor)+' '+str(sminor)+' '+str(factor)+ '\n')
        fobj.write(' 0.0'+str(centmer)+' '+str(originlat)+ '\n')
        fobj.write(' '+str(fe)+' '+str(fn)+' 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0 )' + '\n')
        fobj.write('DATUM = NoDatum' + '\n') 
    elif projection == 'UTM':
        lon=0.0;lat=0.0;utmzone=0.0
        fobj.write('OUTPUT_PROJECTION_TYPE = ' + projection + '\n')
        fobj.write('OUTPUT_PROJECTION_PARAMETERS = (' + '\n')
        fobj.write(' '+str(lon)+' '+str(lat)+' 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0 )' + '\n')
        fobj.write('UTM_ZONE = '+str(utmzone))
        fobj.write('DATUM = NoDatum' + '\n')
    elif projection == 'GEO':
        fobj.write('OUTPUT_PROJECTION_TYPE = ' + projection + '\n')
        fobj.write('OUTPUT_PROJECTION_PARAMETERS = (' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0 )' + '\n')
        fobj.write('DATUM = WGS84' + '\n')
    else:
        fobj.close()
        del fobj
        return '投影类型设置有误!'+projection

    fobj.write('OUTPUT_PIXEL_SIZE = ' + resolution + '\n')
    fobj.close
    del fobj
    return 1   


# MRT执行Register操作  
def Excuteresample(mosaicfile, regfname, registerfile, typesuffixs):
    
    pwdpath = os.path.realpath(__file__)
        
    mrtbindir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'MRT' + os.path.sep + 'bin' 
    mrtdatadir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'MRT' + os.path.sep + 'data'    

    os.system('set MRT_DATA_DIR=' + mrtdatadir + '&&' + \
              mrtbindir + os.path.sep + 'resample.exe -p ' + regfname)
    
    dirname=(os.path.split(registerfile))[0]
    filename=(os.path.split(registerfile))[1]
    filename_=filename.split('.')
    
    tfiles=[]
    for typesuffix in typesuffixs:
        tfile = dirname+os.path.sep+filename_[0]+'.'+typesuffix+'.tif'
        if os.path.exists(tfile):
            tfiles.append(tfile)  
                  
    if os.path.exists(mosaicfile): os.remove(mosaicfile)
    if os.path.exists(regfname): os.remove(regfname)
    return tfiles


# 过滤无效值
def Valid_Single(tfile, valid_range, fillvalue, scale_factor, outfile):
    indataset = gdal.Open(tfile)
    if indataset is None:
        print '打开'+tfile+'失败!'
        return 0
    driver = indataset.GetDriver()
    
    # 读取原始数据
    inband = indataset.GetRasterBand(1)    
    tempdata = inband.ReadAsArray()
    
    # 获取原始数据无效值
    condition_1 = np.logical_or(tempdata<valid_range[0], tempdata>valid_range[1])
    index_1 = np.where(condition_1)
    condition_2 = np.logical_and(tempdata==fillvalue[0], tempdata==fillvalue[0])
    index_2 = np.where(condition_2)

    tempdata = tempdata*scale_factor
    
    # 剔除无效值
    tempdata[index_1] = fillvalue[1]
    tempdata[index_2] = fillvalue[1]
    del condition_1, condition_2, index_1, index_2    
    
    # 输出数据文件
    outdataset = driver.Create(outfile, indataset.RasterXSize, indataset.RasterYSize,1, gdal.GDT_Float32)
    outdataset.SetGeoTransform(indataset.GetGeoTransform())
    outdataset.SetProjection(indataset.GetProjectionRef())
    outband = outdataset.GetRasterBand(1)
    outband.WriteArray(tempdata)
    
    tempdata = None
    del indataset, inband, outband, outdataset
    
    if os.path.exists(outfile):
        if os.path.exists(tfile):
            os.remove(tfile)
        return 1
    else:
        return 0


# 过滤无效值
def Valid_block(tfile, valid_range, fillvalue, scale_factor, outfile):
    indataset = gdal.Open(tfile)
    if indataset is None:
        print '打开'+tfile+'失败!'
        return 0
    driver = indataset.GetDriver()
    
    # 读取原始数据
    inband = indataset.GetRasterBand(1)
    cols = indataset.RasterXSize
    rows = indataset.RasterYSize        

    # 输出数据文件
    outdataset = driver.Create(outfile,indataset.RasterXSize, indataset.RasterYSize, 1, gdal.GDT_Float32)
    outdataset.SetGeoTransform(indataset.GetGeoTransform())
    outdataset.SetProjection(indataset.GetProjectionRef())
    outband = outdataset.GetRasterBand(1)
    
    rowstep = rows/40
    for i in range(0,rows,rowstep):
        if i+rowstep < rows:
            numrows = rowstep
        else:
            numrows = rows-i
        tempdata = inband.ReadAsArray(0, i, cols, numrows)
        
        # 获取原始数据无效值
        condition_1 = np.logical_or(tempdata<valid_range[0], tempdata>valid_range[1])
        index_1 = np.where(condition_1)
        condition_2 = np.logical_and(tempdata==fillvalue[0], tempdata==fillvalue[0])
        index_2 = np.where(condition_2)
                
        tempdata = tempdata*scale_factor
        
        # 剔除无效值
        tempdata[index_1] = fillvalue[1]
        tempdata[index_2] = fillvalue[1]
        del condition_1, condition_2, index_1, index_2
        outband.WriteArray(tempdata, 0, i)
        tempdata = None
    outband.SetNoDataValue(-999.0)

    del indataset, inband, outband, outdataset
    
    if os.path.exists(tfile):
        os.remove(tfile)
    
    if os.path.exists(outfile):
        return 1
    else:
        return 0


# 利用MRT处理各分组HDF文件
def MRTProcess(tempdir, localfiles, bands, projection, resolution, ranges, typesuffixs):
    
    localregisterfiles = [[] for i in range(len(typesuffixs))]
    for i in range(len(localfiles)):
        t = i + 1
        aux.Writelog('开始生成' + str(t).strip() + '分组HDF数据的镶嵌配置文件...', 1)
        mosfname = tempdir + os.path.sep + 'mosaic_' + str(t).strip() + '.prm'
        with open(mosfname, 'w') as f:
            for tfile in localfiles[i]:
                f.write(tfile+'\n')
        if os.path.exists(mosfname):
            aux.Writelog(str(t).strip() + '分组HDF数据的镶嵌配置文件输出完成!', 1)
        else:
            aux.Writelog(str(t).strip() + '分组HDF数据的镶嵌配置文件输出失败!', 0)
            continue
        
        aux.Writelog('开始镶嵌' + str(t).strip() + '分组HDF数据...', 1)
        mosaicfile = tempdir + os.path.sep + 'mosaic_' + str(t).strip() + '.hdf'
        ret = Excutemosaic(mosfname, mosaicfile, bands)
        if ret == 1 :
            aux.Writelog(str(t).strip() + '分组HDF数据的镶嵌完成!', 1)
        else:
            aux.Writelog(str(t).strip() + '分组HDF数据的镶嵌失败!', 0)
            continue
        
        aux.Writelog('开始生成' + str(t).strip() + '分组HDF数据校正的配置文件...', 1)
        registerfile = tempdir + os.path.sep + 'register_' + str(t).strip() + '.tif'
        regfname = tempdir + os.path.sep + 'register_' + str(t).strip() + '.prm'
        ret = Writeresampleprm(regfname, mosaicfile, registerfile, projection, resolution, ranges)
        if ret == 1 :
            aux.Writelog(str(t).strip() + '分组HDF数据校正配置文件输出完成!', 1)
        else:
            aux.Writelog(str(t).strip() + '分组HDF数据校正配置文件输出失败', 10)
            continue
        
        aux.Writelog('开始校正' + str(t).strip() + '分组HDF数据...', 1)
        files = Excuteresample(mosaicfile, regfname, registerfile, typesuffixs)
        if type(files) == list and len(typesuffixs) == len(files):
            aux.Writelog(str(t).strip() + '分组HDF数据校正完成!', 1)
            for j in range(len(files)):
                localregisterfiles[j].append(files[j])            
        else:
            aux.Writelog(str(t).strip() + '分组HDF数据校正失败!', 0)
            continue
    
    if len(localregisterfiles) > 0:
        return localregisterfiles
    else:
        aux.Writelog('所有分块MRT处理失败!', 0)
        print '所有分块MRT处理失败!'
        return 0


# 获得各分块HDF文件
def GetSlice_HDF(tfiles, product_type):
    '获得各分块HDF文件'

    hstrs = ['h0[7-9]', 'h1[0-3]', 'h1[4-6]', 'h1[7-9]', 'h2[0-3]', 'h2[4-6]', 'h2[7-9]', 'h3[0-2]']
    localfiles_ = [[] for i in range(len(hstrs))]

    for i in range(len(tfiles)):
        for j in range(len(hstrs)):
            p = re.compile(r'M'+product_type[1:]+'\.A\d{7}\.'+hstrs[j]+'v[01][0-9]\.006\.\d{13}\.hdf')
            if re.match(p, os.path.basename(tfiles[i])):
                localfiles_[j].append(tfiles[i])
                continue
    
    # 筛选有数据的分块
    localfiles = []
    for t in range(len(localfiles_)):
        if len(localfiles_[t]) > 0 :            
            localfiles.append(localfiles_[t])

    del localfiles_, tfiles, hstrs
    if len(localfiles) > 1:
        return localfiles
    else:
        aux.Writelog('指定路径中没有'+product_type+'数据!', 0)
        print '指定路径中没有'+product_type+'数据!'
        return 0


# 利用GDAL镶嵌各分块投影数据
def Mosaic(registerfile, localregisterfiles, fillvalue):

    if fillvalue == '' :
        warpparameters = gdal.WarpOptions(format='GTiff', resampleAlg=gdal.GRIORA_NearestNeighbour, 
                                          multithread=True)     
    else:
        warpparameters = gdal.WarpOptions(format='GTiff', resampleAlg=gdal.GRIORA_NearestNeighbour, 
                                          multithread=True, srcNodata=fillvalue) #, dstNodata=fillvalue[0]        

    gdal.Warp(registerfile, localregisterfiles, options=warpparameters)
    
    for tfile in localregisterfiles:
        if os.path.exists(tfile):
            os.remove(tfile)
    
    if os.path.exists(registerfile):
        return 1
    else:
        return 0
    
    
# 质量控制
def QualityControl_MOD13A2(QAfile, orignalfile, qualityfile):
    indataset = gdal.Open(orignalfile)
    if indataset is None:
        aux.Writelog('打开'+orignalfile+'失败!', 0)
        print '打开'+orignalfile+'失败!'
        return 0
    driver = indataset.GetDriver()
    
    qadataset = gdal.Open(QAfile)
    if qadataset is None:
        aux.Writelog('打开'+QAfile+'失败!', 0)
        print '打开'+QAfile+'失败!'
        return 0

    inband = indataset.GetRasterBand(1)    
    cols = indataset.RasterXSize
    rows = indataset.RasterYSize 
    qaband = qadataset.GetRasterBand(1)          

    # 输出数据文件
    outdataset = driver.Create(qualityfile, indataset.RasterXSize, indataset.RasterYSize, 1, gdal.GDT_Float32)
    outdataset.SetGeoTransform(indataset.GetGeoTransform())
    outdataset.SetProjection(indataset.GetProjectionRef())
    outband = outdataset.GetRasterBand(1)
    
    rowstep = rows/40
    for i in range(0,rows,rowstep):
        if i+rowstep < rows:
            numrows = rowstep
        else:
            numrows = rows-i
        tempdata_ = inband.ReadAsArray(0, i, cols, numrows)  
        tempdata = np.zeros(tempdata_.shape)-999.0
        qualdata = qaband.ReadAsArray(0, i, cols, numrows) 
                
        condition_1 = np.logical_and((qualdata != 65535), (qualdata >= 32768))
        index_1 = np.where(condition_1)
        qualdata[index_1] -= 32768
        condition_2 = np.logical_and((qualdata != 65535), (qualdata >= 16384))
        index_2 = np.where(condition_2)
        qualdata[index_2] -= 16384
        condition_3 = np.logical_and((qualdata != 65535), (qualdata < 4096))
        index_3 = np.where(condition_3)
        tempdata[index_3] = tempdata_[index_3]

        outband.WriteArray(tempdata, 0, i)    
        tempdata = None; tempdata_= None
        qualdata = None
    outband.SetNoDataValue(-999.0)   
    
    del inband, indataset, qaband, qadataset, outband, outdataset 
        
    if os.path.exists(qualityfile):
        os.remove(QAfile)
        return 1    
    else:
        return 0   


# 波段运算计算NDWI
def Computendwi_Block(infiles, valid_range, fillvalue, scale_factor, ndwifile, error):
    
    if len(infiles) != 2:
        error = '输入文件数量异常!'
        print error
        return 0
    
    inb2dataset = gdal.Open(infiles[0])
    if inb2dataset == None:
        error = infiles[0] + '打开失败!'
        print error
        return 0
    inb7dataset = gdal.Open(infiles[1])
    if inb2dataset == None:
        error = infiles[1] + '打开失败!'
        print error
        return 0    
    inb2band = inb2dataset.GetRasterBand(1)
    inb7band = inb7dataset.GetRasterBand(1)
    cols = inb2dataset.RasterXSize
    rows = inb2dataset.RasterYSize
    driver = inb2dataset.GetDriver()
    
    # 输出数据文件
    outdataset = driver.Create(ndwifile, inb2dataset.RasterXSize,inb2dataset.RasterYSize, 1, gdal.GDT_Float32)
    outdataset.SetGeoTransform(inb2dataset.GetGeoTransform())
    outdataset.SetProjection(inb2dataset.GetProjectionRef())
    outband = outdataset.GetRasterBand(1)
    
    rowstep = rows/80
    for i in range(0,rows,rowstep):
        if i+rowstep < rows:
            numrows = rowstep
        else:
            numrows = rows-i
        b2tempdata = inb2band.ReadAsArray(0, i, cols, numrows) 
        b7tempdata = inb7band.ReadAsArray(0, i, cols, numrows)

        # 获取原始数据无效值
        b2condition_1 = np.logical_or(b2tempdata<valid_range[0][0],b2tempdata>valid_range[0][1])
        b2condition_2 = np.logical_not(fillvalue[0][0])
        b7condition_1 = np.logical_or(b7tempdata<valid_range[1][0],b7tempdata>valid_range[1][1])
        b7condition_2 = np.logical_not(fillvalue[1][0])
        condition = np.logical_and((b2tempdata+b7tempdata)==0,(b2tempdata+b7tempdata)==0)
        index_1 = np.where(b2condition_1)
        index_2 = np.where(b2condition_2)
        index_3 = np.where(b7condition_1)
        index_4 = np.where(b7condition_2)
        index_5 = np.where(condition)
        
        # 去除分母为0 
        b2tempdata[index_5] = 1; b7tempdata[index_5] = 1
               
        # 波段运算
        tempndwi_ = (b2tempdata*scale_factor[0]-b7tempdata*scale_factor[1])/(b2tempdata*scale_factor[0]+b7tempdata*scale_factor[1])
        tempndwi = gdal_array.numpy.nan_to_num(tempndwi_)
        tempndwi_ = None
        
        # 剔除无效值
        tempndwi[index_1] = fillvalue[0][1]
        tempndwi[index_2] = fillvalue[0][1]
        tempndwi[index_3] = fillvalue[0][1] 
        tempndwi[index_4] = fillvalue[0][1]
        tempndwi[index_5] = fillvalue[0][1]
        b2tempdata = None; b7tempdata = None     

        # NDWI限定在(-1,1)范围内
        condition = np.logical_or(tempndwi<-1, tempndwi>1)
        index = np.where(condition)
        tempndwi[index] = fillvalue[0][1]
        
        outband.WriteArray(tempndwi, 0, i)    
        tempndwi = None

    del inb2dataset, inb7dataset, inb2band, inb7band, driver, outdataset, outband
    del b2condition_1, b2condition_2, b7condition_1, b7condition_2, condition
    del index_1, index_2, index_3, index_4, index_5
    
    if os.path.exists(ndwifile):
        for tfile in infiles:
            os.remove(tfile)
        return 1    
    else:
        return 0

