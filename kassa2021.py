# coding: cp1251
ver = " v7 [14/02/2021 09:00]"

import traceback
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import configparser
import serial
import threading
import logging
import subprocess
import psutil
from time import time, localtime, strftime
from datetime import datetime
import platform
import requests
import time

from kdef2021 import fid
from kdef2021 import int2bit
from kdef2021 import bit2error
from kdef2021 import rus
from kdef2021 import add_check_sum
from kdef2021 import new_str
from kdef2021 import kIn
from kdef2021 import kOut
from kdef2021 import byte_to_str
from kdef2021 import str_to_byte
from kdef2021 import cod00
from kdef2021 import cod02
from kdef2021 import cod04
from kdef2021 import txthelp
import socket
import os
from threading import Thread
import sys
from datetime import datetime

from command import command

bigipclient = ''

try:
    config = configparser.ConfigParser()
    config.read('kassa2021.ini')
except:
    print('ОШИБКА ЧТЕНИЯ ini ФАЙЛА! ПРОГРАММА НЕ МОЖЕТ ДАЛЬШЕ РАБОТАТЬ!!!!')
    print('исправьте ini файл - и запустите заново')
    while True:
        input()


#---- блок IP SOCK --------------
# отправка данных на кассу или в IP
def pportinwrite(s):
    global portin
    if fServer:
        #print(type(s))
        #portin.write(str_to_byte(s))
        portin.write(s)
    elif fClient:
        sock.send(s)
        print(s)
    else:
        print("Ты сервер или клиент? внеси данные в конфигурацию!")


# сервер.приём сообщений и пересылка в порт
def f(num, conn1, addr1):
        global client,pport,gport,bigipclient
        #try:
        while True:
            data = conn1.recv(2024)
            if data != b'':
                ipclient = f"{conn1.getpeername()}"
                strsend = data #.decode('utf-8') #f"{data}"[2:-1]
                # print(f"{conn1.getpeername()}- {(data.decode())}=")
                ##0402print(data)
                ##0402print(kIn(data)['id'])
                ##0402print(kIn(data)['cod'])
                ##0402print(byte_to_str(kIn(data)['id']))
                ##0402print(byte_to_str(kIn(data)['cod']))


                print(f"7>K{ipclient}- {strsend}=")
                logging.info(f"7>K{ipclient}")
                # добавить в список команд и отослать на порт
                # conn.send('Ok'.encode())
                #serverclient(ipclient, f"ok:{strsend}")
                pport = 7
                portin.write(data)
                bigipclient = ipclient

                #1202print(f"{byte_to_str(kIn(strsend)['id'])}{byte_to_str(kIn(strsend)['cod'])}")

                #1202gport.update([(f"{byte_to_str(kIn(strsend)['id'])}{byte_to_str(kIn(strsend)['cod'])}", f"{ipclient}")])  # 270121
                #1202print(f"gport:{gport}")
                #pportinwrite(f"{strsend}")
                # требуется проверка свободности кассы 280121

        ##except:
        #   print('Отключили...')
        #    client.remove(conn1)

# сервер2клиент
# сервер отвечает клиенту
def serverclient(ipclient, strsend):
    global client
    for c in client:
        try:
            if str(c.getpeername()) == ipclient:
                #0402print('ответ:',strsend)
                c.send(strsend) #                c.send(strsend.encode())
                #print(f"<{strsend}")
        except:
            print(f"удаляем поток {c}")
            client.pop(c)

def serverwait():
    sock = socket.socket()
    sock.bind(('', ipport))
    sock.listen(max)
    nn = 0
    while True:
        nn += 1
        conn, addr = sock.accept()
        print(f"Новое подключение n:{nn} conn:{conn} addr:{addr}")
        logging.debug(f"Новое подключение n:{nn} conn:{conn} addr:{addr}")
        client.append(conn)
        #conn.send('Соединение с сервером установлено'.encode())
        thread10 = Thread(target=f, args=(nn, conn, addr,))
        thread10.start()

# получение данных клиентом для CLIENT
def connectClient():
    global sock
    try:
        sock = socket.socket()
        sock.connect((ip, ipport))
        while True:
            data: bytes = sock.recv(1024)
            #print(data)
            # определить заказчика, пока отсылаем в 1 порт !!!!!
            print(f"> {data}")
            kk = data.rfind(b'\x02')
            if kk==0:
                portout1.write(data)
            else:
                portout1.write(data[:kk])
                portout1.write(data[kk:])

            #data = data.decode()
            #time.sleep(3)
    except:
        print("другая ошибка")
        time.sleep(3)
        sock.close()
        connectClient()


