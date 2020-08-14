# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 11:22:48 2020

1.添加一个新的功能栏按需搜素按钮
2.添加进度条显示栏
3.添加左下角状态标签
4.鼠标移动到按钮时显示功能
5.修改EF搜索逻辑
6.修改文件生成路径，修改英文版本


@author: Roy
"""





# 用于智能卡功能
from PySmartCard.CpuCard import PcscReader
#用于GUI窗口模块
from tkinter import*
#下拉选项单
from tkinter.ttk import*
#提示信息
from tkinter import messagebox
#另存为菜单
from tkinter.filedialog import asksaveasfilename
#时间系统
import time
#CSV文件系统
import csv
#创建根目录文件
import os
import sys
#启动线程用
import threading
import inspect
import ctypes





#创建一个输出列表,系统判断列表,和DF判断字段
OUTPUT_LIST = []
OUTPUT_sys = []
judge_DF = ''



#创建输出目录
if not os.path.exists(r'D:\File_search_tool'):
    os.makedirs(r'D:\File_search_tool')
    


    
# 单独执行指令，无需过滤
def send_apdu_common(reader, apdu, recv_list, readertype=None):
    # Clear list
    recv_list[:] = []
    #剔除命令中空白字符
    apdu = apdu.replace(" ", "")
    # print(apdu)
    text.insert('insert',apdu)
    text.insert('insert','\n')
    result = reader.send_apdu(apdu, readertype)
    recv_list.append(result[:])
    global judge_DF
    judge_DF = ''
    text.insert('insert',result)
    text.insert('insert','\n')
    window.update()
    

#如果为 00 A4 00 04 02 XXXX，则出现FCP模板   
def send_apducommand_DF(reader, apdu, recv_list, readertype=None):
        send_apdu_DF(reader, apdu, recv_list, readertype)
        if recv_list[0][0:2] == "61":
            apdu = "00C00000" + recv_list[0][2:4]
            send_apdu_DF(reader, apdu, recv_list, readertype)
        elif recv_list[0][0:2] == "6C":
            apdu = apdu[0:8] + recv_list[0][2:4]
            send_apdu_DF(reader, apdu, recv_list, readertype)

#判别3F00下的DF是否存在       
def send_apdu_DF(reader, apdu, recv_list, readertype=None):
    # Clear list
    recv_list[:] = []
    apdu = apdu.replace(" ", "")
    result = reader.send_apdu(apdu, readertype)
    recv_list.append(result[:])
    #全局变量让函数内的值可以和外部相通
    global OUTPUT_LIST
    global OUTPUT_sys
    global judge_DF
    if recv_list[0][8:10] == '78':
        a = recv_list[0].index('8B')
        OUTPUT_LIST.append([recv_list[0][16:20],'Sharable -78'])
        OUTPUT_sys.append([recv_list[0][16:20],'Master',recv_list[0][a+4:a+10],
        '','','','','',recv_list[0][a:a+2],'Sharable'])
        text.insert('insert',result)
        text.insert('insert','\n')
        judge_DF = '78'     
        # if recv_list[0][16:20] == '3F00':
        #     OUTPUT_LIST.append([recv_list[0][16:20],'Sharable -78'])
        #     OUTPUT_sys.append([recv_list[0][16:20],'Master',recv_list[0][40:46],
        #     '','','','','',recv_list[0][36:38],'Sharable'])
        #     text.insert('insert',result)
        #     text.insert('insert','\n')
        #     judge_DF = '78'           
        # else:
        #     OUTPUT_LIST.append([recv_list[0][16:20],'Sharable -78'])
        #     OUTPUT_sys.append([recv_list[0][16:20],'DF',recv_list[0][30:36],
        #     '','','','','',recv_list[0][26:28],'Sharable'])
        #     text.insert('insert',result)
        #     text.insert('insert','\n')
        #     judge_DF = '78'

    elif recv_list[0][8:10] =='38':
        a = recv_list[0].index('8B')
        OUTPUT_LIST.append([recv_list[0][16:20],'Unsharable -38'])
        OUTPUT_sys.append([recv_list[0][16:20],'DF',recv_list[0][a+4:a+10],
            '','','','','',recv_list[0][a:a+2],'Sharable'])
        text.insert('insert',result)
        text.insert('insert','\n')
        judge_DF = '38'
        
    else:
        judge_DF = ''
        
#如果为 00 A4 00 04 02 XXXX，则出现FCP模板   
def send_apducommand_EF(reader, apdu, recv_list, readertype=None):
        send_apdu_EF(reader, apdu, recv_list, readertype)
        if recv_list[0][0:2] == "61":
            apdu = "00C00000" + recv_list[0][2:4]
            send_apdu_EF(reader, apdu, recv_list, readertype)
        elif recv_list[0][0:2] == "6C":
            apdu = apdu[0:8] + recv_list[0][2:4]
            send_apdu_EF(reader, apdu, recv_list, readertype)

#判断EF类型并并储存        
def send_apdu_EF(reader, apdu, recv_list, readertype=None):
    global OUTPUT_LIST
    global OUTPUT_sys
    # Clear list
    recv_list[:] = []
    apdu = apdu.replace(" ", "")
    result = reader.send_apdu(apdu, readertype)
    recv_list.append(result[:])
    text.insert('insert',result)
    text.insert('insert','\n')


# 返回信息有4种情况(长度：52,54,58,60)   
    if len(recv_list[0]) == 52 :
        if  recv_list[0][8:10] == '41':
            File_type = 'Tran-41'
            File_access = 'Sharable'
        elif recv_list[0][8:10] == '01':
            File_type = 'Tran-01'
            File_access = 'Unsharable'
        elif recv_list[0][8:10] == '42':
            File_type = 'Linear-42'
            File_access = 'Sharable'
        elif recv_list[0][8:10] == '02': 
            File_type = 'Linear-02'
            File_access = 'Unsharable'
        elif recv_list[0][8:10] == '46':
            File_type =  'Cyclic-46'
            File_access = 'Sharable'
        elif recv_list[0][8:10] == '06':
            File_type =  'Cyclic-06'
            File_access = 'Unsharable'
        elif recv_list[0][8:10] == '0A':
            File_type = 'Intenal EF'
            File_access = 'Unsharable'
        else:
            File_type = '未知种类'
        if recv_list[0][16:18] == '00':
            File_ID = '"' + recv_list[0][16:20]
        else:
            File_ID = recv_list[0][16:20]
        File_Security =  recv_list[0][30:36]
        File_Size =  recv_list[0][40:44]
        aa = int('0x'+File_Size,16) // 255
        SFI =  'None'
        S_tag = recv_list[0][26:28]
        File_record_list =[]
        if recv_list[0][8:10] == '41' or recv_list[0][8:10] == '01':
             for i in range(1,aa + 2):
                if i == 1 and  aa == 0:
                    apdu = "00B000" + File_Size
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A86':
                        File_record_list.append(recv_list[0][:-4])
                elif i == 1 and aa != 0:
                    apdu = "00B00000" + 'FF'
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A86':
                        File_record_list.append(recv_list[0][:-4])
                elif i == 2:
                    apdu = "00B000FF" + 'FF'
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A86':
                        File_record_list.append(recv_list[0][:-4])
                elif 2 < i <=16:
                    apdu = "00B00" +str((hex((0xff)*(i-1)))[-3:]) +'FF'
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A86':
                        File_record_list.append(recv_list[0][:-4])
                elif i==17:
                    apdu = "00B00FF0"  +'FF'
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A86':
                        File_record_list.append(recv_list[0][:-4])
                elif 17 < i<=128:
                    apdu = "00B0" +str((hex((0xff)*(i-1)))[-4:]) +'FF'
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A86':
                        File_record_list.append(recv_list[0][:-4])
                elif i == 129:
                    apdu = "00B0" +str((hex((0xff)*(i-1)))[-4:]) +'7F'
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A86':
                        File_record_list.append(recv_list[0][:-4])
                else:
                    break
             tree.insert(id_XXXX,index=END,text= tree_file_name ,image=BIN)
        #把列表转化为字符串
        File_record_list_str = '      '.join(File_record_list)
        File_record_list_str2 = ' ' + File_record_list_str
        #输出到列表进行储存
        OUTPUT_LIST.append([File_ID,File_type,File_Security,File_Size,
        '','',File_record_list_str2,SFI])
        OUTPUT_sys.append([File_ID,File_type,File_Security,File_Size,
        '','',File_record_list,SFI,S_tag,File_access])

        
    elif len(recv_list[0]) == 54 :
        if  recv_list[0][8:10] == '41':
            File_type = 'Tran-41'
            File_access = 'Sharable'
        elif recv_list[0][8:10] == '01':
            File_type = 'Tran-01'
            File_access = 'Unsharable'
        elif recv_list[0][8:10] == '42':
            File_type = 'Linear-42'
            File_access = 'Sharable'
        elif recv_list[0][8:10] == '02': 
            File_type = 'Linear-02'
            File_access = 'Unsharable'
        elif recv_list[0][8:10] == '46':
            File_type =  'Cyclic-46'
            File_access = 'Sharable'
        elif recv_list[0][8:10] == '06':
            File_type =  'Cyclic-06'
            File_access = 'Unsharable'
        elif recv_list[0][8:10] == '0A':
            File_type = 'Intenal EF'
            File_access = 'Unsharable'
        else:
            File_type = '未知种类'
        if recv_list[0][16:18] == '00':
            File_ID = '"' + recv_list[0][16:20]
        else:
            File_ID = recv_list[0][16:20]
        File_Security = recv_list[0][30:36]
        File_Size =  recv_list[0][40:44]
        aa = int('0x'+File_Size,16) // 255
        SFI =  'None'
        S_tag = recv_list[0][26:28]
        File_record_list =[]
        if recv_list[0][8:10] == '41' or recv_list[0][8:10] == '01':
           for i in range(1,aa + 2):
                if i == 1 and  aa == 0:
                    apdu = "00B000" + File_Size
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A86':
                        File_record_list.append(recv_list[0][:-4])
                elif i == 1 and aa != 0:
                    apdu = "00B00000" + 'FF'
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A86':
                        File_record_list.append(recv_list[0][:-4])
                elif i == 2:
                    apdu = "00B000FF" + 'FF'
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A86':
                        File_record_list.append(recv_list[0][:-4])
                elif 2 < i <=16:
                    apdu = "00B00" +str((hex((0xff)*(i-1)))[-3:]) +'FF'
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A86':
                        File_record_list.append(recv_list[0][:-4])
                elif i==17:
                    apdu = "00B00FF0"  +'FF'
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A86':
                        File_record_list.append(recv_list[0][:-4])
                elif 17 < i <=128:
                    apdu = "00B0" +str((hex((0xff)*(i-1)))[-4:]) +'FF'
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A86':
                        File_record_list.append(recv_list[0][:-4])
                elif i == 129:
                    apdu = "00B0" +str((hex((0xff)*(i-1)))[-4:]) +'7F'
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A86':
                        File_record_list.append(recv_list[0][:-4])
                else:
                    break
           tree.insert(id_XXXX,index=END,text= tree_file_name ,image=BIN)
        File_record_list_str = '      '.join(File_record_list)
        File_record_list_str2 = ' ' + File_record_list_str
        OUTPUT_LIST.append([File_ID,File_type,File_Security,File_Size,
        '','',File_record_list_str2,SFI])
        OUTPUT_sys.append([File_ID,File_type,File_Security,File_Size,
        '','',File_record_list,SFI,S_tag,File_access])
       
    elif len(recv_list[0]) == 58 :
        if  recv_list[0][8:10] == '41':
            File_type = 'Tran-41'
            File_access = 'Sharable'
        # elif recv_list[0][8:10] == '01':
        #     File_type = 'Tran-01'
        #     File_access = 'Unsharable'
        elif recv_list[0][8:10] == '42':
            File_type = 'Linear-42'
            File_access = 'Sharable'
        # elif recv_list[0][8:10] == '02': 
        #     File_type = 'Linear-02'
        #     File_access = 'Unsharable'
        elif recv_list[0][8:10] == '46':
            File_type =  'Cyclic-46'
            File_access = 'Sharable'
        # elif recv_list[0][8:10] == '06':
        #     File_type =  'Cyclic-06'
        #     File_access = 'Unsharable'
        elif recv_list[0][8:10] == '0A':
            File_type = 'Intenal EF'
            File_access = 'Unsharable'
        else:
            File_type = '未知种类'
            
       
        File_lenth = recv_list[0][14:16]
        File_record_len = recv_list[0][12:16]
        File_record_num =  recv_list[0][16:18]
        if recv_list[0][22:24] == '00':
            File_ID = '"' + recv_list[0][22:26]
        else:
            File_ID = recv_list[0][22:26]
        File_Security =  recv_list[0][36:42]
        File_Size = recv_list[0][46:50]
        SFI = 'None'
        S_tag = recv_list[0][32:34]
        File_record_list = []
        if recv_list[0][8:10] == '42' or recv_list[0][8:10] == '46' or  recv_list[0][8:10] == '0A':
            for i in range(1,int(('0x' + recv_list[0][16:18]),16) + 1):
                if 0 < i < 10:
                    apdu = "00B20" + str(i) + "04" +  File_lenth
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A83':
                            File_record_list.append(recv_list[0][:-4])
                elif i < 50:
                    apdu = "00B2" + str(i) + "04" +  File_lenth
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A83':
                            File_record_list.append(recv_list[0][:-4])
                else:
                    break
            tree.insert(id_XXXX,index=END,text= tree_file_name ,image=record)
        File_record_list_str = '      '.join(File_record_list)
        File_record_list_str2 = ' ' + File_record_list_str
        OUTPUT_LIST.append([File_ID,File_type,File_Security,File_Size,
        File_record_len,File_record_num,File_record_list_str2,SFI])
        OUTPUT_sys.append([File_ID,File_type,File_Security,File_Size,
        File_record_len,File_record_num,File_record_list,SFI,S_tag,File_access])

        
    elif len(recv_list[0]) == 60 :
        if  recv_list[0][8:10] == '41':
            File_type = 'Tran-41'
            File_access = 'Sharable'
        # elif recv_list[0][8:10] == '01':
        #     File_type = 'Tran-01'
        #     File_access = 'Unsharable'
        elif recv_list[0][8:10] == '42':
            File_type = 'Linear-42'
            File_access = 'Sharable'
        # elif recv_list[0][8:10] == '02': 
        #     File_type = 'Linear-02'
        #     File_access = 'Unsharable'
        elif recv_list[0][8:10] == '46':
            File_type =  'Cyclic-46'
            File_access = 'Sharable'
        # elif recv_list[0][8:10] == '06':
        #     File_type =  'Cyclic-06'
        #     File_access = 'Unsharable'
        elif recv_list[0][8:10] == '0A':
            File_type = 'Intenal EF'
            File_access = 'Unsharable'
        else:
            File_type = '未知种类'
        File_record_len = recv_list[0][12:16]
        File_record_list = []
        File_lenth = recv_list[0][14:16]
        File_record_num = recv_list[0][16:18]
        if recv_list[0][22:24] == '00':
            File_ID = '"' + recv_list[0][22:26]
        else:
            File_ID = recv_list[0][22:26]
        File_Security = recv_list[0][36:42]
        File_Size =  recv_list[0][46:50]
        SFI = recv_list[0][54:56]
        S_tag = recv_list[0][32:34]
        if recv_list[0][8:10] == '42' or recv_list[0][8:10] == '46' or recv_list[0][8:10] == '0A':
            for i in range(1,int(('0x' + recv_list[0][16:18]),16) + 1):
                if 0 < i < 10:
                    apdu = "00B20" + str(i) + "04" +  File_lenth
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A83':
                            File_record_list.append(recv_list[0][:-4])
                elif i < 50:
                    apdu = "00B2" + str(i) + "04" +  File_lenth
                    send_apdu_common(reader, apdu, recv_list, readertype)
                    if recv_list[0] != '6A83':
                            File_record_list.append(recv_list[0][:-4])
                else:
                    break
            tree.insert(id_XXXX,index=END,text= tree_file_name ,image=record)
        File_record_list_str = '      '.join(File_record_list)
        File_record_list_str2 = ' ' + File_record_list_str
        OUTPUT_LIST.append([File_ID,File_type,File_Security,File_Size,
        File_record_len,File_record_num,File_record_list_str2,SFI])
        OUTPUT_sys.append([File_ID,File_type,File_Security,File_Size,
        File_record_len,File_record_num,File_record_list,SFI,S_tag,File_access])

def send_apdu(reader, apdu, recv_list, readertype=None):
    # Clear list
    recv_list[:] = []
    apdu = apdu.replace(" ", "")
    time1 = time.strftime("%Y_%m_%d %H:%M:%S", time.localtime(time.time()))
    strin1 = "Send: " + apdu 
    text.insert('insert',strin1)
    text.insert('insert','\n')
    text.insert('insert',time1)
    text.insert('insert','\n')
    result = reader.send_apdu(apdu, readertype)
    recv_list.append(result[:])
    time2 = time.strftime("%Y_%m_%d %H:%M:%S", time.localtime(time.time()))
    strin2 = "Recv: "  + result 
    text.insert('insert',strin2)
    text.insert('insert','\n')
    text.insert('insert',time2)
    text.insert('insert','\n')

def send_apducommand(reader, apdu, recv_list, readertype=None):
    send_apdu(reader, apdu, recv_list, readertype)
    if recv_list[0][0:2] == "61":
        apdu = "00C00000" + recv_list[0][2:4]
        send_apdu(reader, apdu, recv_list, readertype)
    elif recv_list[0][0:2] == "6C":
        apdu = apdu[0:8] + recv_list[0][2:4]
        send_apdu(reader, apdu, recv_list, readertype)

def connect_device():
    readername = cb.get()
    result = pcsc.connect_device(readername)
    pcsc.power_on(readertype)
    if len(result) == 0:
        text.insert('insert','ConnectDevice Failed!')
        text.insert('insert','\n')
    else:
        text.insert('insert','ConnectDevice Success...')
        text.insert('insert','\n')
        connectBtn.config(state = DISABLED)
        disconnectBtn.config(state = NORMAL)
        homeBtn.config(state = NORMAL)
        okBtn.config(state = NORMAL)
        selectBtn.config(state = NORMAL)
        GENBtn.config(state = NORMAL)
        stopBtn.config(state = NORMAL)
def disconnect_device():
    pcsc.disconnect_device()  
    disconnectBtn.config(state = DISABLED)
    connectBtn.config(state = NORMAL)
    homeBtn.config(state = DISABLED)
    okBtn.config(state = DISABLED)
    selectBtn.config(state = DISABLED)
    GENBtn.config(state = DISABLED)
    stopBtn.config(state = DISABLED)
def home_reset():
    readername = cb.get()
    pcsc.disconnect_device()
    reset_text = pcsc.connect_device(readername)
    pcsc.power_on(readertype)
    text.insert('insert',reset_text)
    text.insert('insert','\n')
    var_state.set('Ready')
def home_ok():
    apdu = entry.get()
    revc_info = []
    send_apducommand(pcsc, apdu, revc_info, readertype)
def home_GEN():
    newtree()
    probar['maximum'] = '512'
    probar['value'] = '0'
    time3 = time.strftime("%Y_%m_%d %H:%M:%S", time.localtime(time.time()))
    text.insert('insert','Search,start...')
    text.insert('insert','\n')
    text.insert('insert',time3)
    text.insert('insert','\n')
    test_3F00_EF()
    test_3F00_7FXX()
    time4 = time.strftime("%Y_%m_%d %H:%M:%S", time.localtime(time.time()))
    text.insert('insert','Search,success...  Path:  D:\File_search_tool')
    text.insert('insert','\n')
    text.insert('insert',time4)
    text.insert('insert','\n')
    var_state.set('Finish')
def enter1(event):
    var_state.set('Connect Reader')
def leave1(event):
    var_state.set('')
def enter2(event):
    var_state.set('Disconnect Reader')
def leave2(event):
    var_state.set('')
def enter3(event):
    var_state.set('Reset')
def leave3(event):
    var_state.set('')
def enter4(event):
    var_state.set('Send APDU')
def leave4(event):
    var_state.set('')
def enter5(event):
    var_state.set('Demond Search')
def leave5(event):
    var_state.set('')
def enter6(event):
    var_state.set('Fixed Search')
def leave6(event):
    var_state.set('')
def enter7(event):
    var_state.set('Stop Search')
def leave7(event):
    var_state.set('')
 
#线程   
# threads = []


def start_thread_1():
    global threads
    threads = []
    t = threading.Thread(target=home_GEN)
    threads.append(t)
    for t in threads:
        try:
            t.setDaemon(True)
            t.start()
        except RuntimeError:
            t.start()

def start_thread_2():
    global threads
    threads = []
    t = threading.Thread(target=select_window_fuc)
    threads.append(t)
    for t in threads:
        try:
            t.setDaemon(True)
            t.start()
        except RuntimeError:
            t.start()

def _async_raise(tid, exctype):

    """raises the exception, performs cleanup if needed"""

    tid = ctypes.c_long(tid)

    if not inspect.isclass(exctype):

        exctype = type(exctype)

    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))

    if res == 0:

        raise ValueError("invalid thread id")

    elif res != 1:

        # """if it returns a number greater than one, you're in trouble,

        # and you should call it again with exc=NULL to revert the effect"""

        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)

        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):

    _async_raise(thread.ident, SystemExit)

