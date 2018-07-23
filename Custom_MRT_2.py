# coding:utf-8
'''
Created on 2018年7月5日
@author: Administrator
'''

import os, sys
from osgeo import gdal_array
try:
    from osgeo import gdal
except ImportError:
    import gdal
import numpy as np
import math, re
import Auxiliary_Func_2 as aux


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
def Excutemosaic(exename, mosfile, mosaicfile, bands):
    
    mrtdir = os.path.dirname(exename)
    mrtdatadir = os.path.dirname(mrtdir) + os.path.sep + 'data'
#    mrthomedir = os.path.dirname(mrtdir)
#    os.system('set MRT_DATA_DIR=' + mrtdatadir + '&&' + \
#              'set MRT_HOME=' + mrthomedir + '&&' + \
#              'mrtmosaic -i ' + mosfile + ' -s ' + '"' + bands + '"' + ' -o ' + mosaicfile)    

    os.system('set MRT_DATA_DIR=' + mrtdatadir + '&&' + \
              mrtdir + os.path.sep + 'bin' + os.path.sep + 'mrtmosaic.exe -i ' + mosfile + ' -s ' + '"' + bands + '"' + ' -o ' + mosaicfile)  
    
    if os.path.exists(mosaicfile):
        if os.path.exists(mosfile): os.remove(mosfile)
        return 1
    else:
        return 0

    
# 生成MRT几何校正配置文件  
def Writeresampleprm(regfname, mosaicfile, bands, registerfile, projection, resolution, ranges):
    fobj = open(regfname, 'w')
    fobj.write('INPUT_FILENAME = ' + mosaicfile + '\n')
    fobj.write('SPECTRAL_SUBSET = ( ' + bands + ' )' + '\n')
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
def Excuteresample(mosaicfile, exename, regfname, registerfile, typesuffixs):
    
    mrtdir = os.path.dirname(exename)
    mrtdatadir = os.path.dirname(mrtdir) + os.path.sep + 'data'
#    mrthomedir = os.path.dirname(mrtdir)
#    os.system('set MRT_DATA_DIR=' + mrtdatadir + '&&' + \
#              'set MRT_HOME=' + mrthomedir + '&&' + 'resample -p ' + regfname)

    os.system('set MRT_DATA_DIR=' + mrtdatadir + '&&' + \
              mrtdir + os.path.sep + os.path.sep + 'resample.exe -p ' + regfname)
    
    dirname=(os.path.split(registerfile))[0]
    filename=(os.path.split(registerfile))[1]
    filename_=filename.split('.')
    
    tfiles=[]
    for typesuffix in typesuffixs:
        tfile = dirname+os.path.sep+filename_[0]+'.'+typesuffix+'.tif'
        if os.path.exists(tfile):
            tfiles.append(tfile)  

    if os.path.exists(regfname): os.remove(regfname)
    if os.path.exists(mosaicfile): os.remove(mosaicfile)
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
    condition_1 = np.logical_or(tempdata<valid_range[0],tempdata>valid_range[1])
    index_1 = np.where(condition_1)
    condition_2 = np.logical_and(tempdata==fillvalue[0],tempdata==fillvalue[0])
    index_2 = np.where(condition_2)

    tempdata = tempdata*scale_factor
    
    # 剔除无效值
    tempdata[index_1] = fillvalue[1]
    tempdata[index_2] = fillvalue[1]
    del condition_1, condition_2, index_1, index_2    
    
    # 输出数据文件
    outdataset = driver.Create(outfile,indataset.RasterXSize,indataset.RasterYSize,1,gdal.GDT_Float32)
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


