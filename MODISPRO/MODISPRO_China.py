#!/usr/bin/env python
# coding:utf-8
#
# Description:
#
#
# Author: LC
# Date: 2018-10-17
#

import os
import re
try:
    from osgeo import gdal
except ImportError:
    import gdal
import numpy as np
from copy import deepcopy
import Customize_MRT
import MODISPRO_Global


# 处理MOD09A1产品
def ExcuteProcess_MOD09A1_China(inputfiles, product_type, datestr, projection, QA, outdir, receiptfile,
                                bands, attributes, QAsuffix, resolution, unvalid_value, ranges, tempdir, configpath):

    suffixs = attributes.keys()
    MOD09A1_suffixs = ["sur_refl_b02", "sur_refl_b04"]

    china_outdir = outdir + "China" + os.path.sep
    if not os.path.exists(china_outdir):
        os.makedirs(china_outdir)
    chinaO_outdir = outdir + "ChinaO" + os.path.sep
    if not os.path.exists(chinaO_outdir):
        os.makedirs(chinaO_outdir)

    pwdpath = os.path.realpath(__file__)
    # region_dir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + "resource" + os.path.sep + "standard" + os.path.sep
    # region_dir = region_dir + "500m" + os.path.sep
    region_dir = configpath + "standard" + os.path.sep + "500m" + os.path.sep

    # 筛选中国区HDF数据
    MODISPRO_Global.Writelog("开始筛选中国区HDF文件...", 1)
    hvstrs = ["h23v05", "h23v04", "h24v04", "h24v05", "h25v06", "h25v05", "h25v04", "h25v03", "h26v06", "h26v05",
              "h26v04", "h26v03", "h27v06", "h27v05", "h27v04", "h28v07", "h28v06", "h28v05", "h29v06"]
    infiles = [[]]
    for file_ in inputfiles:
        for hv in hvstrs:
            p = re.compile(r"M" + product_type[1:] + '\.A\d{7}\.' + hv + '.006\.\d{13}\.hdf')
            if re.match(p, os.path.basename(file_)):
                infiles[0].append(file_)
    del inputfiles
    MODISPRO_Global.Writelog("中国区HDF文件筛选完成!", 1)

    # MRT镶嵌投影
    MODISPRO_Global.Writelog("开始对中国区数据利用MRT进行镶嵌投影...", 1)
    res = Customize_MRT.MRTProcess(tempdir, infiles, bands, projection, resolution, suffixs, ranges)
    if res == 0:
        MODISPRO_Global.Writelog('分组数据镶嵌投影失败！', 0)
        return 0
    else:
        MODISPRO_Global.Writelog('分组数据镶嵌投影完成！', 1)
        mrt_processed_files = res
    del res, infiles

    # 裁剪掩膜-过滤无效值-耕地掩膜
    china_valid_files_dict = {}
    for i in range(len(suffixs)): china_valid_files_dict[suffixs[i]] = []
    china_mask_files_dict = {}
    for i in range(len(suffixs)): china_mask_files_dict[suffixs[i]] = []
    base_file = region_dir + "China.tif"
    # mask_file = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + "resource" + os.path.sep + "mask" + os.path.sep + "china2010_arableland_110_500m_4182.tif"
    mask_file = configpath + "mask" + os.path.sep + "china2010_arableland_110_500m_4182.tif"
    if not os.path.exists(base_file):
        MODISPRO_Global.Writelog(base_file + "全球标准输出文件不存在!", 0)
        return 0
    if not os.path.exists(mask_file):
        MODISPRO_Global.Writelog(mask_file + "全球耕地掩膜文件不存在!", 0)
        return 0

    for i in range(len(mrt_processed_files)):
        china_resample_file = (mrt_processed_files[suffixs[i]])[0]

        # 裁剪掩膜
        MODISPRO_Global.Writelog("开始对" + suffixs[i] + "中国数据进行裁剪标准输出...", 1)
        china_subset_file = tempdir + "China_resampled_subset_" + suffixs[i] + ".tif"
        ret = MODISPRO_Global.Subset_Mask(china_resample_file, base_file, china_subset_file, (attributes[suffixs[i]])['fillvalue'])
        if ret == 0:
            MODISPRO_Global.Writelog(suffixs[i] + "中国数据裁剪标准输出失败!", 0)
            continue
        else:
            MODISPRO_Global.Writelog(suffixs[i] + "中国数据裁剪标准输出完成!", 1)
            if os.path.exists(china_resample_file):
                os.remove(china_resample_file)

        # 过滤无效值
        MODISPRO_Global.Writelog("开始对" + suffixs[i] + "中国标准输出数据进行无效值过滤...", 1)
        if QAsuffix == "sur_refl_qc_500m":
            data_type = gdal.GDT_UInt32
        else:
            data_type = gdal.GDT_Float32
        china_valid_file = tempdir + "China_resampled_valid_" + suffixs[i] + ".tif"
        if not os.path.exists(os.path.dirname(china_valid_file)):
            os.makedirs(os.path.dirname(china_valid_file))
        ret = MODISPRO_Global.Filter_unvalid(china_subset_file, attributes[suffixs[i]], china_valid_file, unvalid_value, data_type)
        if ret == 0:
            MODISPRO_Global.Writelog(suffixs[i] + "无效值过滤失败!", 0)
            continue
        else:
            MODISPRO_Global.Writelog(suffixs[i] + "无效值过滤完成!", 1)
            china_valid_files_dict[suffixs[i]] = china_valid_file
            if os.path.exists(china_subset_file):
                os.remove(china_subset_file)

        # 耕地掩膜
        MODISPRO_Global.Writelog("开始对" + suffixs[i] + "中国标准输出数据进行耕地掩膜...", 1)
        if QAsuffix == "sur_refl_qc_500m":
            data_type = gdal.GDT_UInt32
        else:
            data_type = gdal.GDT_Float32
        china_mask_file = tempdir + "China_resampled_valid_mask_" + suffixs[i] + ".tif"
        if not os.path.exists(os.path.dirname(china_mask_file)):
            os.makedirs(os.path.dirname(china_mask_file))
        ret = MODISPRO_Global.Crop_Mask(china_valid_file, mask_file, china_mask_file, unvalid_value, data_type)
        if ret == 0:
            MODISPRO_Global.Writelog(suffixs[i] + "耕地掩膜失败!", 0)
            continue
        else:
            MODISPRO_Global.Writelog(suffixs[i] + "耕地掩膜完成!", 1)
            china_mask_files_dict[suffixs[i]] = china_mask_file

    if QA == "ON":
        suffixs.remove(QAsuffix)

    # 利用无效值过滤后的结果计算NDWI
    MODISPRO_Global.Writelog("开始利用无效值过滤后的B2和B4计算NDWI...", 1)
    for i in range(len(suffixs)):
        if len(china_valid_files_dict[suffixs[i]]) == 0:
            MODISPRO_Global.Writelog(suffixs[i] + "波段执行无效值过滤失败,不能计算NDWI", 0)
            return 0
    b2file = china_valid_files_dict[MOD09A1_suffixs[0]]
    b4file = china_valid_files_dict[MOD09A1_suffixs[1]]
    valid_ndwifile = outdir + "ChinaO" + os.path.sep + "32bit_" + datestr + ".tif"
    if not os.path.exists(os.path.dirname(valid_ndwifile)):
        os.makedirs(os.path.dirname(valid_ndwifile))
    ret = MODISPRO_Global.Calculate_NDWI(b2file, b4file, valid_ndwifile, unvalid_value)
    if ret != 1:
        MODISPRO_Global.Writelog("无效值过滤后计算NDWI失败!", 0)
    else:
        MODISPRO_Global.Writelog("无效值过滤后计算NDWI完成!", 1)
        ret = MODISPRO_Global.ModifiedXMLfile(receiptfile, product_type, "NDWI", "China", "Original", valid_ndwifile)
        if ret != 1:
            MODISPRO_Global.Writelog("回传文件对应修改" + product_type + "产品NDWI数据集China区域Original结果失败!", 0)
        else:
            MODISPRO_Global.Writelog("回传文件对应修改" + product_type + "产品NDWI数据集China区域Original结果完成!", 1)

        if os.path.exists(china_valid_files_dict[MOD09A1_suffixs[0]]):
            os.remove(china_valid_files_dict[MOD09A1_suffixs[0]])
        if os.path.exists(china_valid_files_dict[MOD09A1_suffixs[1]]):
            os.remove(china_valid_files_dict[MOD09A1_suffixs[1]])

    # 利用耕地掩膜后的结果计算NDWI
    MODISPRO_Global.Writelog("开始利用耕地掩膜后的B2和B4计算NDWI...", 1)
    for i in range(len(suffixs)):
        if len(china_mask_files_dict[suffixs[i]]) == 0:
            MODISPRO_Global.Writelog(suffixs[i] + "波段执行耕地掩膜失败,不能计算NDWI!", 0)
            return 0
    b2file = china_mask_files_dict[MOD09A1_suffixs[0]]
    b4file = china_mask_files_dict[MOD09A1_suffixs[1]]
    mask_ndwifile = outdir + "China" + os.path.sep + "32bit_" + datestr + ".tif"
    if not os.path.exists(os.path.dirname(mask_ndwifile)):
        os.makedirs(os.path.dirname(mask_ndwifile))
    ret = MODISPRO_Global.Calculate_NDWI(b2file, b4file, mask_ndwifile, unvalid_value)
    if ret != 1:
        MODISPRO_Global.Writelog("耕地掩膜后计算NDWI失败!", 0)
    else:
        MODISPRO_Global.Writelog("耕地掩膜后计算NDWI完成!", 1)
        ret = MODISPRO_Global.ModifiedXMLfile(receiptfile, product_type, "NDWI", "China", "Cropland_Mask", mask_ndwifile)
        if ret != 1:
            MODISPRO_Global.Writelog("回传文件对应修改" + product_type + "产品NDWI数据集China区域Cropland_Mask结果失败!", 0)
        else:
            MODISPRO_Global.Writelog("回传文件对应修改" + product_type + "产品NDWI数据集China区域Cropland_Mask结果完成!", 1)

    # 如果需要执行质量控制
    if QA == "ON":
        MODISPRO_Global.Writelog("开始执行质量控制...", 1)
        QAfile = china_mask_files_dict[QAsuffix]
        china_QA_files_dict = {}
        for i in range(len(suffixs)): china_QA_files_dict[suffixs[i]] = []
        for i in range(len(suffixs)):
            QA_input_file = china_mask_files_dict[suffixs[i]]
            QA_output_file = tempdir + "China_resampled_subset_valid_mask_QA" + datestr + ".tif"
            ret = MODISPRO_Global.QA_MOD09A1(QA_input_file, QAfile, QA_output_file, unvalid_value)
            if ret == 0:
                MODISPRO_Global.Writelog(suffixs[i] + "质量控制失败!", 0)
                continue
            else:
                MODISPRO_Global.Writelog(suffixs[i] + "质量控制完成!", 1)
                china_QA_files_dict[suffixs[i]] = QA_output_file
                if os.path.exists(QA_input_file):
                    os.remove(QA_input_file)
        if os.path.exists(QAfile):
            os.remove(QAfile)

        # 检测B2 B4两个波段是否全部执行质量控制成功,其中一个波段失败即不能计算NDWI
        MODISPRO_Global.Writelog("开始利用质量控制后B2和B4计算NDWI...", 1)
        for i in range(len(suffixs)):
            if len(china_QA_files_dict[suffixs[i]]) == 0:
                china_QA_files_dict.Writelog(suffixs + "波段执行质量控制失败,不能计算NDWI!", 0)
                return 0
        b2file = china_QA_files_dict[MOD09A1_suffixs[0]]
        b4file = china_QA_files_dict[MOD09A1_suffixs[1]]
        ndwifile = outdir + "ChinaQ" + os.path.sep + "32bit_" + datestr + ".tif"
        if not os.path.exists(os.path.dirname(ndwifile)):
            os.makedirs(os.path.dirname(ndwifile))
        ret = MODISPRO_Global.Calculate_NDWI(b2file, b4file, ndwifile, unvalid_value)
        if ret == 0:
            MODISPRO_Global.Writelog("质量控制后计算NDWI失败!", 0)
            return 0
        else:
            MODISPRO_Global.Writelog("质量控制后计算NDWI完成!", 1)
            ret = MODISPRO_Global.ModifiedXMLfile(receiptfile, product_type, "NDWI", "China", "Quality", ndwifile)
            if ret != 1:
                MODISPRO_Global.Writelog("回传文件对应修改" + product_type + "产品NDWI数据集China区域Quality结果失败!", 0)
            else:
                MODISPRO_Global.Writelog("回传文件对应修改" + product_type + "产品NDWI数据集China区域Quality结果完成!", 1)
    else:
        # 删除耕地掩膜后的B2和B4
        if os.path.exists(china_mask_files_dict[MOD09A1_suffixs[0]]):
            os.remove(china_mask_files_dict[MOD09A1_suffixs[0]])
        if os.path.exists(china_mask_files_dict[MOD09A1_suffixs[1]]):
            os.remove(china_mask_files_dict[MOD09A1_suffixs[1]])

    return 1


