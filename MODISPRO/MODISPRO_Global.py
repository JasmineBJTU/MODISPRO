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
import shutil
import time
import datetime
import xml.dom.minidom as xmldom
import Customize_MRT as mrt
import MODISPRO_China
try:
    from osgeo import gdal
except ImportError:
    import gdal
import numpy as np
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
def Writelog(loginfostr, t):
    if t == 1:
        with open(logfile, 'a+') as logf:
            logf.write(Get_current_time() + ' INFO ' + loginfostr + '\n')
    else:
        with open(logfile, 'a+') as logf:
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

    return res


# 读取系统配置文件
def ReadSysConfig(sysconfigfile, product_type, param_name):

    domxml = xmldom.parse(sysconfigfile)
    rootElement = domxml.documentElement
    propertiesElements = rootElement.getElementsByTagName('Properties')
    if len(propertiesElements) != 1:
        del domxml, rootElement, propertiesElements
        Writelog(sysconfigfile + 'XML文件格式异常!', 0)
        print u'XML文件格式异常!'
        return 0
    for propertiesElement in propertiesElements:
        # Product_Type节点
        productElements = propertiesElement.getElementsByTagName('Product_Type')
        if len(productElements) == 0:
            del domxml, rootElement, propertiesElements
            del productElements
            Writelog(sysconfigfile + 'XML文件格式异常!', 0)
            print u'XML文件格式异常!'
            return 0
        for productElement in productElements:
            name = productElement.getAttribute('name')
            if name == product_type:
                Info_Elements = productElement.getElementsByTagName(param_name)
                if len(Info_Elements) != 1:
                    del domxml, rootElement, propertiesElements
                    Writelog(sysconfigfile + product_type + param_name + '节点格式异常!', 0)
                    print product_type + u"'Bands节点格式异常!'"
                    return 0
                if param_name != "Attributes":
                    value = Info_Elements[0].getAttribute('value')
                    del domxml, rootElement, propertiesElements, Info_Elements
                    return value
                else:
                    elements = Info_Elements[0].getElementsByTagName('Element')
                    if len(elements) == 0:
                        del domxml, rootElement, propertiesElements
                        Writelog(sysconfigfile + product_type + param_name + 'Attributes' + 'Element节点格式异常!', 0)
                        print product_type + 'Attributes' + u"'Element节点格式异常!'"
                        return 0
                    value = {}
                    for element in elements:
                        name = str(element.getAttribute('name'))
                        validrange = element.getAttribute('validranges')
                        fillvalue = element.getAttribute('fillvalue')
                        scale_factor = element.getAttribute('scale_factor')
                        value[name] = {}
                        (value[name])['validranges'] = map(long, validrange.split(','))
                        (value[name])['fillvalue'] = long(fillvalue)
                        (value[name])['scale_factor'] = float(scale_factor)

                    del domxml, rootElement, propertiesElements, Info_Elements
                    return value


# 预设回传文件
def PreReceiptXML(xmlfile, QA, product_type, suffixs, regions):

    if "China" in regions:
        regions.remove("China")

    if not os.path.exists(os.path.dirname(xmlfile)):
        os.makedirs(os.path.dirname(xmlfile))

    doc = xmldom.Document()
    root_node = doc.createElement("Configuration")
    doc.appendChild(root_node)
    property_node = doc.createElement("Properties")
    root_node.appendChild(property_node)

    product_node = doc.createElement("Product_Type")
    property_node.appendChild(product_node)
    product_node.setAttribute("name", product_type)

    if QA == "ON":
        for suffix in suffixs:
            dataset_node = doc.createElement("Dataset")
            product_node.appendChild(dataset_node)
            dataset_node.setAttribute("name", suffix)

            # 全球与中国节点与其它研究区节点结构不同
            region_node = doc.createElement("Region")
            dataset_node.appendChild(region_node)
            region_node.setAttribute("name", "Global")
            original_node = doc.createElement("Original")
            region_node.appendChild(original_node)
            original_node.setAttribute("path", "")
            original_node.setAttribute("status", "0")
            cropland_mask_node = doc.createElement("Cropland_Mask")
            region_node.appendChild(cropland_mask_node)
            cropland_mask_node.setAttribute("path", "")
            cropland_mask_node.setAttribute("status", "0")
            quality_node = doc.createElement("Quality")
            region_node.appendChild(quality_node)
            quality_node.setAttribute("path", "")
            quality_node.setAttribute("status", "0")

            region_node = doc.createElement("Region")
            dataset_node.appendChild(region_node)
            region_node.setAttribute("name", "China")
            original_node = doc.createElement("Original")
            region_node.appendChild(original_node)
            original_node.setAttribute("path", "")
            original_node.setAttribute("status", "0")
            cropland_mask_node = doc.createElement("Cropland_Mask")
            region_node.appendChild(cropland_mask_node)
            cropland_mask_node.setAttribute("path", "")
            cropland_mask_node.setAttribute("status", "0")
            quality_node = doc.createElement("Quality")
            region_node.appendChild(quality_node)
            quality_node.setAttribute("path", "")
            quality_node.setAttribute("status", "0")

            for region in regions:
                region_node = doc.createElement("Region")
                dataset_node.appendChild(region_node)
                region_node.setAttribute("name", region)

                cropland_mask_node = doc.createElement("Cropland_Mask")
                region_node.appendChild(cropland_mask_node)
                cropland_mask_node.setAttribute("path", "")
                cropland_mask_node.setAttribute("status", "0")

                quality_node = doc.createElement("Quality")
                region_node.appendChild(quality_node)
                quality_node.setAttribute("path", "")
                quality_node.setAttribute("status", "0")

    elif QA == "OFF":
        for suffix in suffixs:
            dataset_node = doc.createElement("Dataset")
            product_node.appendChild(dataset_node)
            dataset_node.setAttribute("name", suffix)

            # 全球与中国节点与其它研究区节点结构不同
            region_node = doc.createElement("Region")
            dataset_node.appendChild(region_node)
            region_node.setAttribute("name", "Global")
            original_node = doc.createElement("Original")
            region_node.appendChild(original_node)
            original_node.setAttribute("path", "")
            original_node.setAttribute("status", "0")
            cropland_mask_node = doc.createElement("Cropland_Mask")
            region_node.appendChild(cropland_mask_node)
            cropland_mask_node.setAttribute("path", "")
            cropland_mask_node.setAttribute("status", "0")

            region_node = doc.createElement("Region")
            dataset_node.appendChild(region_node)
            region_node.setAttribute("name", "China")
            original_node = doc.createElement("Original")
            region_node.appendChild(original_node)
            original_node.setAttribute("path", "")
            original_node.setAttribute("status", "0")
            cropland_mask_node = doc.createElement("Cropland_Mask")
            region_node.appendChild(cropland_mask_node)
            cropland_mask_node.setAttribute("path", "")
            cropland_mask_node.setAttribute("status", "0")

            for region in regions:
                region_node = doc.createElement("Region")
                dataset_node.appendChild(region_node)
                region_node.setAttribute("name", region)

                cropland_mask_node = doc.createElement("Cropland_Mask")
                region_node.appendChild(cropland_mask_node)
                cropland_mask_node.setAttribute("path", "")
                cropland_mask_node.setAttribute("status", "0")

    with open(xmlfile, "w") as f:
        f.write(doc.toprettyxml(indent='\t', encoding="UTF-8"))

    del doc, root_node, property_node, product_node
    del dataset_node, region_node, original_node, cropland_mask_node
    if QA == "ON":
        del quality_node

    if os.path.exists(xmlfile):
        return 1
    else:
        return 0


