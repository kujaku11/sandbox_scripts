# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 10:44:51 2021

@author: jpeacock
"""
import re
col_width = 32
pstr = ("             RUN INFORMATION                     STATION 1\n"             
        "PROCESSED FROM DFT TIME SERIES     STN Number: 17-S2a     \n"         
        "SURVEY: Don Campbell              Site Desc; BadR: 0 SatR: 109\n"    
        "COMPANY:                           Lat  38:50:221N Long 118:17:525W\n"
        "    JOB: S2                        Elevation: 1277   M. DECL: 13.00\n"
        "Lat 38:50.368 N Lng 118:17.875 W   Reference Site: REM-C06         \n"
        "HARDWARE: MTU5A MTU5A              Site Permitted by:              \n"
        "START-UP: 2017/12/06 - 23:39:13    Site Layout by:                 \n"
        "END-TIME: 2017/12/08 - 13:37:25            SYSTEM INFORMATION      \n"
        "FILE: 4263C06B 2346C07A            MTU-Box Serial Number: U-4263   \n"
        "MTUPROG VERSION: 3112G3            MTU-Box Gains:E`s x 4 H`s x 1   \n"
        "MTU-DFT VERSION: TStoFT.38         MTU-Ref Serial Number: U-2346   \n"
        "MTU-RBS VERSION:R2012-0216-B22     Comp Chan#   Sensor     Azimuth \n"
        "Reference Field: Remote H - Ref.    Ex1   1     98.20 M   40.0 DGmn\n"
        "  XPR Weighting: RHO Variance.      Ey1   2     100.0 M  130.0 DGmn\n"
        "RBS: 7  COH: 0.85  RHO VAR: 0.75    Hx1   3    BMT53694   40.0 DGmn\n"
        "CUTOFF: 0.11 COH: 35 % VAR: 25 %    Hy1   4    BMT53731  130.0 DGmn\n"
        "Notch Filters set for 60 Hz.        Hz1   5    BMT53191            \n"
        "                                   RHx2   6    BMT53692    0.0 DGmn\n"
        "  Comp   MTU box  S/N   Temp       RHy2   7    BMT53693   90.0 DGmn\n"
        "Ex & Ey: MTU5A    4263   11 C      Ebat:9.93V Hbat:9.93V Rbat:12.0V\n"
        "Hx & Hy: MTU5A    4263   11 C      Ex Pot Resist: 0.386 Kohms      \n"
        "     Hz: MTU5A    4263   11 C      Ex Voltage:AC=108.mV, DC=-2.00mV\n"
        "Rx & Ry: MTU5A    2346   25 C      Ey Pot Resist: 0.371 Kohms      \n"
        " Hx Sen: BMT53694                  Ey Voltage:AC=62.7mV, DC=-4.40mV\n"
        " Hy Sen: BMT53731                  \n"
        " Hz Sen: BMT53191                  \n"
        " Rx Sen: BMT53692                  \n"
        " Ry Sen: BMT53693 ")

info_dict = {}
tlist = []
blist = []

for line in pstr.split("\n"):
    line = line.strip()
    if len(line) > col_width:
        tlist.append(line[0:col_width].strip())
        blist.append(line[col_width:].strip())
    else:
        tlist.append(line)
    #     line_2 = None
        
    # for l in [line_1, line_2]:
    #     if l is None:
    #         continue
    #     if l.count(":") == 1:
    #         k, v = [x.strip() for x in l.split(":")]
    #         info_dict[k] = v
            
        
        