# Поток получения информации из ККТ
def thread_fromKKT(name):  # из KKT получаем
    global pport,txtpost,wait, last_cod

    print('Проверка связи с кассой...')
    while True:
        # if wait == False:
        ###print(' я снова здесь')

        # из ККТ ========
        # --------- блок получения информации ---------------
        bytes_to_read = ''
        bytes_to_read = portin.read(1)  # считываем байт, если
        if bytes_to_read == b'\x06':  #
            print("\t\t... касса ответила на запрос - работает\n", "- " * 40)
            # portin.write(bytes_to_read)
        else:
            bytes_to_read += portin.read_until(b"\x03")
            ###print(bytes_to_read)
            bytes_to_read += portin.read(2)
            ###print(bytes_to_read)
            # --------- блок получения информации ---------------
            ###print(bytes_to_read.hex())
            kOut1 = kOut(bytes_to_read)
            bts = byte_to_str(kOut1['data']).split('\x1c')
            bts1 = [str(str_to_byte(btsx), 'cp866') for btsx in bts]

            # print(f"K>{pport}: ", [f'{r}:{kOut1[r]}' for r in ['id', 'cod', 'error']], data: f'{bts}')
            txtprint = f" K>{pport}: {[f'{r}:{kOut1[r]}' for r in ['id', 'cod', 'error']]} data: {bts1}"
            print(txtprint)
            logging.info(txtprint) #.encode('utf-8-sig').decode('cp-1251')
            logging.debug(f" K>{pport} : {kOut1}")
            logging.debug(f" K>{pport} : bytes_to_read:{bytes_to_read}")

            # txtpost += " ".join(f"K>{pport}: " , [f'{r}:{kOut1[r]}' for r in ['id', 'cod', 'error']] , f'{pbts}')
            # print(f"kOut1:{kOut1['data']}\tbts:{bts}")
            s = datetime.strftime(datetime.now(), "%H:%M:%S")

            if pport == 1:
                portout1.write(bytes_to_read)
            elif pport == 2:
                portout2.write(bytes_to_read)
            elif pport == 3:  # работа с кассой из консоли
                pass
            #    print("... работа с кассой из консоли ...")
            #    # print(f"K>{pport}: ", [f'{i}:{kOut1[i]}' for i in ['id', 'cod', 'error', 'data']])
            #    print(
            #        f"{s} K>{pport}: ID:{byte_to_str(kOut1['id'])} COD:{byte_to_str(kOut1['cod'])} ERROR:{byte_to_str(kOut1['error'])}  DATA:{bts}")  # for i in ['id', 'cod', 'error', 'data']])")

            elif pport == 4:  # работа с POST
                # self.wfile.write(bytes(s, "utf-8"))
                # tpost =(f"K>{pport}: ", [f'{i}:{kOut1[i]}' for i in ['id', 'cod', 'error', 'data']])
                # 110121 tpost = f"K>{pport}: ID:{byte_to_str(kOut1['id'])} COD:{byte_to_str(kOut1['cod'])} ERROR:{byte_to_str(kOut1['error'])}  DATA:{bts}"  # for i in ['id', 'cod', 'error', 'data']])"
                # 110121 txtpost += f"{s} {tpost}\n<BR>"
                # 110121 print(f"{byte_to_str(kOut1['id'])} = {last_cod}")
                if byte_to_str(kOut1['id']) == last_cod:  # b'31':
                    wait = False
                # print(f"txtpost:{txtpost}")

            elif pport == 5:  # работа с POST
                # self.wfile.write(bytes(s, "utf-8"))
                # tpost =(f"K>{pport}: ", [f'{i}:{kOut1[i]}' for i in ['id', 'cod', 'error', 'data']])
                # 110121tpost = f"K>{pport}: ID:{byte_to_str(kOut1['id'])} COD:{byte_to_str(kOut1['cod'])} ERROR:{byte_to_str(kOut1['error'])}  DATA:{bts}"  # for i in ['id', 'cod', 'error', 'data']])"
                # 110121txtpost += f"{s} {tpost}\n<BR>"
                # 110121print(f"{byte_to_str(kOut1['id'])} = {last_cod}")
                if byte_to_str(kOut1['id']) == last_cod:  # b'31':
                    wait = False
                # print(f"txtpost:{txtpost}")
            elif pport == 7:  # работа с POST
                #1202 gp = gport.pop(f"{byte_to_str(kOut1['id'])}{byte_to_str(kOut1['cod'])}", None)  # 270121
                gp = bigipclient
                serverclient(gp, bytes_to_read)
                print(bytes_to_read)

            else:
                print("ERROR PORT!!!!")
                logging.error("ERROR PORT!!!!")
            '''
            if kOut1['cod'] == b'00':
                cod00(bts)
            if kOut1['cod'] == b'02':
                cod02(bts)
            if kOut1['cod'] == b'04':
                cod04(bts)
            '''
            # cod02(bts)

        # wait = True
        ###print('закончил передачу')