# 修改预设回传文件
def ModifiedXMLfile(xmlfile, product_type, suffix, region, tag, path):

    if not os.path.exists(xmlfile):
        # Writelog(xmlfile + "文件不存在!", 0)
        print xmlfile + u'"文件不存在!"'
        return 0

    domxml = xmldom.parse(xmlfile)
    root_Element = domxml.documentElement
    property_Elements = root_Element.getElementsByTagName("Properties")
    if len(property_Elements) != 1:
        del domxml, root_Element, property_Elements
        # Writelog("XML文件格式异常!", 0)
        print u"XML文件格式异常!"
        return 0
    property_Element = property_Elements[0]

    product_type_Elements = property_Element.getElementsByTagName("Product_Type")
    if len(product_type_Elements) != 1:
        del domxml, root_Element, property_Elements, property_Element, product_type_Elements
        # Writelog("XML文件格式异常!", 0)
        print u"XML文件格式异常!"
        return 0
    product_type_Element = product_type_Elements[0]
    if product_type_Element.getAttribute("name") != product_type:
        # Writelog(xmlfile + "文件中不存在" + product_type + "数据产品节点!", 0)
        print xmlfile + u'"文件中不存在"' + product_type + u'"数据产品节点!"'
        return 0

    dataset_Elements = product_type_Element.getElementsByTagName("Dataset")
    dataset_Element = None
    for dataset_Element_ in dataset_Elements:
        if dataset_Element_.getAttribute("name") == suffix:
            dataset_Element = dataset_Element_
            break
    if dataset_Element == None:
        # Writelog(xmlfile + "文件中不存在" + suffix + "数据集节点!", 0)
        print xmlfile + u'"文件中不存在"' + suffix + u'"数据集节点!"'
        return 0

    region_Elements = dataset_Element.getElementsByTagName("Region")
    region_Element = None
    for region_Element_ in region_Elements:
        if region_Element_.getAttribute("name") == region:
            region_Element = region_Element_
            break
    if region_Element == None:
        # Writelog(xmlfile + "文件中不存在" + region + "区域节点!", 0)
        print xmlfile + u'"文件中不存在"' + region + u'"区域节点!"'
        return 0

    tag_Elements = region_Element.getElementsByTagName(tag)
    if len(tag_Elements) != 1:
        del domxml, root_Element, property_Elements, property_Element, product_type_Elements, product_type_Element
        del dataset_Elements, dataset_Element, region_Elements, tag_Elements
        # Writelog("XML文件格式异常!", 0)
        print u"XML文件格式异常!"
        return 0
    tag_Element = tag_Elements[0]

    tag_Element.setAttribute("path", path)
    tag_Element.setAttribute("status", "1")
    pass

    with open(xmlfile, "w") as f:
        f.write(domxml.toxml("UTF-8"))

    del domxml, root_Element, property_Elements, property_Element, product_type_Elements, product_type_Element
    del dataset_Elements, dataset_Element, region_Elements, tag_Elements, tag_Element

    return 1


# 利用GDAL镶嵌各分块投影数据
def GDAL_Mosaic(resample_file, group_resample_files, fill_value):
    if fill_value == '':
        warp_parameters = gdal.WarpOptions(format='GTiff', resampleAlg=gdal.GRIORA_NearestNeighbour,
                                           multithread=True)
    else:
        warp_parameters = gdal.WarpOptions(format='GTiff', resampleAlg=gdal.GRIORA_NearestNeighbour,
                                           multithread=True, srcNodata=fill_value)  # , dstNodata=fillvalue[0]

    gdal.Warp(resample_file, group_resample_files, options=warp_parameters)

    for tfile in group_resample_files:
        if os.path.exists(tfile):
            os.remove(tfile)

    if os.path.exists(resample_file):
        return 1
    else:
        return 0


# 分区裁剪
def Subset_Mask(infile, roifile, outfile, unvalid_value):

    # 读取待裁剪数据左上角坐标及分辨率
    indataset = gdal.Open(infile)
    in_mapinfo = indataset.GetGeoTransform()
    in_ul_lon = in_mapinfo[0]
    in_ul_lat = in_mapinfo[3]
    in_x_pixel = in_mapinfo[1]
    in_y_pixel = in_mapinfo[5]
    in_cols = indataset.RasterXSize
    in_rows = indataset.RasterYSize

    # 读取ROI数据左上角坐标及行列号大小
    roidataset = gdal.Open(roifile)
    roi_mapinfo = roidataset.GetGeoTransform()
    roi_ul_lon = roi_mapinfo[0]
    roi_ul_lat = roi_mapinfo[3]
    roi_x_pixel = roi_mapinfo[1]
    roi_y_pixel = roi_mapinfo[5]
    roi_cols = roidataset.RasterXSize
    roi_rows = roidataset.RasterYSize

    # 待裁剪数据与ROI分辨率不一致时不执行裁剪
    format_ = "%0.8f"
    if ((format_ % in_x_pixel) != (format_ % roi_x_pixel)) or ((format_ % in_y_pixel) != (format_ % roi_y_pixel)):
        return 0

    # 计算起始行列号
    start_x = int((roi_ul_lon - in_ul_lon) / in_x_pixel)
    if start_x < 0: start_x = 0
    start_y = int((roi_ul_lat - in_ul_lat) / in_y_pixel)
    if start_y < 0: start_y = 0
    inband = indataset.GetRasterBand(1)
    roiband = roidataset.GetRasterBand(1)

    # 判断待裁剪掩膜文件的数据类型
    datatype_names_dict = {"uint8": gdal.GDT_Byte,
                           "float": gdal.GDT_Float32,
                           "float16": gdal.GDT_Float32,
                           "float32": gdal.GDT_Float32,
                           "float64": gdal.GDT_Float64,
                           "int8": gdal.GDT_Int16,
                           "int16": gdal.GDT_Int16,
                           "int32": gdal.GDT_Int32,
                           "uint16": gdal.GDT_UInt16,
                           "uint32": gdal.GDT_UInt32}
    example_data = inband.ReadAsArray(0, 0, 1, 1)
    data_type_name = example_data.dtype.name
    if not datatype_names_dict.get(data_type_name):
        data_type = gdal.GDT_Float32
    else:
        data_type = datatype_names_dict.get(data_type_name)

    # 输出结果
    driver = gdal.GetDriverByName("GTiff")
    outdataset = driver.Create(outfile, roi_cols, roi_rows, 1, data_type)
    outdataset.SetGeoTransform(roidataset.GetGeoTransform())
    outdataset.SetProjection(roidataset.GetProjectionRef())
    outband = outdataset.GetRasterBand(1)
    outband.SetNoDataValue(unvalid_value)

    if (roi_cols > in_cols/5) and (roi_rows > in_rows/5):
        row_step = roi_rows/40
        for i in range(0, roi_rows, row_step):
            if i+row_step < roi_rows:
                numrows = row_step
            else:
                numrows = roi_rows - i
            # tempindata = inband.ReadAsArray(0, i, roi_cols, numrows)
            temproidata = roiband.ReadAsArray(0, i, roi_cols, numrows)
            condition_1 = np.logical_and((temproidata == 255), (temproidata == 255))
            index_1 = np.where(condition_1)
            temproidata = None
            tempindata = inband.ReadAsArray(start_x, start_y, roi_cols, numrows)
            tempindata[index_1] = unvalid_value
            outband.WriteArray(tempindata, 0, i)
            tempindata = None
            start_y += row_step
    else:
        roi_data = roiband.ReadAsArray(0, 0, roi_cols, roi_rows)
        condition_1 = np.logical_and((roi_data == 255), (roi_data == 255))
        index_1 = np.where(condition_1)
        roi_data = None
        tempdata = inband.ReadAsArray(start_x, start_y, roi_cols, roi_rows)
        tempdata[index_1] = unvalid_value
        outband.WriteArray(tempdata)
        tempdata = None

    del indataset, inband, roidataset, outdataset, outband, driver, condition_1, index_1

    return 1