def stop():
    for t in threads:
     stop_thread(thread = t)    

#按需搜索功能窗口
def select_window():
    #建立子窗口
    global entry1
    global entry2
    global cb_top
    var_state.set('Ready')
    tl = Toplevel()
    tl.title('Select Search File Path')
    winWidth = 335
    winHeight = 125
    screenWidth = tl.winfo_screenwidth()
    screenHeight = tl.winfo_screenheight()    
    x = int((screenWidth - winWidth) / 2)
    y = int((screenHeight - winHeight) / 2)
    tl.geometry("%sx%s+%s+%s" % (winWidth, winHeight, x, y))
    frame =Frame(tl)
    frame2 =Frame(tl)
    frame3 =Frame(tl)
    label1 =Label(frame,text ='File Type',width = 10)
    label2 =Label(frame2,text='Range',width = 10)
    label3 =Label(frame2,text='-',width = 1)
    cb_top =Combobox(frame,width=15,state= 'readonly')
    cb_top['value'] = ['DF','EF']
    entry1 =Entry(frame2,width = 15)
    entry2 =Entry(frame2,width = 15)
    btn =Button(frame3,text = 'OK',width = 5,command =start_thread_2)
    frame.pack(fill =X)
    frame2.pack(fill =X)
    frame3.pack(fill =X)
    label1.pack(side = LEFT,anchor = W,padx =3,pady=3)
    cb_top.pack(side = LEFT,anchor = W,padx =3,pady=3)
    label2.pack(side = LEFT,anchor = W,padx =3,pady=3)
    entry1.pack(side = LEFT,anchor = W,padx =3,pady=3)
    label3.pack(side = LEFT,anchor = W,padx =3,pady=3)
    entry2.pack(side = LEFT,anchor = W,padx =3,pady=3)
    btn.pack(anchor = CENTER,padx =3,pady=3)
    entry1.insert('insert','0000')
    entry2.insert('insert','FFFF')
