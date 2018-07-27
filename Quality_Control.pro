pro Quality_Control
  compile_opt idl2
  envi,/restore_base_save_files
  envi_batch_init  

  infile='G:\Temp\1111111.1_km_16_days_NDVI.tif'
  qualityfile='G:\Temp\1111111.1_km_16_days_VI_Quality.tif'
  outfile='G:\Temp\1111111.1_km_16_days_NDVI_Rule2_BitFilter.dat'
;  outfile='G:\Temp\MOD13A2_20180610_GEO_Quality.dat'

  validvalues=[1024,2048,3072]

  envi_open_file,infile,r_fid=infid
  envi_file_query,infid,dims=dims,ns=ns,nl=nl,data_type=data_type
  mapinfo=envi_get_map_info(fid=infid)
  envi_open_file,qualityfile,r_fid=quality_fid


;;  整体
;  print,'Start time:'
;  print,systime(/julian),format='(c(CYI,"-",CMOI,"-",CDI," ",CHI,":",CMI,":",CSI))'
;  ndvi_data=fltarr(ns,nl)-999.
;  ndvi_data_=envi_get_data(fid=infid,dims=dims,pos=[0])
;  quality_data=envi_get_data(fid=quality_fid,dims=dims,pos=[0])
;
;  quality_data_1=string(temporary(quality_data),format='(B016)')
;  quality_data_2=strmid(temporary(quality_data_1),2,4)
;  index=where(((quality_data_2 eq '0000') or (quality_data_2 eq '0001') or $
;              (quality_data_2 eq '0010') or (quality_data_2 eq '0011')) and (ndvi_data_ ne -3000), count)
;  if count gt 0 then ndvi_data[index]=ndvi_data_[index]*0.0001
;  ndvi_data_=!null & quality_data_2=!null
;
;  envi_write_envi_file, $
;    temporary(ndvi_data), $
;    ns=ns,nl=nl,nb=1, $
;    offset=0, $
;    interleave=0, $
;    out_dt=4, $
;    map_info=mapinfo, $
;    out_name=outfile, $
;    /write
;  envi_file_mng,id=infid,/remove
;  envi_file_mng,id=quality_fid,/remove
;  print,'End time:'
;  print,systime(/julian),format='(c(CYI,"-",CMOI,"-",CDI," ",CHI,":",CMI,":",CSI))'


;;  分块
;  print,'Start time:'
;  print,systime(/julian),format='(c(CYI,"-",CMOI,"-",CDI," ",CHI,":",CMI,":",CSI))'
;  openw,lun,outfile,/get_lun,/append
;  step=nl/40
;  for i=0,nl-1,step do begin
;    if i+step le nl-1 then numrows=i+step-1 $
;    else numrows=nl-1
;    print,i,numrows
;    ndvi_data=fltarr(ns,numrows-i+1)-999
;    ndvi_data_=envi_get_data(fid=infid,dims=[-1,0,ns-1,i,numrows],pos=[0])
;    quality_data=envi_get_data(fid=quality_fid,dims=[-1,0,ns-1,i,numrows],pos=[0])
;    quality_data_1=string(temporary(quality_data),format='(B016)')
;    quality_data_2=strmid(temporary(quality_data_1),2,4)
;    index=where(((quality_data_2 eq '0000') or (quality_data_2 eq '0001') or $
;                (quality_data_2 eq '0010') or (quality_data_2 eq '0011')) and (ndvi_data_ ne -3000), count)
;    if count gt 0 then begin
;      ndvi_data[index]=ndvi_data_[index]*0.0001
;    endif
;
;    ndvi_data_=!null & quality_data_2=!null
;    writeu,lun,temporary(ndvi_data)
;  endfor
;  free_lun,lun
;
;  envi_setup_head, $
;    fname=outfile, $
;    ns=ns,nl=nl,nb=1, $
;    data_type=4, $
;    offset=0, $
;    interleave=0, $
;    map_info=mapinfo, $
;    /write
;  envi_file_mng,id=infid,/remove
;  envi_file_mng,id=quality_fid,/remove
;  print,'End time:'
;  print,systime(/julian),format='(c(CYI,"-",CMOI,"-",CDI," ",CHI,":",CMI,":",CSI))'