# 过滤无效值
def Filter_unvalid(infile, attributes, outfile, unvalid_value, data_type):

    valid_range = attributes['validranges']
    fill_value = attributes['fillvalue']
    scale_factor = attributes['scale_factor']

    indataset = gdal.Open(infile)
    if indataset is None:
        return 0
    driver = indataset.GetDriver()

    # 读取原始数据
    inband = indataset.GetRasterBand(1)
    cols = indataset.RasterXSize
    rows = indataset.RasterYSize

    # 输出数据文件
    outdataset = driver.Create(outfile, indataset.RasterXSize, indataset.RasterYSize, 1, data_type)
    outdataset.SetGeoTransform(indataset.GetGeoTransform())
    outdataset.SetProjection(indataset.GetProjectionRef())
    outband = outdataset.GetRasterBand(1)
    outband.SetNoDataValue(unvalid_value)

    rowstep = rows / 40
    for i in range(0, rows, rowstep):
        if i + rowstep < rows:
            numrows = rowstep
        else:
            numrows = rows - i
        tempdata = inband.ReadAsArray(0, i, cols, numrows)

        # 获取原始数据无效值
        condition_1 = np.logical_or(tempdata < valid_range[0], tempdata > valid_range[1])
        index_1 = np.where(condition_1)
        condition_2 = np.logical_and(tempdata == fill_value, tempdata == fill_value)
        index_2 = np.where(condition_2)

        tempdata = tempdata * scale_factor

        # 剔除无效值
        tempdata[index_1] = unvalid_value
        tempdata[index_2] = unvalid_value
        del condition_1, condition_2, index_1, index_2
        outband.WriteArray(tempdata, 0, i)
        tempdata = None

    del indataset, inband, outband, outdataset

    # if os.path.exists(tfile):
    #     os.remove(tfile)

    if os.path.exists(outfile):
        return 1
    else:
        return 0


# 耕地掩膜
def Crop_Mask(infile, mask_file, outfile, unvalid_value, data_type):

    indataset = gdal.Open(infile)
    if indataset is None:
        return 0
    driver = indataset.GetDriver()

    maskdataset = gdal.Open(mask_file)
    if maskdataset is None:
        return 0

    inband = indataset.GetRasterBand(1)
    cols = indataset.RasterXSize
    rows = indataset.RasterYSize
    maskband = maskdataset.GetRasterBand(1)

    # 输出数据文件
    outdataset = driver.Create(outfile, indataset.RasterXSize, indataset.RasterYSize, 1, data_type)
    outdataset.SetGeoTransform(indataset.GetGeoTransform())
    outdataset.SetProjection(indataset.GetProjectionRef())
    outband = outdataset.GetRasterBand(1)
    outband.SetNoDataValue(unvalid_value)

    rowstep = rows / 40
    for i in range(0, rows, rowstep):
        if i + rowstep < rows:
            numrows = rowstep
        else:
            numrows = rows - i
        tempdata_ = inband.ReadAsArray(0, i, cols, numrows)
        tempdata = np.zeros(tempdata_.shape) + unvalid_value
        maskdata = maskband.ReadAsArray(0, i, cols, numrows)

        condition = np.logical_and((maskdata == 1), (maskdata == 1))
        index = np.where(condition)
        tempdata[index] = tempdata_[index]

        outband.WriteArray(tempdata, 0, i)
        tempdata = None
        tempdata_ = None
        maskdata = None

    del inband, indataset, maskband, maskdataset, outband, outdataset
    return 1


def Calculate_NDWI(b2file, b4file, ndwifile, unvalid_value):

    b2_dataset = gdal.Open(b2file)
    if b2_dataset == None:
        return 0
    b2_cols = b2_dataset.RasterXSize
    b2_rows = b2_dataset.RasterYSize
    b2_band = b2_dataset.GetRasterBand(1)

    b4_dataset = gdal.Open(b4file)
    if b4_dataset == None:
        return 0
    b4_cols = b4_dataset.RasterXSize
    b4_rows = b4_dataset.RasterYSize
    b4_band = b4_dataset.GetRasterBand(1)

    if (b2_cols != b4_cols) or (b2_rows != b4_rows):
        return 0

    # 输出数据文件
    driver = b2_dataset.GetDriver()
    outdataset = driver.Create(ndwifile, b2_dataset.RasterXSize, b2_dataset.RasterYSize, 1, gdal.GDT_Float32)
    outdataset.SetGeoTransform(b2_dataset.GetGeoTransform())
    outdataset.SetProjection(b2_dataset.GetProjectionRef())
    outband = outdataset.GetRasterBand(1)
    outband.SetNoDataValue(unvalid_value)

    # 当图像行列号大小大于10000*10000时分块计算,否则整体计算
    if (b2_cols > 10000) and (b2_rows > 10000):
        rowstep = b2_rows / 40
        for i in range(0, b2_rows, rowstep):
            if i + rowstep < b2_rows:
                numrows = rowstep
            else:
                numrows = b2_rows - i
            b2_data = b2_band.ReadAsArray(0, i, b2_cols, numrows)
            condition_2 = np.logical_and((b2_data == unvalid_value), (b2_data == unvalid_value))
            index_2 = np.where(condition_2)
            b4_data = b4_band.ReadAsArray(0, i, b2_cols, numrows)
            condition_4 = np.logical_and((b4_data == unvalid_value), (b4_data == unvalid_value))
            index_4 = np.where(condition_4)
            condition_0 = np.logical_and(((b2_data + b4_data) == 0.0), ((b2_data + b4_data) == 0.0))
            index_0 = np.where(condition_0)
            b2_data[index_0] = 1
            b4_data[index_0] = 1
            ndwi = (b4_data - b2_data)/(b2_data + b4_data)
            ndwi[index_2] = unvalid_value
            ndwi[index_4] = unvalid_value
            ndwi[index_0] = unvalid_value
            ndwi_ = np.nan_to_num(ndwi)
            outband.WriteArray(ndwi_, 0, i)
            b2_data = None
            b4_data = None
            ndwi = None
            ndwi_ = None
    else:
        b2_data = b2_band.ReadAsArray(0, 0, b2_cols, b2_rows)
        condition_2 = np.logical_and((b2_data == unvalid_value), (b2_data == unvalid_value))
        index_2 = np.where(condition_2)
        b4_data = b4_band.ReadAsArray(0, 0, b4_cols, b4_rows)
        condition_4 = np.logical_and((b4_data == unvalid_value), (b4_data == unvalid_value))
        index_4 = np.where(condition_4)
        condition_0 = np.logical_and(((b2_data + b4_data) == 0.0), ((b2_data + b4_data) == 0.0))
        index_0 = np.where(condition_0)
        b2_data[index_0] = 1
        b4_data[index_0] = 1
        ndwi = (b4_data - b2_data)/(b2_data + b4_data)
        ndwi[index_2] = unvalid_value
        ndwi[index_4] = unvalid_value
        ndwi[index_0] = unvalid_value
        ndwi_ = np.nan_to_num(ndwi)
        outband.WriteArray(ndwi)
        b2_data = None
        b4_data = None
        ndwi = None
        ndwi_ = None

    del b2_dataset, b2_band, condition_2, index_2
    del b4_dataset, b4_band, condition_4, index_4
    del outdataset, outband, condition_0, index_0
    return 1


def QA_MOD13A2(QA_input_file, QAfile, QA_output_file, unvalid_value):

    indataset = gdal.Open(QA_input_file)
    if indataset is None:
        Writelog('打开' + QA_input_file + '失败!', 0)
        return 0
    driver = indataset.GetDriver()

    qadataset = gdal.Open(QAfile)
    if qadataset is None:
        Writelog('打开' + QAfile + '失败!', 0)
        return 0

    inband = indataset.GetRasterBand(1)
    cols = indataset.RasterXSize
    rows = indataset.RasterYSize
    qaband = qadataset.GetRasterBand(1)

    # 输出数据文件
    outdataset = driver.Create(QA_output_file, indataset.RasterXSize, indataset.RasterYSize, 1, gdal.GDT_Float32)
    outdataset.SetGeoTransform(indataset.GetGeoTransform())
    outdataset.SetProjection(indataset.GetProjectionRef())
    outband = outdataset.GetRasterBand(1)
    outband.SetNoDataValue(unvalid_value)

    rowstep = rows / 40
    for i in range(0, rows, rowstep):
        if i + rowstep < rows:
            numrows = rowstep
        else:
            numrows = rows - i
        tempdata = inband.ReadAsArray(0, i, cols, numrows)
        qualdata = qaband.ReadAsArray(0, i, cols, numrows)

        # 质量控制码中由左至右第11-14位是植被指数可用性字段,筛选0000,0100,1000,1100四种等级
        qualdata_1 = (qualdata >> 2) - (((qualdata >> 2) >> 4) << 4)
        qualdata_2 = qualdata_1 % 4
        condition = np.logical_not(qualdata_2 == 0)
        index = np.where(condition)
        tempdata[index] = unvalid_value

        outband.WriteArray(tempdata, 0, i)
        tempdata = None
        tempdata_ = None
        qualdata = None

    del qualdata, qualdata_1, qualdata_2, condition, index
    del inband, indataset, qaband, qadataset, outband, outdataset, driver

    if os.path.exists(QA_output_file):
        return 1
    else:
        return 0