def select_window_fuc():
    newtree()
    time3 = time.strftime("%Y_%m_%d %H:%M:%S", time.localtime(time.time()))
    text.insert('insert','Search,start...')
    text.insert('insert','\n')
    text.insert('insert',time3)
    text.insert('insert','\n')
    global OUTPUT_LIST
    global OUTPUT_sys
    global judge_DF
    global tree_file_name
    global id_XXXX
    select_type = cb_top.get()
    a = entry1.get()
    b = entry2.get()
    if a == '' or b == '':
        no_search()
    else:
        a1 = '0x' + a
        b1 = '0x' + b
        a2 = int(a1,16)
        b2 = int(b1,16)
        c = int(b2) - int(a2)
        d = int(a2)
        e = int(b2) + 1
        OUTPUT_LIST = [] 
        if select_type == 'EF':
            OUTPUT_LIST.append(["File ID","File Type","File Security",'File size'
            ,'File Len' ,'File Num' ,'Content','SFI' ])
            # OUTPUT_LIST.append(['3F00','','','','','',''])   
            apdu = "00A4000402 3F00"
            tree_file_name ='3F00'
            id_XXXX = tree.insert('',index=END,text= tree_file_name ,image=closefolder)
            revc_info = []
            send_apducommand_DF(pcsc, apdu, revc_info, readertype)
            # send_apdu_common(pcsc, apdu, revc_info, readertype)
            probar['maximum'] = c
            f = 0        
            for i in range(d,e):
                f += 1
                probar['value'] = f
                a = []
                b = hex(i)
                if len(b) == 6:
                  a.append(b[-4:].upper())
                elif len(b) == 5:
                  a.append('0'+ b[-3:].upper())
                elif len(b) == 4:
                  a.append('00'+ b[-2:].upper())
                else:
                  a.append('000'+ b[-1:].upper())
                apdu = "00A4000402" + a[0]
                var_state.set('3F00/' + apdu[-4:])
                tree_file_name =apdu[-4:]
                send_apducommand_EF(pcsc, apdu, revc_info, readertype)
                window.update()
                apdu = "00A4000C02 3F00"
                send_apdu_common(pcsc, apdu, revc_info, readertype)
        elif select_type == 'DF':
                    #开始测试项
            OUTPUT_LIST.append(["File ID","File Type","File Security",'File size'
            ,'File Len' ,'File Num' ,'Content','SFI' ])
            # OUTPUT_LIST.append(['3F00','','','','','',''])

            apdu = "00A4000402 3F00"
            tree_file_name ='3F00'
            id_3F00 = tree.insert('',index=END,text= tree_file_name ,image=closefolder)
            revc_info = []
            send_apdu_common(pcsc, apdu, revc_info, readertype)
            probar['maximum'] = c
            f = 0 
            for i in range(d,e):
                name_XXXX = ''
                f += 1
                probar['value'] = f
                apdu = "00A4000C02 3F00"
                send_apdu_common(pcsc, apdu, revc_info, readertype)
                a = []
                b = hex(i)
                if len(b) == 6:
                  a.append(b[-4:].upper())
                elif len(b) == 5:
                  a.append('0'+ b[-3:].upper())
                elif len(b) == 4:
                  a.append('00'+ b[-2:].upper())
                else:
                  a.append('000'+ b[-1:].upper())
                apdu = "00A4000402" + a[0]
                var_state.set('3F00/' + apdu[-4:])
                name_XXXX = a[0]
                # print(name_XXXX)
                var_state.set('3F00/' + name_XXXX)
                send_apducommand_DF(pcsc, apdu, revc_info, readertype)
                window.update()
                if judge_DF == '78' or judge_DF ==  '38':
                    #寻找ADF下EF文件
                    id_XXXX = tree.insert(id_3F00,index=END,text= name_XXXX ,image=closefolder)
                    for i in range(0,256):
                        a = []
                        b = hex(i)
                        name_6FXX = ''
                        if len(b) == 4:
                              a.append(b[-2:].upper())
                        else:
                              a.append('0'+ b[-1:].upper())
                        
                        apdu = "00A4000402 6F" + a[0]
                        name_6FXX = '6F' + a[0]
                        tree_file_name = name_6FXX
                        var_state.set('3F00/' + name_XXXX +'/'+ name_6FXX)
                        send_apducommand_EF(pcsc, apdu, revc_info, readertype)
                        
                        apdu = "00A4000C02 3F00"
                        revc_info = []
                        send_apdu_common(pcsc, apdu, revc_info, readertype)
                        
                        apdu = "00A4000C02" + name_XXXX
                        send_apdu_common(pcsc, apdu, revc_info, readertype)
                        window.update()
                    #寻找ADF下DF文件    
                    for i in range(0,256):                
                        a = []
                        b = hex(i)
                        name_5FXX = ''
                        if len(b) == 4:
                              a.append(b[-2:].upper())
                        else:
                              a.append('0'+ b[-1:].upper())               
                        apdu = "00A4000402 5F" + a[0]
                        name_5FXX = '5F' + a[0]
                        var_state.set('3F00/' + name_XXXX +'/'+ name_5FXX)
                        send_apducommand_DF(pcsc, apdu, revc_info, readertype)
                        window.update()
                        if judge_DF == '78' or judge_DF ==  '38':
                            tree_file_name = name_5FXX
                            id_XXXX = tree.insert(id_XXXX,index=END,text= tree_file_name ,image=closefolder)
                            for i in range(0,256):
                                a = []
                                b = hex(i)
                                name_4FXX = ''
                                if len(b) == 4:
                                      a.append(b[-2:].upper())
                                else:
                                      a.append('0'+ b[-1:].upper())
                                apdu = "00A4000402 4F" + a[0]
                                tree_file_name =apdu[-4:]
                                name_4FXX = '4F' + a[0]
                                var_state.set('3F00/' + name_XXXX +'/'+ name_5FXX +'/'+ name_4FXX)
                                send_apducommand_EF(pcsc, apdu, revc_info, readertype)
                                
                                apdu = "00A4000C02 3F00"
                                revc_info = []
                                send_apdu_common(pcsc, apdu, revc_info, readertype)
                                
                                apdu = "00A4000C02" + name_XXXX
                                send_apdu_common(pcsc, apdu, revc_info, readertype)
                                
                                apdu = "00A4000C02" + name_5FXX
                                send_apdu_common(pcsc, apdu, revc_info, readertype)
                                window.update()
                        else:
                            pass
                else:
                     pass
        else:
            Bug()
        key = OUTPUT_LIST
        time1 = time.strftime("%H_%M", time.localtime(time.time()))
        csv_file_order_name = 'File_Search('+ time1 + ').csv'
        csv_file_order = 'D:/File_search_tool' + '/' + csv_file_order_name  
        with open(csv_file_order,'w',newline='') as csv_file:
            writer = csv.writer(csv_file)
            for i in range(len(key)):
        # 写入多行用writerows
                writer.writerows([key[i]])
    var_state.set('Finish')
    time4 = time.strftime("%Y_%m_%d %H:%M:%S", time.localtime(time.time()))
    text.insert('insert','Search,success...    Path:  D:\File_search_tool')
    text.insert('insert','\n')
    text.insert('insert',time4)
    text.insert('insert','\n')
        

    