# 利用MRT处理各单幅HDF文件
def MRTPRocess_Single(indir, product_type, loginfofile, tempdir, resampleexe, typesuffixs,
                      bands, projection, ranges, resolution, valid_range, fillvalue, scale_factor):
    
    calfiles = [[] for i in range(len(typesuffixs))]
    tfiles = os.listdir(indir)
    for tfile in tfiles:
        
        p = re.compile(r'M'+product_type[1:]+'\.A\d{7}\.h[0-3][0-9]v[0-1][0-9]\.006\.\d{13}\.hdf')
        if re.match(p, tfile):
            
            aux.Writelog(loginfofile, '开始处理' + tfile + '...', 1)
            
            strs = tfile.split('.')
            registerfile_ = tempdir + os.path.sep + '_'.join(strs[0:5]) + '.tif'
            tfile = indir +os.path.sep + tfile
            regfname = tempdir + os.path.sep + '_'.join(strs[0:5]) + '_Register.prm'
                        
            aux.Writelog(loginfofile, '开始生成' + regfname + '...', 1)            
            res = Writeresampleprm(regfname, tfile, bands, registerfile_, projection, resolution, ranges)
            if res != 1:                
                aux.Writelog(loginfofile, regfname + '生成失败!', 0)
                print regfname+'生成失败!'+res
                continue
            else:
                aux.Writelog(loginfofile, regfname + '输出完成!', 1)
                
                        
            aux.Writelog(loginfofile, '开始对'+tfile+'赋投影...', 1)
            mosaicfile = ''        
            registerfile = Excuteresample(mosaicfile, resampleexe, regfname, registerfile_, typesuffixs)
            if len(registerfile) == 0:
                aux.Writelog(loginfofile, tfile + '赋投影失败!', 0)
                print tfile+'赋投影失败!'
                continue
            else:
                aux.Writelog(loginfofile, tfile + '赋投影完成!', 1)
            
            for i in range(len(typesuffixs)):
                calfile = tempdir + os.path.sep + '_'.join(strs[0:5]) + '_Cal' + typesuffixs[i] + '.tif'
                aux.Writelog(loginfofile, '开始对'+registerfile[i]+'定标,过滤无效值...', 1)
                res = Valid_Single(registerfile[i], valid_range[i], fillvalue[i], scale_factor[i], calfile)
                if res != 1:
                    aux.Writelog(loginfofile, registerfile[i] + '定标过滤无效值失败!', 0)
                    print registerfile+'定标失败!'
                    continue
                else:                
                    calfiles[i].append(calfile)  
                    aux.Writelog(loginfofile, registerfile[i] + '定标过滤无效值完成!', 1)               
                
    tfiles = None
    return calfiles


# 利用MRT处理各分块HDF文件
def MRTProcess_Block(indir, localfiles,
                    mosaicexe, mosfname, mosaicfile, bands, 
                    regfname, registerfile0, projection, resolution, ranges, resampleexe, typesuffixs,
                    valid_range, fillvalue, scale_factor):
    
    t = 1; localregisterfiles = []
    for localfiles_ in localfiles:
        
        with open(mosfname, 'w') as f:
            for tfile in localfiles_:
                f.write(indir+os.path.sep+tfile+'\n')
        
        ret = Excutemosaic(mosaicexe, mosfname, mosaicfile, bands)
        if ret != 1 :
            print '镶嵌失败!'
            continue
        
        strs = registerfile0.split('.')
        registerfile = strs[0]+'_'+str(t).strip()+'.'+strs[1]
        ranges = []
        ret = Writeresampleprm(regfname, mosaicfile, registerfile, projection, resolution, ranges)
        if ret != 1 :
            print ret 
            continue
        
        files = Excuteresample(mosaicfile, resampleexe, regfname, registerfile, typesuffixs)
        
        ret = Valid_Single(files[0], valid_range, fillvalue, scale_factor, registerfile)
        if ret == 0 :
            print '无效值过滤失败!'
            continue
        else:
            localregisterfiles.append(registerfile)
        
        t += 1    
    
    if len(localregisterfiles) > 0:
        return localregisterfiles
    else:
        return '所有分块MRT处理失败!'