def QA_MOD09A1(QA_input_file, QAfile, QA_output_file, attributes):

    return 0


def QA_MOD15A2H(QA_input_file, QAfile, QA_output_file, attributes):

    return 0


def QA_MOD16A2(QA_input_file, QAfile, QA_output_file, attributes):

    return 0


# 处理MOD09A1产品
def ExcuteProcess_MOD09A1(inputfiles, product_type, datestr, projection, QA, outdir, receiptfile,
                          bands, attributes, QAsuffix, resolution, unvalid_value, regions, ranges, configpath):

    suffixs = attributes.keys()
    regions2 = regions[:]
    if "China" in regions:
        regions.remove("China")
    MOD09A1_suffixs = ["sur_refl_b02", "sur_refl_b04"]

    global_outdir = outdir + "Global" + os.path.sep
    if not os.path.exists(global_outdir):
        os.makedirs(global_outdir)
    globalO_outdir = outdir + "GlobalO" + os.path.sep
    if not os.path.exists(globalO_outdir):
        os.makedirs(globalO_outdir)

    pwdpath = os.path.realpath(__file__)
    # region_dir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + "resource" + os.path.sep + "standard" + os.path.sep
    # region_dir = region_dir + "500m" + os.path.sep
    region_dir = configpath + "standard" + os.path.sep + "500m" + os.path.sep

    # 全球HDF数据分组
    Writelog('开始对全球HDF数据分组...', 1)
    res = mrt.GetSlice_HDF(inputfiles, product_type)
    if res == 0:
        Writelog('全球HDF数据分组失败!', 0)
        return 0
    else:
        Writelog('全球HDF数据分组完成!', 1)
        groups_files = res
    del res, inputfiles

    # MRT处理镶嵌投影各分组HDF数据
    Writelog('开始对分组数据镶嵌投影...', 1)
    res = mrt.MRTProcess(tempdir, groups_files, bands, projection, resolution, suffixs, ranges)
    if res == 0:
        Writelog('分组数据镶嵌投影失败！', 0)
        return 0
    else:
        Writelog('分组数据镶嵌投影完成！', 1)
        mrt_processed_files = res
    del res, groups_files

    # 各分组数据全球拼接-标准输出-无效值过滤-耕地掩膜(包含质量码波段)
    global_valid_files_dict = {}
    for i in range(len(suffixs)): global_valid_files_dict[suffixs[i]] = []
    global_mask_files_dict = {}
    for i in range(len(suffixs)): global_mask_files_dict[suffixs[i]] = []
    base_file = region_dir + "Global.tif"
    # mask_file = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + "resource" + os.path.sep + "mask" + os.path.sep + "global_cropland_mask_500m_standard.tif"
    mask_file = configpath + "mask" + os.path.sep + "global_cropland_mask_500m_standard.tif"
    if not os.path.exists(base_file):
        Writelog(base_file + "全球标准输出文件不存在!", 0)
        return 0
    if not os.path.exists(mask_file):
        Writelog(mask_file + "全球耕地掩膜文件不存在!", 0)
        return 0
    for i in range(len(suffixs)):
        Writelog("开始拼接" + suffixs[i] + "全球数据...", 1)
        temp_files = mrt_processed_files[suffixs[i]]
        global_resample_file = tempdir + "global_resampled_" + suffixs[i] + ".tif"
        fill_value = (attributes[suffixs[i]])['fillvalue']
        ret = GDAL_Mosaic(global_resample_file, temp_files, fill_value)
        if ret == 0:
            Writelog(suffixs[i] + "全球数据拼接失败!", 0)
            continue
        else:
            Writelog(suffixs[i] + "全球数据拼接完成!", 1)

        global_resample_file_ = tempdir + "global_resampled_" + suffixs[i] + "_.tif"
        gdal.Translate(global_resample_file_, global_resample_file, projWin=ranges)
        if os.path.exists(global_resample_file_) and os.path.exists(global_resample_file):
            os.remove(global_resample_file)

        Writelog("开始对" + suffixs[i] + "全球数据进行裁剪标准输出...", 1)
        global_subset_file = tempdir + "global_resampled_subset_" + suffixs[i] + ".tif"
        ret = Subset_Mask(global_resample_file_, base_file, global_subset_file, (attributes[suffixs[i]])['fillvalue'])
        if ret == 0:
            Writelog(suffixs[i] + "全球数据裁剪标准输出失败!", 0)
            continue
        else:
            Writelog(suffixs[i] + "全球数据裁剪标准输出完成!", 1)
            if os.path.exists(global_resample_file_):
                os.remove(global_resample_file_)

        Writelog("开始对" + suffixs[i] + "全球标准输出数据进行无效值过滤...", 1)
        if QAsuffix == "sur_refl_qc_500m":
            data_type = gdal.GDT_UInt32
        else:
            data_type = gdal.GDT_Float32
        global_valid_file = tempdir + "global_resampled_subset_valid_" + suffixs[i] + ".tif"
        ret = Filter_unvalid(global_subset_file, attributes[suffixs[i]], global_valid_file, unvalid_value, data_type)
        if ret == 0:
            Writelog(suffixs[i] + "无效值过滤失败!", 0)
            continue
        else:
            Writelog(suffixs[i] + "无效值过滤完成!", 1)
            global_valid_files_dict[suffixs[i]] = global_valid_file
            if os.path.exists(global_subset_file):
                os.remove(global_subset_file)

        Writelog("开始对" + suffixs[i] + "全球标准输出数据进行耕地掩膜...", 1)
        if QAsuffix == "sur_refl_qc_500m":
            data_type = gdal.GDT_UInt32
        else:
            data_type = gdal.GDT_Float32
        global_mask_file = tempdir + "global_resampled_subset_valid_mask_" + suffixs[i] + ".tif"
        ret = Crop_Mask(global_valid_file, mask_file, global_mask_file, unvalid_value, data_type)
        if ret == 0:
            Writelog(suffixs[i] + "耕地掩膜失败!", 0)
            continue
        else:
            Writelog(suffixs[i] + "耕地掩膜完成!", 1)
            global_mask_files_dict[suffixs[i]] = global_mask_file

    if QA == "ON":
        suffixs.remove(QAsuffix)

    # global_valid_files_dict = {'sur_refl_b02': 'F:\\Pycharm_workspace\\MODISPRO\\temp\\1539949235.51\\global_resampled_subset_valid_sur_refl_b02.tif',
    #                            'sur_refl_b07': 'F:\\Pycharm_workspace\\MODISPRO\\temp\\1539949235.51\\global_resampled_subset_valid_sur_refl_b07.tif'}
    # global_mask_files_dict = {'sur_refl_b02': 'F:\\Pycharm_workspace\\MODISPRO\\temp\\1539949235.51\\global_resampled_subset_valid_mask_sur_refl_b02.tif',
    #                           'sur_refl_b07': 'F:\\Pycharm_workspace\\MODISPRO\\temp\\1539949235.51\\global_resampled_subset_valid_mask_sur_refl_b07.tif'}

    # 利用无效值过滤的结果计算NDWI
    Writelog("开始利用无效值过滤后的B2和B4计算NDWI...", 1)
    for i in range(len(suffixs)):
        if not os.path.exists(global_valid_files_dict[suffixs[i]]):
            Writelog(suffixs[i] + "波段执行无效值过滤失败,不能计算NDWI!", 0)
            return 0
    b2file = global_valid_files_dict[MOD09A1_suffixs[0]]
    b4file = global_valid_files_dict[MOD09A1_suffixs[1]]
    valid_ndwifile = outdir + "GlobalO" + os.path.sep + "32bit_" + datestr + ".tif"
    if not os.path.exists(os.path.dirname(valid_ndwifile)):
        os.makedirs(os.path.dirname(valid_ndwifile))
    ret = Calculate_NDWI(b2file, b4file, valid_ndwifile, unvalid_value)
    if ret != 1:
        Writelog("无效值过滤后B2和B4计算NDWI失败!", 0)
    else:
        Writelog("无效值过滤后B2和B4计算NDWI完成!", 1)

        ret = ModifiedXMLfile(receiptfile, product_type, "NDWI", "Global", "Original", valid_ndwifile)
        if ret != 1:
            Writelog("回传文件对应修改" + product_type + "产品NDWI数据Global区域Original结果失败!", 0)
        else:
            Writelog("回传文件对应修改" + product_type + "产品NDWI数据Global区域Original结果完成!", 1)

        # 删除无效值过滤后b2file,b4file
        if os.path.exists(global_valid_files_dict[MOD09A1_suffixs[0]]):
            os.remove(global_valid_files_dict[MOD09A1_suffixs[0]])
        if os.path.exists(global_valid_files_dict[MOD09A1_suffixs[1]]):
            os.remove(global_valid_files_dict[MOD09A1_suffixs[1]])
        del global_valid_files_dict

    # 利用耕地掩膜的结果计算NDWI并进行分区裁剪
    Writelog("开始利用耕地掩膜后的B2和B4计算NDWI...", 1)
    for i in range(len(suffixs)):
        if not os.path.exists(global_mask_files_dict[suffixs[i]]):
            Writelog(suffixs[i] + "波段执行耕地掩膜失败,不能计算NDWI!", 0)
            return 0
    b2file = global_mask_files_dict[MOD09A1_suffixs[0]]
    b4file = global_mask_files_dict[MOD09A1_suffixs[1]]
    mask_ndwifile = outdir + "Global" + os.path.sep + "32bit_" + datestr + ".tif"
    if not os.path.exists(os.path.dirname(mask_ndwifile)):
        os.makedirs(os.path.dirname(mask_ndwifile))
    ret = Calculate_NDWI(b2file, b4file, mask_ndwifile, unvalid_value)
    if ret != 1:
        Writelog("耕地掩膜后B2和B4计算NDWI失败!", 0)
    else:
        Writelog("耕地掩膜后B2和B4计算NDWI完成!", 1)

        ret = ModifiedXMLfile(receiptfile, product_type, "NDWI", "Global", "Cropland_Mask", mask_ndwifile)
        if ret != 1:
            Writelog("回传文件对应修改" + product_type + "产品NDWI数据全球区域Cropland_Mask结果失败!", 0)
        else:
            Writelog("回传文件对应修改" + product_type + "产品NDWI数据全球区域Cropland_Mask结果完成!", 1)

        # 质量控制前分区裁剪
        Writelog("开始执行质量控制前分区裁剪...", 1)
        for region in regions:
            region_base_file = region_dir + region + ".tif"
            if not os.path.exists(region_base_file):
                Writelog(region + "研究区标准输出文件不存在,分区裁剪失败!", 0)
                continue
            region_file = outdir + region + os.path.sep + "32bit_" + datestr + ".tif"
            if not os.path.exists(os.path.dirname(region_file)):
                os.makedirs(os.path.dirname(region_file))
            ret = Subset_Mask(mask_ndwifile, region_base_file, region_file, unvalid_value)
            if ret == 0:
                Writelog(region + "分区裁剪失败!", 0)
                continue
            else:
                ret = ModifiedXMLfile(receiptfile, product_type, "NDWI", region, "Cropland_Mask", region_file)
                if ret != 1:
                    Writelog("回传文件对应修改" + product_type + "产品NDWI数据" + region + "区域Cropland_Mask结果失败!", 0)
                else:
                    Writelog("回传文件对应修改" + product_type + "产品NDWI数据" + region + "区域Cropland_Mask结果完成!", 1)
        Writelog("各研究区质量控制前的分区裁剪操作全部完成!", 1)

    # 如果需要执行质量控制
    if QA == "ON":
        Writelog("开始执行质量控制...", 1)
        QAfile = global_mask_files_dict[QAsuffix]
        if not os.path.exists(QAfile):
            Writelog(QAsuffix + "质量码波段在耕地掩膜部分处理失败,不能执行质量控制!", 0)
            return 0
        global_QA_files_dict = {}
        for i in range(len(suffixs)): global_QA_files_dict[suffixs[i]] = []
        for i in range(len(suffixs)):
            # 利用耕地掩膜结果计算NDWI时检测过global_mask_files_dict,此处不必再检测
            QA_input_file = global_mask_files_dict[suffixs[i]]
            QA_output_file = tempdir + "global_resampled_subset_valid_mask_QA" + datestr + ".tif"
            ret = QA_MOD09A1(QA_input_file, QAfile, QA_output_file, unvalid_value)
            if ret == 0:
                Writelog(suffixs[i] + "质量控制失败!", 0)
                continue
            else:
                Writelog(suffixs[i] + "质量控制完成!", 1)
                if os.path.exists(QA_input_file):
                    os.remove(QA_input_file)
                global_QA_files_dict[suffixs[i]] = QA_output_file
        if os.path.exists(QAfile):
            os.remove(QAfile)

        # 检测B2 B4两个波段是否全部执行质量控制成功,其中一个波段失败即不能计算NDWI
        Writelog("开始利用质量控制后B2和B4计算NDWI...", 1)
        for i in range(len(suffixs)):
            if not os.path.exists(global_QA_files_dict[suffixs[i]]):
                Writelog(suffixs + "波段执行质量控制失败,不能计算NDWI!", 0)
                return 0
        b2file = global_QA_files_dict[MOD09A1_suffixs[0]]
        b4file = global_QA_files_dict[MOD09A1_suffixs[1]]
        ndwifile = outdir + "GlobalQ" + os.path.sep + "32bit_" + datestr + ".tif"
        if not os.path.exists(os.path.dirname(ndwifile)):
            os.makedirs(os.path.dirname(ndwifile))
        ret = Calculate_NDWI(b2file, b4file, ndwifile, unvalid_value)
        if ret != 1:
            Writelog("质量控制后计算NDWI失败!", 0)
            return 0
        else:
            Writelog("质量控制后计算NDWI完成!", 1)

            ret = ModifiedXMLfile(receiptfile, product_type, "NDWI", "Global", "Quality", mask_ndwifile)
            if ret != 1:
                Writelog("回传文件对应修改" + product_type + "产品NDWI数据全球区域Quality结果失败!", 0)
            else:
                Writelog("回传文件对应修改" + product_type + "产品NDWI数据全球区域Quality结果完成!", 1)

            # 质量控制后分区裁剪
            Writelog("开始执行质量控制后分区裁剪...", 1)
            for region in regions:
                region_base_file = region_dir + region + ".tif"
                if not os.path.exists(region_base_file):
                    Writelog(region + "研究区标准输出文件不存在,分区裁剪失败!", 0)
                    continue
                region_file = outdir + region + "Q" + os.path.sep + "32bit_" + datestr + ".tif"
                if not os.path.exists(os.path.dirname(region_file)):
                    os.makedirs(os.path.dirname(region_file))
                ret = Subset_Mask(ndwifile, region_base_file, region_file, unvalid_value)
                if ret == 0:
                    Writelog(region + "分区裁剪失败!", 0)
                    continue
                else:
                    ret = ModifiedXMLfile(receiptfile, product_type, "NDWI", region, "Quality", region_file)
                    if ret != 1:
                        Writelog("回传文件对应修改" + product_type + "产品NDWI数据" + region + "区域Quality结果失败!", 0)
                    else:
                        Writelog("回传文件对应修改" + product_type + "产品NDWI数据" + region + "区域Quality结果完成!", 1)
            Writelog("各研究区质量控制后的分区裁剪操作全部完成!", 1)
    else:
        # 删除耕地掩膜后b2file,b4file
        if os.path.exists(global_mask_files_dict[MOD09A1_suffixs[0]]):
            os.remove(global_mask_files_dict[MOD09A1_suffixs[0]])
        if os.path.exists(global_mask_files_dict[MOD09A1_suffixs[1]]):
            os.remove(global_mask_files_dict[MOD09A1_suffixs[1]])
        del global_mask_files_dict

    return 1