def newFile():
    text.delete('1.0', END)

def newtree():    
    x=tree.get_children()
    for item in x:
        tree.delete(item)
    
def saveAsFile():
    textContent = text.get('1.0',END)
    filename = asksaveasfilename(defaultextension = '.txt')
    if filename =='':
        return
    with open(filename,'w') as output:
        output.write(textContent)
 
def no_search():
    messagebox.showinfo('Warning','请输入搜索范围')

def Bug():
    messagebox.showinfo('Warning','有Bug')        
        
def Help():
    messagebox.showinfo('Help','待补充')

def About():
    messagebox.showinfo('About','开发:Roy，仅供内部使用！') 


#定义主程序
def test_3F00_EF():
    #开始测试项
    global OUTPUT_LIST
    global OUTPUT_sys
    global id_XXXX
    global tree_file_name
    global id_3F00
    #3F00下的7FXX项
    OUTPUT_LIST.append(["File ID","File Type","File Security",'File size'
        ,'File Len' ,'File Num' ,'Content','SFI' ])
    apdu = "00A4000402 3F00"
    revc_info = []
    # send_apdu_common(pcsc, apdu, revc_info, readertype)
    send_apducommand_DF(pcsc, apdu, revc_info, readertype)
    # #验证ADM指令
    # apdu = "00 20 00 0a 08 3733433244374630"
    # send_apdu_common(pcsc, apdu, revc_info, readertype)
    tree_file_name = '3F00'
    id_3F00 = id_XXXX = tree.insert('',index=END,text= tree_file_name ,image=closefolder)  

    # OUTPUT_LIST.append(["File ID","File Type","File Security",'File size'
    #         ,'File Len' ,'File Num' ,'Content','SFI' ])
    # OUTPUT_LIST.append(['3F00','','','','','',''])
    # 3F00下EF-2FXX
    # send_apdu_common(pcsc, apdu, revc_info, readertype)   
    for i in range(0,256):
        probar['value'] = i+1
        a = []
        b = hex(i)
        if len(b) == 4:
              a.append(b[-2:].upper())
        else:
              a.append('0'+ b[-1:].upper())
        apdu = "00A4000402 2F" + a[0]
        var_state.set('3F00/' + apdu[-4:])
        tree_file_name = apdu[-4:]
        window.update()
        send_apducommand_EF(pcsc, apdu, revc_info, readertype)


        
        apdu = "00A4000C02 3F00"
        send_apdu_common(pcsc, apdu, revc_info, readertype)
    
    
    # send_apdu_common(pcsc, apdu, revc_info, readertype)   
    # for i in range(0,65536):
    #     a = []
    #     b = hex(i)
    #     if len(b) == 6:
    #           a.append(b[-4:].upper())
    #     elif len(b) == 5:
    #         a.append('0'+ b[-3:].upper())
    #     elif len(b) == 4:
    #         a.append('00'+ b[-2:].upper())
    #     else:
    #           a.append('000'+ b[-1:].upper())
    #     apdu = "00A40004" + a[0]
    #     var_state.set('3F00/' + a[0])
    #     window.update()
    #     send_apducommand_EF(pcsc, apdu, revc_info, readertype)

        
    #     apdu = "00A4000C02 3F00"
    #     send_apdu_common(pcsc, apdu, revc_info, readertype)
        
    # key = OUTPUT_LIST
    # csv_file_order = 'D:/个人化工具/列表数据.csv'   
    # with open(csv_file_order,'w',newline='') as csv_file:
    #     writer = csv.writer(csv_file)
    #     for i in range(len(key)):
    #         writer.writerows([key[i]])
    return 0