;  位运算
  print,'Start time:'
  print,systime(/julian),format='(c(CYI,"-",CMOI,"-",CDI," ",CHI,":",CMI,":",CSI))'
  openw,lun,outfile,/get_lun,/append
  step=nl/10
  for i=0,nl-1,step do begin
    if i+step le nl-1 then numrows=i+step-1 $
    else numrows=nl-1
    print,i,numrows
    ndvi_data=fltarr(ns,numrows-i+1)-999
    ndvi_data_=envi_get_data(fid=infid,dims=[-1,0,ns-1,i,numrows],pos=[0])
    quality_data=envi_get_data(fid=quality_fid,dims=[-1,0,ns-1,i,numrows],pos=[0])
    
    ;Rule-1
    ;*******************************************************************
    ;Dataset1={(MODLAND_QA=00) or (MODLAND_QA=01 and VI Useful=(0000~0111))}
    ;'0100000000000000'-->2L^14
    ;'0110000000000000'-->24576
    ;*******************************************************************
    index=where(quality_data lt 24576,count)
    ndvi_data[index]=ndvi_data_[index]*0.0001
    
    
    ;Rule-2
    ;*******************************************************************
    ;Dataset2={(MODLAND_QA=00) or ((MODLAND_QA=01) and (VI Useful=(0000~0111) and (Mixed Clouds=0) and (Possible Shadow=0)))}
    ;
    ;******************************************************************* 
    index=where(quality_data lt 24576,count)
    temp_data_1=(quality_data and 2L^5)
    temp_data_2=(quality_data and 2L^1)
    index_1=where(temp_data_1 eq 2L^5,count_1)
    index_2=where(temp_data_2 eq 2L^1,count_2)
    ndvi_data[index]=ndvi_data_[index]*0.0001
    ndvi_data[index_1]=-3000
    ndvi_data[index_2]=-3000
    
    
;    for j=0,n_elements(validvalues)-1 do begin
;      ;Rule-3
;      ;除去前两位的影响
;      index=where((quality_data ne 65535) and (quality_data ge 32768),count)
;      if count gt 0 then quality_data[index]-=32768
;      index=where((quality_data ne 65535) and (quality_data ge 16384),count)
;      if count gt 0 then quality_data[index]-=16384
;      
;      temp_data_1=(quality_data and validvalues[j])
;      temp_data_2=(quality_data xor validvalues[j])
;      index=where((temp_data_1 eq validvalues[j]) and (temp_data_2 lt validvalues[j]) and $
;                  (quality_data ne 65535) and (ndvi_data_ ne -3000) or (quality_data eq 0),count)
;      if count gt 0 then begin
;        ndvi_data[index]=ndvi_data_[index]*0.0001
;      endif
;    endfor

    ndvi_data_=!null & quality_data=!null 
    temp_data_1=!null & temp_data_2=!null
    writeu,lun,temporary(ndvi_data)
  endfor
  free_lun,lun

  envi_setup_head, $
    fname=outfile, $
    ns=ns,nl=nl,nb=1, $
    data_type=4, $
    offset=0, $
    interleave=0, $
    map_info=mapinfo, $
    /write
  envi_file_mng,id=infid,/remove
  envi_file_mng,id=quality_fid,/remove
  print,'End time:'
  print,systime(/julian),format='(c(CYI,"-",CMOI,"-",CDI," ",CHI,":",CMI,":",CSI))'


;;  提取符合质量要求的像素
;  print,'Start time:'
;  print,systime(/julian),format='(c(CYI,"-",CMOI,"-",CDI," ",CHI,":",CMI,":",CSI))'
;  openw,lun,outfile,/get_lun,/append
;  step=nl/20
;  for i=0,nl-1,step do begin
;    if i+step le nl-1 then numrows=i+step-1 $
;    else numrows=nl-1
;    print,i,numrows    
;    quality_data=envi_get_data(fid=quality_fid,dims=[-1,0,ns-1,i,i+step-1],pos=[0])
;    quality_data_1=string(temporary(quality_data),format='(B016)')
;    quality_data_2=strmid(temporary(quality_data_1),2,4)
;    index=where((quality_data_2 eq '0000') or (quality_data_2 eq '0001') or $
;      (quality_data_2 eq '0010') or (quality_data_2 eq '0011'),count)
;    data=bytarr(ns,numrows-i+1)
;    if count gt 0 then data[index]=1B
;    quality_data_2=!null  
;    
;    writeu,lun,temporary(data)    
;  endfor
;  free_lun,lun
;
;  envi_file_mng,id=infid,/remove
;  envi_file_mng,id=quality_fid,/remove
;  print,'End time:'
;  print,systime(/julian),format='(c(CYI,"-",CMOI,"-",CDI," ",CHI,":",CMI,":",CSI))'
  
end



function bin2dec,n
  p=strlen(n)
  y=0L
  for i=0,p-1 do begin

    y=y+strmid(n,i,1)*2^(p-i-1)

  endfor
  return,y
end