# 处理MOD13A2\MYD13A2\MOD15A2H\MOD16A2产品
def ExcuteProcess_MOD15A2H(inputfiles, product_type, datestr, projection, QA, outdir_dict, receiptfile,
                           bands, attributes, QAsuffix, resolution, unvalid_value, regions, ranges, configpath):

    suffixs = attributes.keys()
    regions2 = regions[:]
    if "China" in regions:
        regions.remove("China")

    pwdpath = os.path.realpath(__file__)
    # region_dir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + "resource" + os.path.sep + "standard" + os.path.sep
    region_dir = configpath + "standard" + os.path.sep
    if product_type == "MOD13A2" or product_type == "MYD13A2":
        region_dir = region_dir + "1000m" + os.path.sep
    else:
        region_dir = region_dir + "500m" + os.path.sep

    # 全球HDF数据分组
    Writelog('开始对全球HDF数据分组...', 1)
    res = mrt.GetSlice_HDF(inputfiles, product_type)
    if res == 0:
        Writelog('全球HDF数据分组失败!', 0)
        return 0
    else:
        Writelog('全球HDF数据分组完成!', 1)
        groups_files = res
    del res, inputfiles

    # MRT处理镶嵌投影各分组HDF数据
    Writelog('开始对分组数据镶嵌投影...', 1)
    res = mrt.MRTProcess(tempdir, groups_files, bands, projection, resolution, suffixs, ranges)
    if res == 0:
        Writelog('分组数据镶嵌投影失败！', 0)
        return 0
    else:
        Writelog('分组数据镶嵌投影完成！', 1)
        mrt_processed_files = res
    del res, groups_files

    # 各分组数据全球拼接-标准输出-无效值过滤-耕地掩膜(包含质量码波段)
    global_mask_files_dict = {}
    for i in range(len(suffixs)): global_mask_files_dict[suffixs[i]] = []
    base_file = region_dir + "Global.tif"
    # if (product_type == "MOD13A2") or (product_type == "MYD13A2"):
    #     mask_file = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + "resource" + os.path.sep + "mask" + os.path.sep + "global_cropland_mask_1km_standard.tif"
    # else:
    #     mask_file = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + "resource" + os.path.sep + "mask" + os.path.sep + "global_cropland_mask_500m_standard.tif"
    if (product_type == "MOD13A2") or (product_type == "MYD13A2"):
        mask_file = configpath + "mask" + os.path.sep + "global_cropland_mask_1km_standard.tif"
    else:
        mask_file = configpath + "mask" + os.path.sep + "global_cropland_mask_500m_standard.tif"

    if not os.path.exists(base_file):
        Writelog(base_file + "全球标准输出文件不存在!", 0)
        return 0
    if not os.path.exists(mask_file):
        Writelog(mask_file + "全球耕地掩膜文件不存在!", 0)
        return 0

    for i in range(len(suffixs)):
        Writelog("开始拼接" + suffixs[i] + "全球数据...", 1)
        temp_files = mrt_processed_files[suffixs[i]]
        global_resample_file = tempdir + "global_resampled_" + suffixs[i] + ".tif"
        fill_value = (attributes[suffixs[i]])['fillvalue']
        ret = GDAL_Mosaic(global_resample_file, temp_files, fill_value)
        if ret == 0:
            Writelog(suffixs[i] + "全球数据拼接失败!", 0)
            continue
        else:
            Writelog(suffixs[i] + "全球数据拼接完成!", 1)

        global_resample_file_ = tempdir + "global_resampled_" + suffixs[i] + "_.tif"
        gdal.Translate(global_resample_file_, global_resample_file, projWin=ranges)
        if os.path.exists(global_resample_file_) and os.path.exists(global_resample_file):
            os.remove(global_resample_file)

        Writelog("开始对" + suffixs[i] + "全球数据进行裁剪标准输出...", 1)
        global_subset_file = tempdir + "global_resampled_subset_" + suffixs[i] + ".tif"
        ret = Subset_Mask(global_resample_file_, base_file, global_subset_file, (attributes[suffixs[i]])['fillvalue'])
        if ret == 0:
            Writelog(suffixs[i] + "全球数据裁剪标准输出失败!", 0)
            continue
        else:
            Writelog(suffixs[i] + "全球数据裁剪标准输出完成!", 1)
            if os.path.exists(global_resample_file_):
                os.remove(global_resample_file_)

        Writelog("开始对" + suffixs[i] + "全球标准输出数据进行无效值过滤...", 1)
        if suffixs[i] == QAsuffix:
            if QAsuffix == "1_km_16_days_VI_Quality":
                data_type = gdal.GDT_UInt16
            else:
                data_type = gdal.GDT_Byte
            global_valid_file = tempdir + "global_resampled_subset_valid_" + suffixs[i] + ".tif"
        else:
            data_type = gdal.GDT_Float32
            global_valid_file = outdir_dict[suffixs[i]] + "GlobalO" + os.path.sep + "32bit-" + datestr + ".tif"
            if not os.path.exists(os.path.dirname(global_valid_file)):
                os.makedirs(os.path.dirname(global_valid_file))
        ret = Filter_unvalid(global_subset_file, attributes[suffixs[i]], global_valid_file, unvalid_value, data_type)
        if ret == 0:
            Writelog(suffixs[i] + "无效值过滤失败!", 0)
            continue
        else:
            Writelog(suffixs[i] + "无效值过滤完成!", 1)
            # 质量控制波段无效值过滤结果无须写入回传文件
            if suffixs[i] != QAsuffix:
                ret = ModifiedXMLfile(receiptfile, product_type, suffixs[i], "Global", "Original", global_valid_file)
                if ret != 1:
                    Writelog("回传文件对应修改" + product_type + "产品" + suffixs[i] + "数据集全球区域Original结果失败!", 0)
                else:
                    Writelog("回传文件对应修改" + product_type + "产品" + suffixs[i] + "数据集全球区域Original结果完成", 1)

            if os.path.exists(global_subset_file):
                os.remove(global_subset_file)

        Writelog("开始对" + suffixs[i] + "全球标准输出数据进行耕地掩膜...", 1)
        if suffixs[i] == QAsuffix:
            if QAsuffix == "1_km_16_days_VI_Quality":
                data_type = gdal.GDT_UInt16
            else:
                data_type = gdal.GDT_Byte
            global_mask_file = tempdir + "global_resampled_subset_valid_mask_" + suffixs[i] + ".tif"
        else:
            data_type = gdal.GDT_Float32
            global_mask_file = outdir_dict[suffixs[i]] + "Global" + os.path.sep + "32bit-" + datestr + ".tif"
            if not os.path.exists(os.path.dirname(global_mask_file)):
                os.makedirs(os.path.dirname(global_mask_file))
        ret = Crop_Mask(global_valid_file, mask_file, global_mask_file, unvalid_value, data_type)
        if ret == 0:
            Writelog(suffixs[i] + "耕地掩膜失败!", 0)
            continue
        else:
            Writelog(suffixs[i] + "耕地掩膜完成!", 1)
            # 质量控制波段掩膜结果无须写入回传文件
            if suffixs[i] != QAsuffix:
                ret = ModifiedXMLfile(receiptfile, product_type, suffixs[i], "Global", "Cropland_Mask", global_mask_file)
                if ret != 1:
                    Writelog("回传文件对应修改" + product_type + "产品" + suffixs[i] + "数据集全球区域Cropland_Mask结果失败!", 0)
                else:
                    Writelog("回传文件对应修改" + product_type + "产品" + suffixs[i] + "数据集全球区域Cropland_Mask结果完成", 1)
            global_mask_files_dict[suffixs[i]] = global_mask_file

    # 质量控制前分区裁剪(不包含质量码波段)
    Writelog("开始执行质量控制前的分区裁剪...", 1)
    global_mask_files_dict2 = deepcopy(global_mask_files_dict)
    if QA == "ON":
        QAfile = global_mask_files_dict2.pop(QAsuffix)
        suffixs.remove(QAsuffix)
    # 其它波段掩膜均失败,则不执行分区裁剪操作
    if len(global_mask_files_dict2) == 0:
        Writelog("所有波段耕地掩膜操作失败,不能执行分区裁剪!", 0)
        return 0
    suffixs2 = suffixs[:]
    for m in range(len(global_mask_files_dict2)):
        tempfile = global_mask_files_dict2[suffixs2[m]]
        if not os.path.exists(tempfile):
            Writelog(suffixs2[m] + "波段在耕地掩膜部分操作失败,不能执行分区裁剪!", 0)
            continue
        for n in range(len(regions)):
            region_base_file = region_dir + regions[n] + ".tif"
            if not os.path.exists(region_base_file):
                Writelog(regions[n] + "研究区标准输出文件不存在,分区裁剪失败!", 0)
                continue
            region_file = outdir_dict[suffixs2[m]] + regions[n] + os.path.sep + "32bit-" + datestr + ".tif"
            if not os.path.exists(os.path.dirname(region_file)):
                os.makedirs(os.path.dirname(region_file))
            ret = Subset_Mask(tempfile, region_base_file, region_file, unvalid_value)
            if ret == 0:
                Writelog(regions[n] + "分区裁剪失败!", 0)
                continue
            else:
                ret = ModifiedXMLfile(receiptfile, product_type, suffixs2[m], regions[n], "Cropland_Mask", region_file)
                if ret != 1:
                    Writelog("回传文件对应修改" + product_type + "产品" + suffixs2[m] + "数据集" + regions[n] + "区域Cropland_Mask结果失败!", 0)
                else:
                    Writelog("回传文件对应修改" + product_type + "产品" + suffixs2[m] + "数据集" + regions[n] + "区域Cropland_Mask结果完成", 1)
    Writelog("各研究区质量控制前的分区裁剪操作全部完成!", 1)

    # 如果需要执行质量控制
    # 质量控制完成后执行分区裁剪操作
    if QA == "ON":
        Writelog("开始执行质量控制...", 1)
        # 各产品对应的质量控制函数
        QA_dict = {'MOD13A2': QA_MOD13A2,
                   'MYD13A2': QA_MOD13A2,
                   'MOD15A2H': QA_MOD15A2H,
                   'MOD16A2': QA_MOD16A2}
        # 质量码波段在耕地掩膜部分处理失败,不能执行质量控制
        if not os.path.exists(QAfile):
            Writelog("质量码波段在耕地掩膜部分处理失败,不能执行质量控制!", 0)
            return 0
        for i in range(len(global_mask_files_dict2)):
            QA_input_file = global_mask_files_dict2[suffixs2[i]]
            if not os.path.exists(QA_input_file):
                Writelog(suffixs2[i] + "波段在耕地掩膜部分处理失败,不能执行质量控制!", 0)
                continue
            QA_output_file = outdir_dict[suffixs2[i]] + "GlobalQ" + os.path.sep + "32bit_" + datestr + ".tif"
            if not os.path.exists(os.path.dirname(QA_output_file)):
                os.makedirs(os.path.dirname(QA_output_file))
            ret = QA_dict[product_type](QA_input_file, QAfile, QA_output_file, unvalid_value)
            if ret == 0:
                Writelog(suffixs2[i] + "波段数据执行质量控制失败!", 0)
                continue
            else:
                Writelog(suffixs2[i] + "波段数据质量控制完成!", 1)

                ret = ModifiedXMLfile(receiptfile, product_type, suffixs2[i], "Global", "Quality", region_file)
                if ret != 1:
                    Writelog("回传文件对应修改" + product_type + "产品" + suffixs2[i] + "数据集Global区域Quality结果失败!", 0)
                else:
                    Writelog("回传文件对应修改" + product_type + "产品" + suffixs2[i] + "数据集Global区域Quality结果完成!", 1)

                Writelog(suffixs2[i] + "开始进行质量控制后分区裁剪...", 1)
                for j in range(len(regions)):
                    region_base_file = region_dir + regions[j] + ".tif"
                    if not os.path.exists(region_base_file):
                        Writelog(regions[j] + "研究区标准输出文件不存在,分区裁剪失败!", 0)
                        continue
                    region_file = outdir_dict[suffixs2[i]] + regions[j] + "Q" + os.path.sep + "32bit-" + datestr + ".tif"
                    if not os.path.exists(os.path.dirname(region_file)):
                        os.makedirs(os.path.dirname(region_file))
                    ret = Subset_Mask(QA_output_file, region_base_file, region_file, unvalid_value)
                    if ret == 0:
                        Writelog(regions[j] + "分区裁剪失败!", 0)
                        continue
                    else:
                        ret = ModifiedXMLfile(receiptfile, product_type, suffixs2[i], regions[j], "Quality", region_file)
                        if ret != 1:
                            Writelog("回传文件对应修改" + product_type + "产品" + suffixs2[i] + "数据集" + regions[j] + "区域Quality结果失败!", 0)
                        else:
                            Writelog("回传文件对应修改" + product_type + "产品" + suffixs2[i] + "数据集" + regions[j] + "区域Quality结果完成!", 1)
                Writelog("各研究区质量控制后的分区裁剪操作全部完成!", 1)

    return 1