#查询3F00下其他7FXX文件下所包含文件的文件夹
def test_3F00_7FXX():

    #开始测试项
    global OUTPUT_LIST 
    global judge_DF
    global id_XXXX
    global tree_file_name
    global id_3F00
    apdu = "00A4000C02 3F00"
    revc_info = []
    send_apdu_common(pcsc, apdu, revc_info, readertype)

    
    # #验证ADM指令
    # apdu = "00 20 00 0a 08 3733433244374630"
    # send_apdu_common(pcsc, apdu, revc_info, readertype)
    
    
    for i in range(0,256):
        probar['value'] = i+256
        apdu = "00A4000C02 3F00"
        revc_info = []
        send_apdu_common(pcsc, apdu, revc_info, readertype)
        name_7FXX = ''
        a = []
        b = hex(i)
        if len(b) == 4:
              a.append(b[-2:].upper())
        else:
              a.append('0'+ b[-1:].upper())
        apdu = "00A4000402 7F" + a[0]
        name_7FXX = '7F' + a[0]
        var_state.set('3F00/' + name_7FXX)
        send_apducommand_DF(pcsc, apdu, revc_info, readertype)
        window.update()
        if judge_DF == '78' or judge_DF ==  '38':
            tree_file_name = name_7FXX
            id_XXXX = tree.insert(id_3F00,index=END,text= tree_file_name ,image=closefolder)    
            #寻找ADF下EF文件
            for i in range(0,256):
                a = []
                b = hex(i)
                name_6FXX = ''
                if len(b) == 4:
                      a.append(b[-2:].upper())
                else:
                      a.append('0'+ b[-1:].upper())
                
                apdu = "00A4000402 6F" + a[0]
                name_6FXX = '6F' + a[0]
                tree_file_name = name_6FXX
                var_state.set('3F00/' + name_7FXX +'/'+ name_6FXX)
                send_apducommand_EF(pcsc, apdu, revc_info, readertype)
                
                apdu = "00A4000C02 3F00"
                revc_info = []
                send_apdu_common(pcsc, apdu, revc_info, readertype)
                
                apdu = "00A4000C02" + name_7FXX
                send_apdu_common(pcsc, apdu, revc_info, readertype)
                window.update()
            #寻找ADF下DF文件    
            for i in range(0,256):                
                a = []
                b = hex(i)
                name_5FXX = ''
                if len(b) == 4:
                      a.append(b[-2:].upper())
                else:
                      a.append('0'+ b[-1:].upper())               
                apdu = "00A4000402 5F" + a[0]
                name_5FXX = '5F' + a[0]
                var_state.set('3F00/' + name_7FXX +'/'+ name_5FXX)
                send_apducommand_DF(pcsc, apdu, revc_info, readertype)
                window.update()
                if judge_DF == '78' or judge_DF ==  '38':
                    tree_file_name = name_5FXX
                    id_XXXX = tree.insert(id_XXXX,index=END,text= tree_file_name ,image=closefolder)    
                    for i in range(0,256):
                        a = []
                        b = hex(i)
                        name_4FXX = ''
                        if len(b) == 4:
                              a.append(b[-2:].upper())
                        else:
                              a.append('0'+ b[-1:].upper())
                        apdu = "00A4000402 4F" + a[0]
                        name_4FXX = '4F' + a[0]
                        tree_file_name = name_4FXX
                        var_state.set('3F00/' + name_7FXX +'/'+ name_5FXX +'/'+ name_4FXX)
                        send_apducommand_EF(pcsc, apdu, revc_info, readertype)
                        
                        apdu = "00A4000C02 3F00"
                        revc_info = []
                        send_apdu_common(pcsc, apdu, revc_info, readertype)
                        
                        apdu = "00A4000C02" + name_7FXX
                        send_apdu_common(pcsc, apdu, revc_info, readertype)
                        
                        apdu = "00A4000C02" + name_5FXX
                        send_apdu_common(pcsc, apdu, revc_info, readertype)
                        window.update()
                else:
                    pass
        else:
             pass


    key = OUTPUT_LIST
    # print(key)
    time1 = time.strftime("%H_%M", time.localtime(time.time()))
    csv_file_order_name = 'File_search('+ time1 + ').csv'
    csv_file_order = 'D:/File_search_tool/'  + csv_file_order_name   
    with open(csv_file_order,'w',newline='') as csv_file:
        writer = csv.writer(csv_file)
        for i in range(len(key)):
        # 写入多行用writerows
            writer.writerows([key[i]])