#
# Поток получения информация из Порта 1
#
def thread_com1(name):
    global pport, txtpost, gport

    while True:
        try:
            bytes_to_read = portout1.read(1)  # считываем байт, если
            if bytes_to_read == b'\x05':  #
                print("1>Проверка связи")
                logging.info(" 1>K: Проверка связи(автоответ)")
                portout1.write(b'\x06')  # portin.write(bytes_to_read)
            elif bytes_to_read == b'\x0A':  #
                print("1>перевод строки")
                pportinwrite(bytes_to_read)
            else:
                bytes_to_read += portout1.read_until(b"\x03")
                bytes_to_read += portout1.read(2)
                kIn1 = kIn(bytes_to_read)
                bts = byte_to_str(kIn1['data']).split('\x1c')

                # 11/01/21 внести изменения в данные при неправильных
                # коррекция чека для старых драйверов 1с
                #
                if (len(bts) < 5) and kIn1['cod'] == b'30' and bts[0] == '2':
                    # пересобрать строку отсылки
                    bytes_to_read = new_str(byte_to_str(kIn1['id']), byte_to_str(kIn1['cod']),
                                            [2, bts[1], bts[2], 0, 1])
                    kIn1 = kIn(bytes_to_read)
                    bts = byte_to_str(kIn1['data']).split('\x1c')

                if (len(bts) < 8 ) and kIn1['cod'] == b'42':
                    # пересобрать строку отсылки
                    pr_sposob = 4  # 4 - Полный расчет
                    pr_ras = ""
                    tova = str(str_to_byte(bts[0]), 'cp866')
                    if tova[0:6] == '[Отд1]':
                        pr_ras = 4  #Платёж
                    if tova[0:6] == '[Отд2]':
                        pr_ras = 1  #Товар
                    if tova[0:6] == '[Отд3]':
                        pr_ras = 4  #Товар

                    bytes_to_read = new_str(byte_to_str(kIn1['id']), byte_to_str(kIn1['cod']),
                        [bts[0], bts[1], bts[2], bts[3], 3, bts[5], 1, 0, "", "0.000", pr_sposob,  pr_ras ])
                    kIn1 = kIn(bytes_to_read)
                    bts = byte_to_str(kIn1['data']).split('\x1c')
                # конец блока

                # перекодировка данных в читаемый текст для вывода и лога
                bts1 = [str(str_to_byte(btsx), 'cp866') for btsx in bts]

                #portin.write(bytes_to_read)
                pportinwrite(bytes_to_read) #2801
                pport = 1

                #0802txtprint = f" 1>K: {[f'{r}:{byte_to_str(kIn1[r])}' for r in ['id', 'cod']]} data: {bts1}"
                txtprint = f" 1>K: {[f'{r}:{(kIn1[r])}' for r in ['id', 'cod']]} data: {bts1}"
                #0802print(txtprint)
                logging.info(txtprint)
                logging.debug(f" 1>K: {kIn1}")
                logging.debug(f" 1>K: bytes_to_read: {bytes_to_read}")

        except:
            print(f"Порт1 ОШИБКА :{traceback.format_exc()} в модуле получения данных. ")
            logging.error(f"Порт1 Ошибка {traceback.format_exc()} в модуле получения данных. ")


# Поток получения информация из Порта 2
def thread_com2(name):
    global pport, txtpost

    while True:
        try:
            bytes_to_read = portout2.read(1)  # считываем байт, если
            if bytes_to_read == b'\x05':  #
                print("2>Проверка связи")
                logging.info(" 2>K: Проверка связи(автоответ)")
                portout2.write(b'\x06')  # portin.write(bytes_to_read)
            elif bytes_to_read == b'\x0A':  #
                print("2>перевод строки")
                pportinwrite(bytes_to_read)
            else:
                bytes_to_read += portout2.read_until(b"\x03")
                bytes_to_read += portout2.read(2)
                kIn2 = kIn(bytes_to_read)
                bts = byte_to_str(kIn2['data']).split('\x1c')

                # 11/01/21 внести изменения в данные при неправильных
                # коррекция чека для старых драйверов 1с
                #
                if (len(bts) < 5) and kIn2['cod'] == b'30' and bts[0] == '2':
                    # пересобрать строку отсылки
                    bytes_to_read = new_str(byte_to_str(kIn2['id']), byte_to_str(kIn2['cod']),
                                            [2, bts[1], bts[2], 0, 1])
                    kIn2 = kIn(bytes_to_read)
                    bts = byte_to_str(kIn2['data']).split('\x1c')

                if (len(bts) < 8 ) and kIn2['cod'] == b'42':
                    # пересобрать строку отсылки
                    pr_sposob = 4  # 4 - Полный расчет
                    pr_ras = ""
                    tova = str(str_to_byte(bts[0]), 'cp866')
                    if tova[0:6] == '[Отд1]':
                        pr_ras = 4  #Платёж
                    if tova[0:6] == '[Отд2]':
                        pr_ras = 1  #Товар
                    if tova[0:6] == '[Отд3]':
                        pr_ras = 4  #Товар

                    bytes_to_read = new_str(byte_to_str(kIn2['id']), byte_to_str(kIn2['cod']),
                        [bts[0], bts[1], bts[2], bts[3], 3, bts[5], 1, 0, "", "0.000", pr_sposob,  pr_ras ])
                    kIn2 = kIn(bytes_to_read)
                    bts = byte_to_str(kIn2['data']).split('\x1c')
                # конец блока

                # перекодировка данных в читаемый текст для вывода и лога
                bts1 = [str(str_to_byte(btsx), 'cp866') for btsx in bts]

                pportinwrite(bytes_to_read)
                pport = 2

                #0802txtprint = f" 2>K: {[f'{r}:{byte_to_str(kIn2[r])}' for r in ['id', 'cod']]} data: {bts1}"
                txtprint = f" 2>K: {[f'{r}:{(kIn2[r])}' for r in ['id', 'cod']]} data: {bts1}"
                #print(txtprint)
                logging.info(txtprint)
                logging.debug(f" 2>K: {kIn2}")
                logging.debug(f" 2>K: bytes_to_read: {bytes_to_read}")
        except:
            print(f"Порт2 ОШИБКА :{traceback.format_exc()} в модуле получения данных. ")
            logging.error(f"Порт2 Ошибка {traceback.format_exc()} в модуле получения данных. ")