# 主函数
def MODISPROCESS(paramfile, logfile_):
    '''
    # 执行MODIS数据预处理
    :param paramfile:    参数文件
    :param loginfofile_:    传入的日志文件
    :return: 1--执行成功, 0--执行失败
    '''

    # 记录开始时间
    starttime = datetime.datetime.now()

    # 将日志文件设为全局变量
    global logfile
    logfile = logfile_
    if not os.path.exists(os.path.dirname(logfile)):
        os.makedirs(os.path.dirname(logfile))
    Writelog('开始处理...', 1)

    pwdpath = os.path.realpath(__file__)

    # 判断MRT工具是否存在
    resampleexe = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'MRT' + os.path.sep + \
                  'bin' + os.path.sep + 'resample.exe'
    if not os.path.exists(resampleexe):
        Writelog(resampleexe + '工具不存在!', 0)
        print resampleexe + u"'工具不存在!'"
        return 0

    mrtmosaicexe = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'MRT' + os.path.sep + \
                   'bin' + os.path.sep + 'mrtmosaic.exe'
    if not os.path.exists(mrtmosaicexe):
        Writelog(mrtmosaicexe + '工具不存在!', 0)
        print mrtmosaicexe + u"'工具不存在!'"
        return 0

    mrtdatadir = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + 'MRT' + os.path.sep + 'data'
    if not os.path.exists(mrtdatadir):
        Writelog(mrtdatadir + '路径不存在!', 0)
        print mrtdatadir + u"'路径不存在!'"
        return 0

    #
    if not os.path.exists(paramfile):
        Writelog(paramfile + "参数文件不存在!", 0)
        return 0

    # 读取参数文件
    product_type = ReadConfig(paramfile, "Product_Type")
    if not product_type:
        Writelog(paramfile + "参数文件读取Product_Type失败!", 0)
        return 0
    datestr = ReadConfig(paramfile, "Date")
    if not datestr:
        Writelog(paramfile + "参数文件读取Date失败!", 0)
        return 0
    # projection = ReadConfig(paramfile, "Projection")
    # if not projection:
    #     Writelog(paramfile + "参数文件读取Projection失败!", 0)
    #     return 0
    QA = ReadConfig(paramfile, "QA")
    if not QA:
        Writelog(paramfile + "参数文件读取QA失败!", 0)
        return 0
    outdir = ReadConfig(paramfile, "Outputdir")
    if not outdir:
        Writelog(paramfile + "参数文件读取Outputdir失败!", 0)
        return 0
    receiptfile = ReadConfig(paramfile, "ReceiptFile")
    if not receiptfile:
        Writelog(paramfile + "参数文件读取ReceiptFile失败!", 0)
        return 0
    configpath = ReadConfig(paramfile, "ConfigPath")
    if not configpath:
        Writelog(paramfile + "参数文件读取ConfigPath失败!", 0)
        return 0
    tempdir_ = ReadConfig(paramfile, "Tempdir")
    if not tempdir_:
        Writelog(paramfile + "参数文件读取Tempdir失败!", 0)
        return 0
    inputfiles = ReadConfig(paramfile, "InputFiles")
    if not inputfiles:
        Writelog(paramfile + "参数文件读取Inputfiles失败!", 0)
        return 0

    print product_type
    print datestr
    # print projection
    print QA
    print outdir
    print receiptfile
    print configpath
    print tempdir_
    print len(inputfiles)

    product_type_list = ["MOD09A1", "MOD13A2", "MOD15A2H", "MOD16A2", "MYD13A2"]
    if not (product_type in product_type_list):
        Writelog(product_type + "设置有误!", 0)
        return 0

    # 输出路径不存在则创建
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # 创建临时路径并设为全局变量
    global tempdir
    tempdir = tempdir_ + os.path.sep + str(time.time()).strip() + os.path.sep
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)

    # 读取系统配置文件
    if QA == "ON":
        systemfile = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + "system" + os.path.sep + "system_QA.xml"
        if not os.path.exists(systemfile):
            Writelog(systemfile + "系统配置文件不存在!", 0)
            return 0
        bands = str(ReadSysConfig(systemfile, product_type, "Bands"))
        attributes = ReadSysConfig(systemfile, product_type, "Attributes")
        QAsuffix = str(ReadSysConfig(systemfile, product_type, "QAsuffix"))
        resolution = str(ReadSysConfig(systemfile, product_type, "Resolution"))
        unvalid_value_ = ReadSysConfig(systemfile, product_type, "Unvalid_value")
        unvalid_value = float(unvalid_value_)
    else:
        systemfile = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + "system" + os.path.sep + "system.xml"
        if not os.path.exists(systemfile):
            Writelog(systemfile + "系统配置文件不存在!", 0)
            return 0
        bands = str(ReadSysConfig(systemfile, product_type, "Bands"))
        attributes = ReadSysConfig(systemfile, product_type, "Attributes")
        QAsuffix = None
        resolution = str(ReadSysConfig(systemfile, product_type, "Resolution"))
        unvalid_value_ = ReadSysConfig(systemfile, product_type, "Unvalid_value")
        unvalid_value = float(unvalid_value_)

    print bands
    print attributes
    print QAsuffix
    print resolution
    print unvalid_value

    # 处理范围(MRT设置投影类型用到,镶嵌后全球标准输出前gdal.warp操作用到)
    ranges = [-180.0, 72.0, 180.0, -58.0]

    # 读取研究区
    regions_file = os.path.dirname(os.path.dirname(pwdpath)) + os.path.sep + "system" + os.path.sep + "regions.xml"
    if not os.path.exists(regions_file):
        Writelog(regions_file + "存放研究区的配置文件不存在!", 0)
        return 0
    domxml = xmldom.parse(regions_file)
    rootElement = domxml.documentElement
    propertiesElements = rootElement.getElementsByTagName("Properties")
    if len(propertiesElements) != 1:
        Writelog(regions_file + "格式异常!", 0)
        del domxml, rootElement, propertiesElements
        return 0
    regionsElements = propertiesElements[0].getElementsByTagName("Regions")
    if len(regionsElements) != 1:
        Writelog(regions_file + "格式异常!", 0)
        del domxml, rootElement, propertiesElements, regionsElements
        return 0
    regions_str = str(regionsElements[0].getAttribute("value"))
    regions = regions_str.split(";")
    del domxml, rootElement, propertiesElements, regionsElements, regions_str
    print regions

    # 预设回传文件
    if product_type == "MOD09A1":
        ret = PreReceiptXML(receiptfile, QA, product_type, ["NDWI"], regions)
    else:
        if QA == "ON":
            temp_var = attributes.keys()
            temp_var.remove(QAsuffix)
            ret = PreReceiptXML(receiptfile, QA, product_type, temp_var, regions)
        else:
            ret = PreReceiptXML(receiptfile, QA, product_type, attributes.keys(), regions)
    if ret != 1:
        Writelog(receiptfile + "回传文件预设失败!", 0)
        return 0
    else:
        Writelog(receiptfile + "回传文件预设完成!", 1)

    try:
        if product_type == "MOD09A1":
            outdir = outdir + "NDWI" + os.path.sep
            Writelog("开始处理除中国外的其它国家地区与全球的" + product_type + "数据...", 1)
            projection = "GEO"
            ret = ExcuteProcess_MOD09A1(inputfiles, product_type, datestr, projection, QA, outdir, receiptfile,
                                        bands, attributes, QAsuffix, resolution, unvalid_value, regions, ranges, configpath)
            if ret == 1:
                Writelog("除中国外的其它国家地区与全球的" + product_type + "数据处理完成!", 1)
            else:
                Writelog("除中国外的其它国家地区与全球的" + product_type + "数据处理失败!", 0)

            Writelog("开始处理中国区的" + product_type + "数据...", 1)
            projection = "Albers"
            if resolution == '0.00833333':
                resolution = '1000'
            elif resolution == '0.0041666650':
                resolution = '500'
            ret = MODISPRO_China.ExcuteProcess_MOD09A1_China(inputfiles, product_type, datestr, projection, QA, outdir, receiptfile,
                                bands, attributes, QAsuffix, resolution, unvalid_value, ranges, tempdir, configpath)
            if ret == 1:
                Writelog("中国区的" + product_type + "数据处理完成!", 1)
            else:
                Writelog("中国区的" + product_type + "数据处理失败!", 0)

        else:
            outdir_dict = {'MOD13A2': {"1_km_16_days_NDVI": outdir + "NDVI" + os.path.sep},
                           'MYD13A2': {"1_km_16_days_NDVI": outdir + "NDVI" + os.path.sep},
                           'MOD15A2H': {"Fpar_500m": outdir + "FPAR" + os.path.sep,
                                        "Lai_500m": outdir + "LAI" + os.path.sep},
                           'MOD16A2': {"ET_500m": outdir + "ET" + os.path.sep}}
            Writelog("开始处理除中国外的其它国家地区与全球的" + product_type + "数据...", 1)
            projection = "GEO"
            ret = ExcuteProcess_MOD15A2H(inputfiles, product_type, datestr, projection, QA, outdir_dict[product_type], receiptfile,
                                         bands, attributes, QAsuffix, resolution, unvalid_value, regions, ranges, configpath)
            if ret == 1:
                Writelog("除中国外的其它国家地区与全球的" + product_type + "数据处理完成!", 1)
            else:
                Writelog("除中国外的其它国家地区与全球的" + product_type + "数据处理失败!", 0)

            Writelog("开始处理中国区的" + product_type + "数据...", 1)
            projection = "Albers"
            if resolution == '0.00833333':
                resolution = '1000'
            elif resolution == '0.0041666650':
                resolution = '500'
            ret = MODISPRO_China.ExcuteProcess_MOD15A2H_China(inputfiles, product_type, datestr, projection, QA, outdir_dict[product_type], receiptfile,
                                 bands, attributes, QAsuffix, resolution, unvalid_value, ranges, tempdir, configpath)
            if ret == 1:
                Writelog("中国区的" + product_type + "数据处理完成!", 1)
            else:
                Writelog("中国区的" + product_type + "数据处理失败!", 0)

        print u'开始时间: ', starttime
        print u'结束时间: ', datetime.datetime.now()
        if ret != 1:
            print u'最终处理失败!'
            return 0
        else:
            print u'最终处理完成!'
            return 1
    except Exception, e:
        Writelog(e.message, 0)
        print e
        return 0
    finally:
        Deletedir(tempdir)