window = Tk()
window.title('File_System_read')
winWidth = 850
winHeight = 450
# 获取屏幕分辨率
screenWidth = window.winfo_screenwidth()
screenHeight = window.winfo_screenheight()
 
x = int((screenWidth - winWidth) / 2)
y = int((screenHeight - winHeight) / 2)
 

# 设置窗口初始位置在屏幕居中
window.geometry("%sx%s+%s+%s" % (winWidth, winHeight, x, y))
#获取路径
prog_call = sys.argv[0]
prog_location = os.path.split(prog_call)[0]
#树状结构

def update_tree( tree):
    a=[]
    for item_A in OUTPUT_sys:
        a.append(item_A[0])
    sel = tree.selection()
    b = tree.parent(sel)
    # print(b)
    if b == '':
        c = 0
    else:    
        c = a.index(tree.item(b)['text'])
    # print(c)
    # print(tree.item(sel))
    # print(tree.item(sel)['text'])
    for item in OUTPUT_sys[c:]:
        # 有时会找到重复的选项，用Break语句打断
        if tree.item(sel)['text'] == item[0]:
            # if tree.item(sel)['text'][:2] in ['5F','3F','7F']:
                clear_entry_info()
                a_entry_str.set(item[0])
                b_entry_str.set(item[3])
                c_entry_str.set(item[9])
                d_entry_str.set(item[7])
                e_entry_str.set(item[4])
                f_entry_str.set(item[1])
                g_entry_str.set(item[5])
                h_entry_str.set(item[8])
                i_entry_str.set(item[2])
                tree_text =0
                for item in item[6]:
                    tree_text += 1
                    tree_value= item
                    tree_basic.insert('',index=END,text=tree_text,values=tree_value)               
                break
        else:
           pass