# 获得各分块tif文件
def GetSlice_TIF(calfiles, product_type):
    '获得各分块HDF文件'

    hstrs = ['h0[7-9]', 'h1[0-3]', 'h1[4-7]', 'h1[8-9]', 'h2[0-3]', 'h2[4-7]', 'h2[8-9]', 'h3[0-2]']
    localfiles_ = [[] for i in range(len(hstrs))]
    
    for i in range(len(calfiles)):
        for j in range(len(hstrs)):
            p = re.compile(r'M'+product_type[1:]+'_A\d{7}_'+hstrs[j]+'v[01][0-9]_006_\d{13}_.*\.tif')
            strs = os.path.split(calfiles[i])
            if re.match(p, strs[1]):
                localfiles_[j].append(calfiles[i])
                continue
    
    localfiles = []
    for j in range(len(localfiles_)):
        if len(localfiles_[j]) > 0 :            
            localfiles.append(localfiles_[j])

    del localfiles_, calfiles, hstrs
    if len(localfiles) > 1:
        return localfiles
    else:
        return '指定路径中没有'+product_type+'定标后数据!'


# 获得各分块HDF文件
def GetSlice_HDF(calfiles, product_type):
    '获得各分块HDF文件'

    hstrs = ['h0[7-9]', 'h1[0-3]', 'h1[4-7]', 'h1[8-9]', 'h2[0-3]', 'h2[4-7]', 'h2[8-9]', 'h3[0-2]']
    localfiles_ = [[] for i in range(len(hstrs))]
    
    for i in range(len(calfiles)):
        for j in range(len(hstrs)):
            p = re.compile(r'M'+product_type[1:]+'_A\d{7}_'+hstrs[j]+'v[01][0-9]_006_\d{13}\.hdf')
            strs = os.path.split(calfiles[i])
            if re.match(p, strs[1]):
                localfiles_[j].append(calfiles[i])
                continue
    
    localfiles = []
    for j in range(len(localfiles_)):
        if len(localfiles_[j]) > 0 :            
            localfiles.append(localfiles_[j])

    del localfiles_, calfiles, hstrs
    if len(localfiles) > 1:
        return localfiles
    else:
        return '指定路径中没有'+product_type+'定标后数据!'


# 利用GDAL镶嵌各分块投影数据
def Mosaic(registerfile, localregisterfiles, fillvalue):

    warpparameters = gdal.WarpOptions(format='GTiff', resampleAlg=gdal.GRIORA_NearestNeighbour, 
                                      multithread=True, srcNodata=fillvalue) 
    gdal.Warp(registerfile, localregisterfiles, options=warpparameters)
    
    for tfile in localregisterfiles:
        if os.path.exists(tfile):
            os.remove(tfile)
    
    if os.path.exists(registerfile):
        return 1
    else:
        return 0


# 层级镶嵌(先局部分块镶嵌,最后全球镶嵌)
def Hierarchical_Mosaic(calfiles, loginfofile, tempdir, 
                        product_type, fillvalue, outfile):
    
    aux.Writelog(loginfofile, '开始对全球数据分块...', 1)    
    res = GetSlice_TIF(calfiles, product_type)
    if type(res) == list:
        block_calfiles = res
        aux.Writelog(loginfofile, '全球数据分块完成!', 1)
    else:
        aux.Writelog(loginfofile, '全球数据分块失败!', 0)
        aux.Deletedir(tempdir)
        print '全球数据分块失败!'   
    
    
    aux.Writelog(loginfofile, '开始对全球数据进行一级镶嵌...', 1)    
    t = 1; tempoutfiles = []    
    for block_calfiles_ in block_calfiles:
        tfilename = os.path.basename(outfile)
        strs = tfilename.split('.')
        tempoutfile = tempdir + os.path.sep + strs[0] + '_'+str(t).strip()+'.'+strs[1]
        ret = Mosaic(tempoutfile, block_calfiles_, fillvalue[1])
        if ret == 0 :
            aux.Writelog(loginfofile, str(t).strip() + '分块全球数据一级镶嵌失败!', 0) 
            print '分块tiff数据镶嵌失败!'
            continue
        else:
            tempoutfiles.append(tempoutfile)
            t += 1
            aux.Writelog(loginfofile, str(t).strip() + '分块全球数据一级镶嵌完成!', 1) 
    if len(tempoutfiles) == 0:
        aux.Writelog(loginfofile, '全球数据一级分块镶嵌均失败!', 0)
        aux.Deletedir(tempdir)
        sys.exit()
    else:
        aux.Writelog(loginfofile, '全球数据一级分块镶嵌全部完成!', 1)
    
    
    aux.Writelog(loginfofile, '开始对全球数据进行二级镶嵌...', 1) 
    ret = Mosaic(outfile, tempoutfiles, fillvalue[1])
    if ret == 0 :
        aux.Writelog(loginfofile, '全球数据二级镶嵌失败!', 0) 
        aux.Deletedir(tempdir)
        print '全球分块tiff数据镶嵌失败!' 
        return 0
    else:
        aux.Writelog(loginfofile, '全球数据二级镶嵌完成!', 1)
        return 1