#  id = kIn2['id'].decode(encoding="utf-8", errors="strict")


# Поток получения информация из Консоли
def thread_maincourceA(name):  #
    global inKKT
    global inSOFT
    global inSOFT2
    global bbegin
    global id
    global pport

    l = range(33, 126)
    while True:
        try:
            inp = input("")
            # if inp == 'exit':
            #    print('exit1')
            #    sys.exit()
            #    print('exit2')
            if inp in ['X', 'x', 'Х', 'х']:  # x - отчёт
                pport = 3
                # ll = chr(random.choice(l))
                # sss = new_str(f"{ll}", '20', rus('ФИО Кассира'))
                sss = new_str(fid(), '20', rus('ФИО Кассира'))
                # print(sss)
                # print(f"{sss}")
                print('X-Отчёт')
                pportinwrite(sss)
            elif inp in ['help', 'h', 'H', 'HELP', 'Help', 'р', '?']:  # z - отчёт
                print(txthelp)
            elif inp in ['Z', 'z', 'Я', 'я']:  # z - отчёт
                pport = 3
                # ll = chr(random.choice(l))
                sss = new_str(fid(), '21', rus('ФИО Кассира'))
                # print(sss)
                # print(f"{sss}")
                print('Z-Отчёт')
                pportinwrite(sss)

            elif inp in ['restart', 're', 'reboot']:  # restart
                pport = 3
                # ll = chr(random.choice(l))
                sss = new_str(fid(), '9C', "")
                print(sss)
                # print(f"{sss}")
                print('Рестарт ККТ')
                pportinwrite(sss)


            elif inp in ['00']:  # z - состояние кассы
                pport = 3
                # ll = chr(random.choice(l))
                sss = new_str(fid(), '00', '0')
                print('3>K:Состояние [00]')
                pportinwrite(sss)
                pport = 3
                # ll = chr(random.choice(l))
                sss = new_str(fid(), '02', '2')
                print('3>K:Прошивка [2.2]')
                pportinwrite(sss)
                pport = 3
                # ll = chr(random.choice(l))
                sss = new_str(fid(), '04', '')
                print('3>K:Принтер [4]')
                pportinwrite(sss)

            elif inp in ['out']:  # 32. Аннулировать документ
                pport = 3
                # ll = chr(random.choice(l))
                sss = new_str(fid(), '32', '')
                # print(sss)
                # print(f"{sss}")
                print('Аннулировать документ')
                pportinwrite(sss)

            elif inp == 'proxy':  # проверка связи
                service_request = psutil.win_service_get('ComProxy')  # подключение к службе ComProxy
                print(service_request.name(), service_request.status())  # запрос на имя службы и ее статус
                if service_request.status() == 'stopped':  # условие на перезапуск службы
                    subprocess.call('net start ComProxy')
                    print('service ... запускаем')
                else:
                    print('service работает')

            elif inp == '1':  # проверка связи
                pportinwrite(b'\x05')

            elif inp in ['begin']:  # начало работы
                print('Начало работы')
                pport = 3
                timeb = strftime("%H%M%S", time.localtime())
                dateb = strftime("%d%m%y", time.localtime())

                # ll = chr(random.choice(l))
                # ll = 'R'
                com = "10"
                param = {dateb, timeb}
                sss = new_str(fid(), com, param)
                # print(sss)
                #print(f"3>K:УcтановкаВремени[10]:{sss}")
                pportinwrite(sss)



            elif inp in ['open', 'открыть']:  # открытие смены
                print('Открыть смену')
                pport = 3
                timeb = strftime("%H%M%S", time.localtime())
                dateb = strftime("%d%m%y", time.localtime())

                # ll = chr(random.choice(l))
                # ll = 'R'
                com = "10"
                param = {dateb, timeb}
                sss = new_str(fid(), com, param)
                # print(sss)
                print(f"3>K:УcтановкаВремени[10]:{sss}")

                pportinwrite(sss)

                pport = 3
                # ll = chr(random.choice(l))
                # ll = 'O'
                com = "23"
                param = {rus("ФИО Кассира")}
                sss = new_str(fid(), com, param)
                # print(sss)
                print(f"3>K:ОткрытьСмену[23]{sss}")
                pportinwrite(sss)

            elif inp == 'is_open':
                print("Проверка состояния портов:")
                print(f"PORTIN   {portin.is_open}")
                print(f"PORTOUT1  {portout1.is_open}")
                print(f"PORTOUT2 {portout2.is_open}")

            elif inp == 'reopen':
                print("Переоткрытие портов")
                # global COMIN
                # portin.port = COMIN
                # = serial.Serial(port=COMIN, timeout=None, baudrate=57600, stopbits=serial.STOPBITS_ONE,
                #                       bytesize=serial.EIGHTBITS)
                # print(f"COMOUT : {COMOUT}")
                # portout = serial.Serial(port=COMOUT, timeout=None, baudrate=57600, stopbits=serial.STOPBITS_ONE,
                #                        bytesize=serial.EIGHTBITS)
                # print(f"COMOUT2: {COMOUT2}")
                # portout2 = serial.Serial(port=COMOUT2, timeout=None, baudrate=57600, stopbits=serial.STOPBITS_ONE,
                #                        bytesize=serial.EIGHTBITS)

                # print(f"PORTIN   {portin.open()}")
                # print(f"PORTOUT  {portout.open()}")
                # print(f"PORTOUT2 {portout2.open()}")



            elif inp == '911':
                pport = 3
                com = input("Консольный режим работы с кассой \nВведите команду : ")
                # проверка на список доступных команд, если нет в списке - исключение
                try:
                    print(f"{com} # {command[com]}")
                    print("Введите параметры, окончание - пустой параметр (Enter)")
                    param = []
                    p = '1'
                    i = 0
                    while p != '':
                        p = input(f"Параметр {i}: ")
                        i += 1
                        if p != '':
                            param.append(rus(p))
                    if input("Введите 1 для отправки ") == '1':
                        # ll = chr(random.choice(l))
                        # ll='R'
                        sss = new_str(fid(), com, param)  # f"{ll}"
                        print(sss)
                        print(f"{sss}")
                        pportinwrite(sss)
                    else:
                        print("Отмена отправки")
                except:
                    print('#! НЕДОПУСТИМАЯ КОМАНДА')
                    logging.error(f"#! НЕДОПУСТИМАЯ КОМАНДА: {traceback.format_exc()}")


            elif inp == '900':

                pport = 3
                print("Консольный режим работы с кассой \nКоманда + параметры через пробел \n "
                      "Отправить - последняя строка end")
                com900 = input()

                while com900 != 'end':
                    print(f'com900={com900}')
                    if '|' in com900:
                        com101, com901 = com900.split('|', 1)
                        param = rus(com901).split('|')
                    else:
                        com101 = com900
                        param = []
                    # проверка на список доступных команд, если нет в списке - исключение
                    print(f"{com101} # {command[com101]}")
                    sss = new_str(fid(), com101, param)  # f"{ll}"
                    pportinwrite(sss)
                    # time.sleep(0.5)
                    com900 = input()
            #            except:
            #                    print(f'{com101} #! НЕДОПУСТИМАЯ КОМАНДА')

            elif inp == '922':
                pport = 3
                d = input("Отправка на кассу строки (без контрольной суммы) : ")
                # sss1=sss.encode()
                print(d)

                # input
                # \x02PIRIR022\x1c\x03    7F
                # output
                # A0210126019473
                i = 0
                sss = ''
                while i < d.__len__():
                    s = d[i]
                    if s == '\\':
                        s = chr(int(f"{d[i + 2]}{d[i + 3]}", 16))
                        i = i + 3
                    i += 1
                    print(s, ord(s))
                    sss += s
                print('sss', sss)
                # --------------------------
                eee = (add_check_sum((str_to_byte(sss))))
                # eee = str_to_byte(sss)
                print(eee)
                pportinwrite(eee)
                print("отправили команду: ")

            elif inp == '888':
                with open('c:/2020/kassa/spam.bmp', 'rb') as f:
                    data = bytearray(f.read())
                #print(data)
                print(len(data))
                sss = new_str(fid(), '15', ['3374'])  # f"{ll}"
                pportinwrite(sss)
                input()
                pportinwrite(chr(27).encode('utf-8'))
                pportinwrite(data)

            elif inp == '889':
                with open('c:/work/hello.bmp', 'rb') as f:
                    data = bytearray(f.read())
                #print(data)
                print(len(data))
                sss = new_str(fid(), '55', [123,469,0])  # f"{ll}"
                pportinwrite(sss)
                time.sleep(0.2)
                #portin.write(chr(27).encode('utf-8'))
                pportinwrite(data)

            elif inp == '999':
                pport = 3
                print("Режим пакетного ввода команд, для окончания введите 1")
                d = input()
                # d = rus(d)
                while d != '1':
                    # A0210126019473
                    i = 0
                    sss = ''
                    while i < d.__len__():
                        s = d[i]
                        if s == '\\':
                            s = chr(int(f"{d[i + 2]}{d[i + 3]}", 16))
                            i = i + 3
                        i += 1
                        print(s, ord(s))
                        sss += s
                    print('sss', sss)
                    # --------------------------
                    eee = (add_check_sum((str_to_byte(sss))))
                    # eee = str_to_byte(sss)
                    print(eee)
                    pportinwrite(eee)
                    print("отправили команду: ")
                    d = input()

        except:
            print(f"Ошибка в блоке {traceback.format_exc()} ")
            logging.error(f"Ошибка в блоке {traceback.format_exc()} ")