def clear_entry_info():
    a_entry.delete(0,END)
    b_entry.delete(0,END) 
    c_entry.delete(0,END) 
    d_entry.delete(0,END) 
    e_entry.delete(0,END) 
    f_entry.delete(0,END) 
    g_entry.delete(0,END)
    h_entry.delete(0,END)
    i_entry.delete(0,END)
    x=tree_basic.get_children()
    for item in x:
        tree_basic.delete(item)        
            
            
            
def tree_open( tree):
    sel = tree.selection()
    # print(sel)
    if tree.item(sel)['text'][:2] in ['5F','3F','7F']:
        tree.item(sel,image=openfolder)
    else:
        pass


def tree_close(tree):
    sel = tree.selection()
    if tree.item(sel)['text'][:2] in ['5F','3F','7F']:
        tree.item(sel,image=closefolder)
    else:
        pass


tree = Treeview(window)
y_scrollbar = Scrollbar(window)

    
tree.bind('<<TreeviewSelect>>',
             lambda e :update_tree(tree))
tree.bind('<<TreeviewOpen>>',
             lambda e :tree_open(tree))
tree.bind('<<TreeviewClose>>',
             lambda e :tree_close(tree))    

photo_loc_close = os.path.join(prog_location,"./images/closefolder.gif")
closefolder = PhotoImage(file=photo_loc_close)
photo_loc_open = os.path.join(prog_location,"./images/openfolder.gif")
openfolder = PhotoImage(file=photo_loc_open)
photo_loc_BIN = os.path.join(prog_location,"./images/BIN.gif")
BIN = PhotoImage(file=photo_loc_BIN)
photo_loc_record = os.path.join(prog_location,"./images/record.gif")
record = PhotoImage(file=photo_loc_record)

# asia =['a','b','c']
tree.column('#0')
tree.heading('#0',text='File System')
# idAsia = tree.insert('',index=END,text='Asia',image=closefolder)
# for country in asia:
#     tree.insert(idAsia,index=END,text=country,image=closefolder)

# for country in asia:
#     tree.insert(idAsia,index=END,text=country,image=BIN)
    


cb_var = StringVar()
entry_var = StringVar()
var_state = StringVar()
a_entry_str = StringVar()
b_entry_str = StringVar()
c_entry_str = StringVar()
d_entry_str = StringVar()
e_entry_str = StringVar()
f_entry_str = StringVar()
g_entry_str = StringVar()
h_entry_str = StringVar()
i_entry_str = StringVar()


#建立最上层菜单
menubar = Menu(window)
#建立子菜单,tearoff设置为False时，没有分隔虚线
filemenu = Menu(menubar,tearoff = False)
helpmenu = Menu(menubar,tearoff = False)
menubar.add_cascade(label = 'File',menu = filemenu)
menubar.add_cascade(label='Help',menu = helpmenu)
menubar.add_command(label = 'Exit',command = window.destroy)

#添加子菜单的可选项
filemenu.add_command(label = 'New File',command = newFile)
filemenu.add_command(label = 'Save as File',command = saveAsFile)
helpmenu.add_command(label = 'About',command = About)
helpmenu.add_separator()
helpmenu.add_command(label = 'Help',command = Help)


#建立工具栏和工具栏按钮
toolbar = Frame(window,relief =RAISED,borderwidth = 2)
statebar = Frame(window,relief =GROOVE,borderwidth = 2)

#下拉选项框
cb =Combobox(toolbar,textvariable = cb_var,width=20,state= 'readonly')

#进度条
probar = Progressbar(statebar,length = '200',maximum = '512',value = '0')
#输入框
entry = Entry(toolbar,textvariable = entry_var,width = 35)


tabControl = Notebook(window)
tab2 = Frame(tabControl)        # 创建选项卡（tab）
tabControl.add(tab2, text='Text Info')  
tab1 = Frame(tabControl)        # 创建选项卡（tab）
tabControl.add(tab1, text='Basic Information')
tab3 = Frame(tabControl)        # 创建选项卡（tab）
tabControl.add(tab3, text='Access Condition')  


Basic_info = LabelFrame(tab1,text='Info')
Basic_info.pack(anchor =NW,padx =6,pady=6)
#第一行

list1 = Frame(Basic_info)
list1.pack(anchor =W,padx =3,pady=3)

a_label = Label(list1, text="ID:    ")
a_label.pack(side= LEFT,padx =3,pady=3)
a_entry =Entry(list1,width =18,textvariable = a_entry_str)
a_entry.pack(side= LEFT,padx =3,pady=3)

b_label = Label(list1, text="  FileSize:       ")
b_label.pack(side= LEFT,padx =3,pady=3)
b_entry =Entry(list1,width =10,textvariable = b_entry_str)
b_entry.pack(side= LEFT,padx =3,pady=3)

c_label = Label(list1, text="  Accessibility:  ")
c_label.pack(side= LEFT,padx =3,pady=3)
c_entry =Entry(list1,width =14,textvariable = c_entry_str)
c_entry.pack(side= LEFT,padx =3,pady=3)
#第二行
list2 = Frame(Basic_info)
list2.pack(anchor =W,padx =3,pady=3)

d_label = Label(list2, text="SFI:   ")
d_label.pack(side= LEFT,padx =3,pady=3)
d_entry =Entry(list2,width =18,textvariable = d_entry_str)
d_entry.pack(side= LEFT,padx =3,pady=3)

e_label = Label(list2, text="  RecordSize: ")
e_label.pack(side= LEFT,padx =3,pady=3)
e_entry =Entry(list2,width =10,textvariable = e_entry_str)
e_entry.pack(side= LEFT,padx =3,pady=3)


#第二行
list2 = Frame(Basic_info)
list2.pack(anchor =W,padx =3,pady=3)