# 处理MOD13A2\MYD13A2\MOD15A2H\MOD16A2产品
def ExcuteProcess_MOD15A2H_China(inputfiles, product_type, datestr, projection, QA, outdir_dict, receiptfile,
                                 bands, attributes, QAsuffix, resolution, unvalid_value, ranges, tempdir, configpath):

    suffixs = attributes.keys()

    pwdpath = os.path.realpath(__file__)
    # region_dir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + "resource" + os.path.sep + "standard" + os.path.sep
    region_dir = configpath + "standard" + os.path.sep
    if product_type == "MOD13A2" or product_type == "MYD13A2":
        region_dir = region_dir + "1000m" + os.path.sep
    else:
        region_dir = region_dir + "500m" + os.path.sep

    # 筛选中国区HDF数据
    MODISPRO_Global.Writelog("开始筛选中国区HDF文件...", 1)
    hvstrs = ["h23v05", "h23v04", "h24v04", "h24v05", "h25v06", "h25v05", "h25v04", "h25v03", "h26v06", "h26v05",
              "h26v04", "h26v03", "h27v06", "h27v05", "h27v04", "h28v07", "h28v06", "h28v05", "h29v06"]
    infiles = [[]]
    for file_ in inputfiles:
        for hv in hvstrs:
            p = re.compile(r"M" + product_type[1:] + '\.A\d{7}\.' + hv + '.006\.\d{13}\.hdf')
            if re.match(p, os.path.basename(file_)):
                infiles[0].append(file_)
    del inputfiles
    MODISPRO_Global.Writelog("中国区HDF文件筛选完成!", 1)

    # MRT镶嵌投影
    MODISPRO_Global.Writelog("开始对中国区数据利用MRT进行镶嵌投影...", 1)
    res = Customize_MRT.MRTProcess(tempdir, infiles, bands, projection, resolution, suffixs, ranges)
    if res == 0:
        MODISPRO_Global.Writelog('分组数据镶嵌投影失败！', 0)
        return 0
    else:
        MODISPRO_Global.Writelog('分组数据镶嵌投影完成！', 1)
        mrt_processed_files = res
    del res, infiles

    # mrt_processed_files = {'1_km_16_days_NDVI': ["F:\\Pycharm_workspace\\MODISPRO\\temp\\1539896274.24\\resample_000.1_km_16_days_NDVI.tif"],
    #                        '1_km_16_days_VI_Quality': ["F:\\Pycharm_workspace\\MODISPRO\\temp\\1539896274.24\\resample_000.1_km_16_days_VI_Quality.tif"]}

    # 裁剪掩膜-过滤无效值-耕地掩膜
    china_mask_files_dict = {}
    for i in range(len(suffixs)): china_mask_files_dict[suffixs[i]] = []
    base_file = region_dir + "China.tif"
    # if (product_type == "MOD13A2") or (product_type == "MYD13A2"):
    #     mask_file = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + "resource" + os.path.sep + "mask" + os.path.sep + "china2010_arableland_110_1km_4182.tif"
    # else:
    #     mask_file = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + "resource" + os.path.sep + "mask" + os.path.sep + "china2010_arableland_110_500m_4182.tif"
    if (product_type == "MOD13A2") or (product_type == "MYD13A2"):
        mask_file = configpath + "mask" + os.path.sep + "china2010_arableland_110_1km_4182.tif"
    else:
        mask_file = configpath + "mask" + os.path.sep + "china2010_arableland_110_500m_4182.tif"
    if not os.path.exists(base_file):
        MODISPRO_Global.Writelog(base_file + "中国标准输出文件不存在!", 0)
        return 0
    if not os.path.exists(mask_file):
        MODISPRO_Global.Writelog(mask_file + "中国耕地掩膜文件不存在!", 0)
        return 0

    for i in range(len(mrt_processed_files)):
        if len(mrt_processed_files[suffixs[i]]) != 1:
            MODISPRO_Global.Writelog(suffixs[i] + "波段MRT处理异常!", 0)
            continue
        china_resample_file = (mrt_processed_files[suffixs[i]])[0]
        if not os.path.exists(china_resample_file):
            MODISPRO_Global.Writelog(suffixs[i] + "波段MRT处理失败!", 0)
            continue

        # 裁剪掩膜
        MODISPRO_Global.Writelog("开始对" + suffixs[i] + "中国数据进行裁剪标准输出...", 1)
        china_subset_file = tempdir + "China_resampled_subset_" + suffixs[i] + ".tif"
        ret = MODISPRO_Global.Subset_Mask(china_resample_file, base_file, china_subset_file, (attributes[suffixs[i]])['fillvalue'])
        if ret == 0:
            MODISPRO_Global.Writelog(suffixs[i] + "中国数据裁剪标准输出失败!", 0)
            continue
        else:
            MODISPRO_Global.Writelog(suffixs[i] + "中国数据裁剪标准输出完成!", 1)
            if os.path.exists(china_resample_file):
                os.remove(china_resample_file)

        # 过滤无效值
        MODISPRO_Global.Writelog("开始对" + suffixs[i] + "中国标准输出数据进行无效值过滤...", 1)
        if suffixs[i] == QAsuffix:
            if QAsuffix == "1_km_16_days_VI_Quality":
                data_type = gdal.GDT_UInt16
            else:
                data_type = gdal.GDT_Byte
            china_valid_file = tempdir + "China_resampled_subset_valid_" + suffixs[i] + ".tif"
        else:
            data_type = gdal.GDT_Float32
            china_valid_file = outdir_dict[suffixs[i]] + "ChinaO" + os.path.sep + "32bit-" + datestr + ".tif"
            if not os.path.exists(os.path.dirname(china_valid_file)):
                os.makedirs(os.path.dirname(china_valid_file))
        ret = MODISPRO_Global.Filter_unvalid(china_subset_file, attributes[suffixs[i]], china_valid_file, unvalid_value, data_type)
        if ret == 0:
            MODISPRO_Global.Writelog(suffixs[i] + "无效值过滤失败!", 0)
            continue
        else:
            MODISPRO_Global.Writelog(suffixs[i] + "无效值过滤完成!", 1)
            # 质量控制波段无效值过滤结果无须写入回传文件
            if suffixs[i] != QAsuffix:
                ret = MODISPRO_Global.ModifiedXMLfile(receiptfile, product_type, suffixs[i], "China", "Original", china_valid_file)
                if ret != 1:
                    MODISPRO_Global.Writelog("回传文件对应修改" + product_type + "产品" + suffixs[i] + "数据集China区域Original结果失败!", 0)
                else:
                    MODISPRO_Global.Writelog("回传文件对应修改" + product_type + "产品" + suffixs[i] + "数据集China区域Original结果完成!", 1)
            if os.path.exists(china_subset_file):
                os.remove(china_subset_file)

        # 耕地掩膜
        MODISPRO_Global.Writelog("开始对" + suffixs[i] + "中国标准输出数据进行耕地掩膜...", 1)
        if suffixs[i] == QAsuffix:
            if QAsuffix == "1_km_16_days_VI_Quality":
                data_type = gdal.GDT_UInt16
            else:
                data_type = gdal.GDT_Byte
            china_mask_file = tempdir + "China_resampled_subset_valid_mask_" + suffixs[i] + ".tif"
        else:
            data_type = gdal.GDT_Float32
            china_mask_file = outdir_dict[suffixs[i]] + "China" + os.path.sep + "32bit-" + datestr + ".tif"
            if not os.path.exists(os.path.dirname(china_mask_file)):
                os.makedirs(os.path.dirname(china_mask_file))
        ret = MODISPRO_Global.Crop_Mask(china_valid_file, mask_file, china_mask_file, unvalid_value, data_type)
        if ret == 0:
            MODISPRO_Global.Writelog(suffixs[i] + "耕地掩膜失败!", 0)
            continue
        else:
            MODISPRO_Global.Writelog(suffixs[i] + "耕地掩膜完成!", 1)
            # 质量控制波段耕地掩膜结果无须写入回传文件
            if suffixs[i] != QAsuffix:
                ret = MODISPRO_Global.ModifiedXMLfile(receiptfile, product_type, suffixs[i], "China", "Cropland_Mask", china_mask_file)
                if ret != 1:
                    MODISPRO_Global.Writelog("回传文件对应修改" + product_type + "产品" + suffixs[i] + "数据集China区域Cropland_Mask结果失败!", 0)
                else:
                    MODISPRO_Global.Writelog("回传文件对应修改" + product_type + "产品" + suffixs[i] + "数据集China区域Cropland_Mask结果完成!", 1)
            china_mask_files_dict[suffixs[i]] = china_mask_file

    # 如果需要质量控制
    if QA == "ON":
        suffixs.remove(QAsuffix)
        china_mask_files_dict2 = deepcopy(china_mask_files_dict)
        QAfile = china_mask_files_dict2[QAsuffix]
        MODISPRO_Global.Writelog("开始执行质量控制...", 1)
        # 各产品对应的质量控制函数
        QA_dict = {'MOD13A2': MODISPRO_Global.QA_MOD13A2,
                   'MYD13A2': MODISPRO_Global.QA_MOD13A2,
                   'MOD15A2H': MODISPRO_Global.QA_MOD15A2H,
                   'MOD16A2': MODISPRO_Global.QA_MOD16A2}
        # 质量码波段在耕地掩膜部分处理失败,不能执行质量控制
        if not china_mask_files_dict[QAsuffix]:
            MODISPRO_Global.Writelog("质量码波段在耕地掩膜部分处理失败,不能执行质量控制!", 0)
            return 0

        for i in range(len(suffixs)):
            QA_input_file = china_mask_files_dict2[suffixs[i]]
            if not QA_input_file:
                MODISPRO_Global.Writelog(suffixs[i] + "波段在耕地掩膜部分处理失败,不能执行质量控制!", 0)
                continue
            QA_output_file = outdir_dict[suffixs[i]] + "ChinaQ" + os.path.sep + "32bit_" + datestr + ".tif"
            if not os.path.exists(os.path.dirname(QA_output_file)):
                os.makedirs(os.path.dirname(QA_output_file))
            ret = QA_dict[product_type](QA_input_file, QAfile, QA_output_file, unvalid_value)
            if ret == 0:
                MODISPRO_Global.Writelog(suffixs[i] + "波段数据执行质量控制失败!", 0)
                continue
            else:
                MODISPRO_Global.Writelog(suffixs[i] + "波段数据执行质量控制完成!", 1)
                ret = MODISPRO_Global.ModifiedXMLfile(receiptfile, product_type, suffixs[i], "China", "Quality", QA_output_file)
                if ret != 1:
                    MODISPRO_Global.Writelog("回传文件对应修改" + product_type + "产品" + suffixs[i] + "数据集China区域Quality结果失败!", 0)
                else:
                    MODISPRO_Global.Writelog("回传文件对应修改" + product_type + "产品" + suffixs[i] + "数据集China区域Quality结果完成!", 1)

        MODISPRO_Global.Writelog("中国区执行质量控制完成!", 1)

    return 1