def kkm_txt(a):
    global pport
    global txtpost
    global wait
    global last_cod
    pport = 4
    txtpost = ""  # переменная ответа
    for i in a:
        print(f"{i['Command']:}")
        com = f"{i['Command']}"
        param = []
        for j in i['Arg']:
            print(f"      {j}")
            param.append(rus(j))
        cod = fid()
        sss = new_str(cod, com, param)  # f"{ll}"
        print(sss)
        print(f"4>K: {sss}")
        portin.write(sss)
    last_cod = cod

    # wait = False
    # print(f"wait = {wait}")


# Работа с веб интерфейсом
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        global wait
        global txtpost
        global last_cod
        global pport
        print("!!!!!!!!!!!!!!!!!")
        # txtpost=''
        pport = 5
        length = int(self.headers.get('Content-length', 0))
        data = self.rfile.read(length).decode()
        print(data)
        # 3. Extract the "message" field from the request data.
        # print(data.encode('utf-8').decode('utf-8-sig'))
        data = data.replace("\r", "|")
        data = data.replace("\n", "|")
        j = json.loads(data.encode('utf-8').decode('utf-8-sig'))
        print(f"post.json:{j}")
        print(j['Type'])
        last_cod = "stop"
        wait = True
        for xx in j['Coms']:
            print(xx['C'], xx['Arg'])
            try:
                xx['Arg'][0] = rus(xx['Arg'][0])
            except:
                pass
            my_fid = fid()
            sss = new_str(my_fid, xx['C'], xx['Arg'])  # f"{ll}"
            #1402pportinwrite(sss)
        last_cod = my_fid

        # if j['BillType'] == 666:
        #    kkm_txt(j['El'])

        while wait:
            # print(wait)
            time.sleep(0.05)
            pass

        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        # self.wfile.write(txtpost.encode())
        print(f">>>txtpost>>>{txtpost}")
        self.wfile.write(bytes(txtpost, "utf-8"))

        # otv = 'Ok'

        # for i in res9:
        #    self.wfile.write(otv.encode())

    def do_GET(self):
        global txtpost
        print("GET:")
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        # time.sleep(10)
        s0 = '''<style  type = "text/css">
        p
        {
            font-size: 11;
        font-family: Verdana, Arial, Helvetica, sans - serif;
        color:  # ff3366;
        }
        </style>
        '''
        # self.wfile.write(bytes(s0, "utf-8"))
        self.end_headers()
        self.wfile.write(bytes(s0, "utf-8"))
        # self.wfile.write("Hello World!")
        now = datetime.now()
        s = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S <br>\n \r")
        self.wfile.write(bytes(f"<p>{s}</p>", "utf-8"))

        r = ''

        filename = 'kassa2021.log'
        with open(filename, ) as file_object:
            for line in file_object:
                if line[:10]==datetime.today().strftime('%Y-%m-%d'):
                    r+=f"{line}<br>"


        #print(r)

        self.wfile.write(bytes(
            f"<p><br>{r}{txtpost}<br></p><p>Сервер кассовых чеков запущен. <br>Работает. <br>Полёт нормальный!!!<br><br><br> \n \r ",
            "utf-8"))
        # result = self.response.json().get('result')
        # print(result)
        html = ""


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass


def serve_on_port(sip, sport):
    try:
        print("Запустили...")
        server = ThreadingHTTPServer((sip, sport), Handler)  # localhost 10.10.8.178
        server.serve_forever()
    except KeyboardInterrupt:
        print("^C received, shutting down server")
        server.socket.close()


# - ------------------------------------
#
#       Г Л А В Н Ы Й    Б Л О К
#
#
#
#
# - ------------------------------------
COMIN = config['DEFAULT']['COMPROXYKASSA']  # 'COM7' # порт компрокси для кассы
ipport = int(config['SERVER']['IPPORT']) # PORTA = "3333"
ip = config['SERVER']['IPSERVER'] # '10.10.8.190'

fServer = False
fClient = False
flagserver = config['SERVER']['FSERVER'] # 'server'
flagserver=flagserver.replace(' ', '')
if len(flagserver)>0:
    fServer = True
flagserver = config['SERVER']['FCLIENT'] # 'server'
flagserver=flagserver.replace(' ', '')
if len(flagserver)>0:
    fClient = True

print(f"* Сервер : {fServer} (подключаем ККМ)\n* Клиент : {fClient}")

sock = ''
max = 20
client = []
gport={}

leveld = int(config['LOG']['Logging'])  # logging.DEBUG
logging.basicConfig(level=leveld, filename='kassa2021.log', format='%(asctime)s %(levelname)s:%(message)s')

STX = '\x02'  # 0x02
ETX = '\x03'  # 0x03
PASS = 'PIRI'
ENQ = '\x05'  # 0x03
ACK = '\x06'  # 0x03
FS = '\x1c'  # 0x1C
LF = '\x0A'  # 0x0A перемотка бумаги
lastfid = 0