f_label = Label(list2, text="Type:")
f_label.pack(side= LEFT,padx =3,pady=3)
f_entry =Entry(list2,width =18,textvariable = f_entry_str)
f_entry.pack(side= LEFT,padx =3,pady=3)

g_label = Label(list2, text="  RecordNum:")
g_label.pack(side= LEFT,padx =3,pady=3)
g_entry =Entry(list2,width =10,textvariable = g_entry_str)
g_entry.pack(side= LEFT,padx =3,pady=3)

#记录输入框
list_basic = Frame(Basic_info)
list_basic.pack(expand =True,fill =BOTH,padx =5,pady=5)
xt_scrollbar = Scrollbar(list_basic,orient = HORIZONTAL)
yt_scrollbar = Scrollbar(list_basic)
xt_scrollbar.pack(side = BOTTOM,fill =X)
yt_scrollbar.pack(side = RIGHT,fill =Y)
tree_basic = Treeview(list_basic,columns=('Value'))
tree_basic.heading('#0',text='No.')
tree_basic.heading('Value',text='Value')
tree_basic.column("#0",minwidth=0,width=80, stretch=NO)
tree_basic.column('Value',minwidth=0,width=600,stretch=NO)
tree_basic.pack(expand =True,fill =BOTH)
xt_scrollbar.config(command=tree_basic.xview)
yt_scrollbar.config(command=tree_basic.yview)
tree_basic.configure(xscrollcommand = xt_scrollbar.set)
tree_basic.configure(yscrollcommand = yt_scrollbar.set)




#接口状态选项
Access_info = LabelFrame(tab3,text='Info')
Access_info.pack(anchor =NW,padx =6,pady=6)
#第一行
list1 = Frame(Access_info)
list1.pack(anchor =W,padx =3,pady=3)

h_label = Label(list1, text="Security Tag:    ")
h_label.pack(side= LEFT,padx =3,pady=3)
h_entry =Entry(list1,width =18,textvariable = h_entry_str)
h_entry.pack(side= LEFT,padx =3,pady=3)

#第二行
list2 = Frame(Access_info)
list2.pack(anchor =W,padx =3,pady=3)

i_label = Label(list2, text="Security Atr:     ")
i_label.pack(side= LEFT,padx =3,pady=3)
i_entry =Entry(list2,width =18,textvariable = i_entry_str)
i_entry.pack(side= LEFT,padx =3,pady=3)

#文本
text = Text(tab2,wrap = NONE)
xscrollbar = Scrollbar(tab2,orient = HORIZONTAL)
yscrollbar = Scrollbar(tab2)


#图片地址


photo_loc_dis = os.path.join(prog_location,"./images/disconnect.gif")
disconnectGif = PhotoImage(file=photo_loc_dis)
disconnectBtn =Button(toolbar,image = disconnectGif,command = disconnect_device,state = DISABLED)
photo_loc_con = os.path.join(prog_location,"./images/connect.gif")
connectGif = PhotoImage(file=photo_loc_con)
connectBtn =Button(toolbar,image = connectGif,command = connect_device)
photo_loc_home = os.path.join(prog_location,"./images/home.gif")
homeGif = PhotoImage(file=photo_loc_home)
homeBtn =Button(toolbar,image = homeGif,command = home_reset,state = DISABLED)
photo_loc_sel = os.path.join(prog_location,"./images/select.gif")
selectGif = PhotoImage(file=photo_loc_sel)
selectBtn =Button(toolbar,command = select_window,image = selectGif,state = DISABLED)
photo_loc_ok = os.path.join(prog_location,"./images/ok.gif")
okGif = PhotoImage(file=photo_loc_ok)
okBtn =Button(toolbar,command = home_ok,image = okGif,state = DISABLED)
photo_loc_GEN = os.path.join(prog_location,"./images/GEN.gif")
GENGif = PhotoImage(file=photo_loc_GEN)
GENBtn =Button(toolbar,command = start_thread_1,image =GENGif,state = DISABLED)
photo_loc_stop = os.path.join(prog_location,"./images/stop.gif")
stopGif = PhotoImage(file=photo_loc_stop)
stopBtn =Button(toolbar,command = stop,image =stopGif,state = DISABLED)

Statelab = Label(statebar,textvariable = var_state)

cb.pack(side=LEFT,padx =3,pady=3)
connectBtn.pack(side=LEFT,padx =3,pady=3)
disconnectBtn.pack(side=LEFT,padx =3,pady=3)
homeBtn.pack(side=LEFT,padx =3,pady=3)
selectBtn.pack(side=LEFT,padx =3,pady=3)
entry.pack(side = RIGHT,padx =3,pady=3)
okBtn.pack(side = RIGHT,padx =3,pady=3)
GENBtn.pack(side = LEFT,padx =3,pady=3)
stopBtn.pack(side = LEFT,padx =3,pady=3)
toolbar.pack(side=TOP,fill = X)
statebar.pack(side=BOTTOM,fill =X)

tree.pack(side=LEFT,fill=Y)
y_scrollbar.pack(side = LEFT,fill =Y)
xscrollbar.pack(side = BOTTOM,fill =X)
yscrollbar.pack(side = RIGHT,fill =Y)
text.pack(side = RIGHT,expand =True,fill =BOTH)
tabControl.pack(fill="both",expand =True)  # pack 以使其可见
Statelab.pack(side = LEFT,padx =3,pady=3)
probar.pack(side = RIGHT,padx =3,pady=3)
xscrollbar.config(command=text.xview)
yscrollbar.config(command=text.yview)
y_scrollbar.config(command=tree.yview)
text.configure(xscrollcommand = xscrollbar.set)
text.configure(yscrollcommand = yscrollbar.set)
tree.configure(yscrollcommand = y_scrollbar.set)
connectBtn.bind('<Enter>',enter1)
connectBtn.bind('<Leave>',leave1)
disconnectBtn.bind('<Enter>',enter2)
disconnectBtn.bind('<Leave>',leave2)
homeBtn.bind('<Enter>',enter3)
homeBtn.bind('<Leave>',leave3)
okBtn.bind('<Enter>',enter4)
okBtn.bind('<Leave>',leave4)
selectBtn.bind('<Enter>',enter5)
selectBtn.bind('<Leave>',leave5)
GENBtn.bind('<Enter>',enter6)
GENBtn.bind('<Leave>',leave6)
stopBtn.bind('<Enter>',enter7)
stopBtn.bind('<Leave>',leave7)


#智能卡取名字   
pcsc = PcscReader()
result = pcsc.get_pcsc_readerlist()
readername_all = result.split(";")
cb['value'] = readername_all[:-1]
readertype = 1 




#显示菜单对象
window.config(menu = menubar)

window.mainloop()