# 波段运算计算NDWI
def Computendwi(b2file, b7file, valid_range, fillvalue, scale_factor, ndwifile):
    inb2dataset = gdal.Open(b2file)
    inb7dataset = gdal.Open(b7file)
    driver = inb2dataset.GetDriver()
     
    #读取band2\band7原始数据       
    band2 = inb2dataset.GetRasterBand(1)
    b2arr = band2.ReadAsArray()
    band7 = inb7dataset.GetRasterBand(1)
    b7arr = band7.ReadAsArray()
    
    #获取原始数据无效值
    b2condition_1 = np.logical_or(b2arr<valid_range[0],b2arr>valid_range[1])
    b2condition_2 = np.logical_not(fillvalue[0])
    b7condition_1 = np.logical_or(b2arr<valid_range[0],b2arr>valid_range[1])
    b7condition_2 = np.logical_not(fillvalue[0])
    condition = np.logical_and((b2arr+b7arr)==0,(b2arr+b7arr)==0)
    index_1 = np.where(b2condition_1)
    index_2 = np.where(b2condition_2)
    index_3 = np.where(b7condition_1)
    index_4 = np.where(b7condition_2)
    index_5 = np.where(condition)
    
    #去除分母为0 
    b2arr[index_5] = 1;b7arr[index_5] = 1
           
    #波段运算
    ndwi_ = ((b2arr-b7arr)*scale_factor)/((b2arr+b7arr)*scale_factor)
    ndwi = gdal_array.numpy.nan_to_num(ndwi_)
    
    #剔除无效值
    ndwi[index_1] = fillvalue[1]
    ndwi[index_2] = fillvalue[1] 
    ndwi[index_3] = fillvalue[1] 
    ndwi[index_4] = fillvalue[1]
    ndwi[index_5] = fillvalue[1]
    b2arr = None;b7arr = None;ndwi_ = None
    
    #NDWI限定在(-1,1)范围内
    condition = np.logical_or(ndwi<-1,ndwi>1)
    index = np.where(condition)
    ndwi[index] = fillvalue[1]
    
    #输出NDWI文件
    outdataset = driver.Create(ndwifile,inb2dataset.RasterXSize,inb2dataset.RasterYSize,1,gdal.GDT_Float32)
    outdataset.SetGeoTransform(inb2dataset.GetGeoTransform())
    outdataset.SetProjection(inb2dataset.GetProjectionRef())    
    outband = outdataset.GetRasterBand(1)
    outband.WriteArray(ndwi)
    
    ndwi = None
    del b2arr,b7arr,ndwi_,ndwi
    del inb2dataset,inb7dataset,driver,outdataset,outband
    del b2condition_1,b2condition_2,b7condition_1,b7condition_2,condition
    del index_1,index_2,index_3,index_4,index_5
    
    if os.path.exists(ndwifile):
        if os.path.exists(b2file):
            os.remove(b2file)
        if os.path.exists(b7file):
            os.remove(b7file)
        return 1    
    else:
        return 0