txtpost = ""
pport = 0
spisok_id = ['id', 'cod', 'data']

try:
    COMIN = config['DEFAULT']['COMPROXYKASSA']  # 'COM7' # порт компрокси для кассы
    COMOUT1 = config['DEFAULT']['COM1C1']  # 'COM15'  # порт указывается в 1с для подключения кассы
    COMOUT2 = config['DEFAULT']['COM1C2']  # 'COM7'
    webIP = config['WEB']['IP']  # "0.0.0.0"
    webPort = int(config['WEB']['Port'])  # 1212
    PersonalName = config['PERSONAL']['Name']  # "0.0.0.0"
    logging.info(f" Загружаем конфигурацию ")
except:
    print(f"ошибка данных ini файла.")
    logging.error(f"Ошибка данных ini файла {traceback.format_exc()}")
    print(input)
    exit()

# pl = platform.uname()

#white = True

#-- информация о Компрокси
comproxy_path = psutil.win_service_get('ComProxy').as_dict()['binpath']
comproxy_status = psutil.win_service_get('ComProxy').as_dict()['status']
print("Информация о ComProxy")
print(comproxy_path, comproxy_status)
print('- ' * 15)
#--

inKKT = []
inSOFT = []
inSOFT2 = []
bbegin = False
fid.id = chr(65)
pport = 0
last_cos = ""

try:
    #if 'server' in flagserver:
    if fServer:
        print(f"COMIN : {COMIN}")
        portin = serial.Serial(port=COMIN, timeout=None, baudrate=57600, stopbits=serial.STOPBITS_ONE,
                               bytesize=serial.EIGHTBITS)
    #if 'сlient' in flagserver:
    if fClient:
        print(f"COMOUT1 : {COMOUT1}")
        portout1 = serial.Serial(port=COMOUT1, timeout=None, baudrate=57600, stopbits=serial.STOPBITS_ONE,
                                bytesize=serial.EIGHTBITS)
        y = threading.Thread(target=thread_com1, args=(1,))
        y.start()

        print(f"COMOUT2: {COMOUT2}")
        portout2 = serial.Serial(port=COMOUT2, timeout=None, baudrate=57600, stopbits=serial.STOPBITS_ONE,
                                 bytesize=serial.EIGHTBITS)
        z = threading.Thread(target=thread_com2, args=(1,))
        z.start()

except OSError as e:
    logging.error(f"ошибка открытия порт {OSError}")
    print(f"ошибка открытия порт {OSError}")
    i = input()
    exit()

logging.info(f" Порты подключены")

#-----------------------------
print('Отправка данных о запуске программы....')
try:
    pl = platform.uname()
    data = (
        f"{pl.system} {pl.node} {pl.version} {pl.machine} - ver{ver}: {COMIN} : {COMOUT1} : {COMOUT2} - {PersonalName}")
    data1 = {"from": "Alex", "to": "Alex2", "mes": data, "flag": "add"}
    base = "http://www.a-34.ru/MAP/p.php?"
    r = requests.get(base, params=data1)
    print('...данные отправлены')
except:
    logging.error(f"ошибка загрузки на a-34.ru нет интернета, или сайт - офф")
    print('...ошибка загрузки на a-34.ru нет интернета, или сайт - офф')
#-----------------------------

# -- запуск IP сервера ---


if fServer:
    print("Запускаем сервер ip")
    thread7 = Thread(target=serverwait, args=())
    thread7.start()
elif fClient:
#if flagserver == 'сlient':
    print("Запускаем клиент ip")
    thread8 = Thread(target=connectClient, args=())
    thread8.start()
#--------------------------------------------------------

print(f"Программа запущена. Не закрывайте меня. версия {ver}")
# print(f"Порты для подключения:")

print('- ' * 15)
print("help - для вывода списка команд")
print('- ' * 15)

#if 'server' in flagserver:
if fServer:
    x = threading.Thread(target=thread_fromKKT, args=(1,))
    x.start()
#if 'client' in flagserver:
    #portin.write(b'\x05')

# - ------------------------------------


txtA = ""
maincource = threading.Thread(target=thread_maincourceA, args=(1,))
maincource.start()
print(f"запуск сервера: http://{webIP}:{webPort}")
serve_on_port(webIP, webPort)

b = '{  "BillType": 666, ' \
    '"El":' \
    '[' \
    '{"Command" : "30" , "Arg" : [49,1,"Popov",100,4]},' \
    '{"Command" : "40" , "Arg" : ["Проверка текста.Малый текст.0123456789[43]1234",0]},' \
    '{"Command" : "40" , "Arg" : ["Широкий>>>>>>>>>[20]>",32]},' \
    '{"Command" : "40" , "Arg" : ["ВЫСОКИЙ ШРИФТ4567890123456789012345678[42]3",16]},' \
    '{"Command" : "40" , "Arg" : ["подчеркнуть",128]},' \
    '{"Command" : "41" , "Arg" : [0,5,0,8,"t=20200203T1604&s=1.00&fn=9287440300026894&i=34014&fp=2972911564&n=1"]},' \
    '{"Command" : "31" , "Arg" : [0,"a@a-34.ru"]}    ' \
    ']' \
    '}'
