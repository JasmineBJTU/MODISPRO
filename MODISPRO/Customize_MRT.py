#!/usr/bin/env python
# coding:utf-8
#
# Description:
#
#
# Author: LC
# Date: 2018-10-13
#

import os
try:
    from osgeo import gdal
except ImportError:
    import gdal
import re
import math
import MODISPRO_Global


# 获得各分组HDF文件
def GetSlice_HDF(tfiles, product_type):

    hstrs = ['h0[6-9]', 'h1[0-3]', 'h1[4-6]', 'h1[7-9]', 'h2[0-3]', 'h2[4-6]', 'h2[7-9]', 'h3[0-2]']
    localfiles_ = [[] for i in range(len(hstrs))]

    for i in range(len(tfiles)):
        for j in range(len(hstrs)):
            p = re.compile(r'M' + product_type[1:] + '\.A\d{7}\.' + hstrs[j] + 'v[01][0-9]\.006\.\d{13}\.hdf')
            if re.match(p, os.path.basename(tfiles[i])):
                localfiles_[j].append(tfiles[i])
                continue

    # 筛选有数据的分块
    localfiles = []
    for t in range(len(localfiles_)):
        if len(localfiles_[t]) > 0:
            localfiles.append(localfiles_[t])

    del localfiles_, tfiles, hstrs
    if len(localfiles) > 1:
        return localfiles
    else:
        MODISPRO_Global.Writelog('指定路径中没有' + product_type + '数据!', 0)
        return 0