'''
requests.post('http://localhost:1212',data=b.encode('utf-8')).text
'''
c = '{' \
    '"BillType":666, ' \
    '"El":' \
    '[' \
    '{"Command" : "30" , "Arg" : [2,1,"Popov",100,3]},' \
    '{"Command" : "42" , "Arg" : ["Nokia 3400","0123456",1,2.00,3,"",1,0,"",0.00,1,1,"",""]},' \
    '{"Command" : "44" , "Arg" : [""]},' \
    '{"Command" : "47" , "Arg" : [0,3.00,""]},' \
    '{"Command" : "47" , "Arg" : [1,1.00,""]},' \
    '{"Command" : "31" , "Arg" : [0,"a@a-34.ru","",""]}' \
    ']' \
    '}'
# '{"Command" : "45" , "Arg" : [1, "SKIDKA", 1.00]},' \

'''
# "cod:b'31'"
# "data: 46036 604.7 84 34110  x8f 4047582530
'''

'''

import psutil
for proc in psutil.process_iter(['pid', 'name', 'username']):
     print(proc.info)

{'username': None, 'pid': 25008, 'name': 'ComProxySrv.exe'}

'''

''' пробить чек...
'{"BillType":666, 
"El":[
{"Command" : "30" , 
"Arg" :[2,1,"Popov",100,3]},

{"Command" : "42" , 
"Arg" : ["Nokia 3400","0123456",1,2.00,3,"",1,0,"",0.00,1,1,"",""]},

{"Command" : "44" , 
"Arg" : [""]},

{"Command" : "47" , 
"Arg" : [0,3.00,""]},

{"Command" : "47" , 
"Arg" : [1,1.00,""]},

{"Command" : "31" , 
"Arg" : [0,"a@a-34.ru","",""]}]}'
'''

# import random

# print(strftime("%d%m%y %H%M%S", localtime()))
# print(strftime("%d%m%y", time.localtime()))
# print(strftime("%H%M%S", time.localtime()))

'''
900
32||
30|1|
40|Тестовый текст|1
40|Тестовый текст|0
41|0|5|0|8|t=20200203T1604&s=1.00&fn=9287440300026894&i=34014&fp=2972911564&n=1|
40|Тестовый текст|1
40|Тестовый текст|0
32|
end


900 - все данные
01|1
01|2
01|3
01|4
01|5
01|6
01|7
01|8
01|9
01|10
01|11
01|12
01|15
01|16
01|17
01|18
02|1
02|2
02|3
02|4
02|5
02|6
02|7
02|8
02|9
02|10
02|11
02|12
02|13
02|14
02|15
02|16
02|17
02|18
02|19
02|20
02|21
02|22
02|23
end

'''


# requests.post('http://localhost:1212',data='{  "BillType": 2,  "BillOtdel": "",  "BillKassir": "Иванов",  "BillNumDoc": "",  "BillTax": "3",  "BarCodeHeader": {  "BarcodeType": "PDF417",  "Barcode": "www.pavlyukevich.ru"  },  "CheckStrings": [  {  "Name": "Сотовый телефон Nokia 3310",  "Art": 1,  "Quantity": 1,  "Price": 0.10,  "Tax": 3,  "Posicion": "",  "Department": 0,  "TypeSale": 3,  "Rezerv": "",  "SumSale": "",  "PSR": 4,  "PPR": 1  },  {  "Name": "Сотовый телефон Nokia 3410",  "Art": 1,  "Quantity": 1,  "Price": 0.50,  "Tax": 3,  "Posicion": "",  "Department": 0,  "TypeSale": 3,  "Rezerv": "",  "SumSale": "",  "PSR": 4,  "PPR": 1  }  ],  "Cash": 0.60,  "PayByCard": 0,  "PayByCredit": 0,  "PayByCertificate": 0,  "ClientTel": "",  "BarCodeFooter": {  "BarcodeType": "CODEQR",  "Barcode": "www.pavlyukevich.ru"  } }'.encode('utf-8'))

# a = '{  "BillType": 666, "El":[{"Command" : "30" , "Arg" : [49,1,"Popov",100,4]},{"Command" : "40" , "Arg" : ["Проверка текста.Малый текст.0123456789[43]1234",0]},{"Command" : "40" , "Arg" : ["Широкий>>>>>>>>>[20]>",32]},{"Command" : "40" , "Arg" : ["ВЫСОКИЙ ШРИФТ4567890123456789012345678[42]3",16]},{"Command" : "40" , "Arg" : ["подчеркнуть",128]},{"Command" : "41" , "Arg" : [0,5,0,8,"t=20200203T1604&s=1.00&fn=9287440300026894&i=34014&fp=2972911564&n=1"]},{"Command" : "32" , "Arg" : [0,"a@a-34.ru"]}    ]}'
# requests.post('http://localhost:1212',data=a.encode('utf-8'))