# 生成MRT镶嵌配置文件
def Writemosaicprm(mosfname, files):
    fobj = open(mosfname, 'w')

    if len(files) == 0:
        return 0

    for tfile in files:
        fobj.write(tfile + '\n')

    fobj.close()
    del fobj
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
        smajor = 0.0;
        sminor = 0.0;
        stdpr1 = 25;
        stdpr2 = 47
        centmer = 110;
        originlat = 0.0;
        fe = 4000000.0;
        fn = 0.0
        fobj.write('OUTPUT_PROJECTION_TYPE = AEA' + '\n')
        fobj.write('OUTPUT_PROJECTION_PARAMETERS = (' + '\n')
        fobj.write(' ' + str(smajor) + ' ' + str(sminor) + ' ' + str(stdpr1) + ' ' + '\n')
        fobj.write(' ' + str(stdpr2) + ' ' + str(centmer) + ' ' + str(originlat) + ' ' + '\n')
        fobj.write(' ' + str(fe) + ' ' + str(fn) + ' 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0 )' + '\n')
        fobj.write('DATUM = WGS84' + '\n')
    elif projection == 'Lambert':
        smajor = 0.0;
        sminor = 0.0;
        stdpr1 = 0.0;
        stdpr2 = 0.0
        centmer = 0.0;
        originlat = 0.0;
        fe = 0.0;
        fn = 0.0
        fobj.write('OUTPUT_PROJECTION_TYPE = ' + projection + '\n')
        fobj.write('OUTPUT_PROJECTION_PARAMETERS = (' + '\n')
        fobj.write(' ' + str(smajor) + ' ' + str(sminor) + ' ' + str(stdpr1) + ' ' + '\n')
        fobj.write(' ' + str(stdpr2) + ' ' + str(centmer) + ' ' + str(originlat) + ' ' + '\n')
        fobj.write(' ' + str(fe) + ' ' + str(fn) + ' 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0 )' + '\n')
        fobj.write('DATUM = NoDatum' + '\n')
    elif projection == 'Mercator':
        ranges = map(float, ranges)
        centmer = (ranges[0] + ranges[2]) / 2.0;
        fe = 0.0;
        fn = 0.0
        truescale = 1.0 / (math.cos(math.radians((ranges[1] + ranges[3]) / 2.0)))
        fobj.write('OUTPUT_PROJECTION_TYPE = ' + projection + '\n')
        fobj.write('OUTPUT_PROJECTION_PARAMETERS = (' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 ' + str(centmer) + ' ' + str(truescale) + '\n')
        fobj.write(' ' + str(fe) + ' ' + str(fn) + ' 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0 )' + '\n')
        fobj.write('DATUM = WGS84' + '\n')
    elif projection == 'TM':
        smajor = 0.0;
        sminor = 0.0;
        factor = 0.0;
        centmer = 0.0;
        originlat = 0.0;
        fe = 0.0;
        fn = 0.0
        fobj.write('OUTPUT_PROJECTION_TYPE = ' + projection + '\n')
        fobj.write('OUTPUT_PROJECTION_PARAMETERS = (' + '\n')
        fobj.write(' ' + str(smajor) + ' ' + str(sminor) + ' ' + str(factor) + '\n')
        fobj.write(' 0.0' + str(centmer) + ' ' + str(originlat) + '\n')
        fobj.write(' ' + str(fe) + ' ' + str(fn) + ' 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0 )' + '\n')
        fobj.write('DATUM = NoDatum' + '\n')
    elif projection == 'UTM':
        lon = 0.0;
        lat = 0.0;
        utmzone = 0.0
        fobj.write('OUTPUT_PROJECTION_TYPE = ' + projection + '\n')
        fobj.write('OUTPUT_PROJECTION_PARAMETERS = (' + '\n')
        fobj.write(' ' + str(lon) + ' ' + str(lat) + ' 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0' + '\n')
        fobj.write(' 0.0 0.0 0.0 )' + '\n')
        fobj.write('UTM_ZONE = ' + str(utmzone))
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
        return '投影类型设置有误!' + projection

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

    dirname = (os.path.split(registerfile))[0]
    filename = (os.path.split(registerfile))[1]
    filename_ = filename.split('.')

    tfiles = []
    for typesuffix in typesuffixs:
        tfile = dirname + os.path.sep + filename_[0] + '.' + typesuffix + '.tif'
        if os.path.exists(tfile):
            tfiles.append(tfile)

    if os.path.exists(mosaicfile): os.remove(mosaicfile)
    if os.path.exists(regfname): os.remove(regfname)
    return tfiles


def MRTProcess(tempdir, groups_files, bands, projection, resolution, suffixs, ranges):

    processed_files = {}
    for t in range(len(suffixs)): processed_files[suffixs[t]] = []

    for i in range(len(groups_files)):
        mosaic_prm_file = tempdir + "mosaic_" + ("%03i" % i) + ".prm"
        ret = Writemosaicprm(mosaic_prm_file, groups_files[i])
        if ret == 0:
            MODISPRO_Global.Writelog(str(i) + "组镶嵌配置文件生成失败!", 0)
            return 0
        else:
            MODISPRO_Global.Writelog(str(i) + "组镶嵌配置文件生成完成!", 1)

        temp_mosaic_file = tempdir + "mosaic_" + ("%03i" % i) + ".hdf"
        ret = Excutemosaic(mosaic_prm_file, temp_mosaic_file, bands)
        if ret == 0:
            MODISPRO_Global.Writelog(str(i) + "组HDF数据镶嵌失败!", 0)
            return 0
        else:
            MODISPRO_Global.Writelog(str(i) + "组HDF数据镶嵌完成!", 1)

        resample_prm_file = tempdir + "resample_" + ("%03i" % i) + ".prm"
        temp_resample_file = tempdir + "resample_" + ("%03i" % i) + ".tif"
        ret = Writeresampleprm(resample_prm_file, temp_mosaic_file, temp_resample_file, projection, resolution, ranges)
        if ret == 0:
            MODISPRO_Global.Writelog(str(i) + "组投影配置文件生成失败!", 0)
            return 0
        else:
            MODISPRO_Global.Writelog(str(i) + "组投影配置文件生成完成!", 1)

        ret = Excuteresample(temp_mosaic_file, resample_prm_file, temp_resample_file, suffixs)
        if ret == 0 :
            MODISPRO_Global.Writelog(str(i) + "组HDF数据投影失败!", 0)
            return 0
        else:
            MODISPRO_Global.Writelog(str(i) + "组HDF数据投影完成!", 1)
            for j in range(len(ret)):
                processed_files[suffixs[j]].append(ret[j])

    return processed_files