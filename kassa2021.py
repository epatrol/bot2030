from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import json
import time
import threading
import configparser
import serial
import threading
import logging
import subprocess
import psutil

#from kassa2 import rus
#from kassa2 import new_str
#from kassa2 import add_check_sum
#from femail import send_email_with_attachment
#import requests
#import platform
#import time
import random
#import time
from time import time, localtime, strftime
from datetime import datetime
import time
#print(strftime("%d%m%y %H%M%S", localtime()))
#print(strftime("%d%m%y", time.localtime()))
#print(strftime("%H%M%S", time.localtime()))

ver = "09/07/2020 17:00"


#requests.post('http://localhost:1212',data='{  "BillType": 2,  "BillOtdel": "",  "BillKassir": "Иванов",  "BillNumDoc": "",  "BillTax": "3",  "BarCodeHeader": {  "BarcodeType": "PDF417",  "Barcode": "www.pavlyukevich.ru"  },  "CheckStrings": [  {  "Name": "Сотовый телефон Nokia 3310",  "Art": 1,  "Quantity": 1,  "Price": 0.10,  "Tax": 3,  "Posicion": "",  "Department": 0,  "TypeSale": 3,  "Rezerv": "",  "SumSale": "",  "PSR": 4,  "PPR": 1  },  {  "Name": "Сотовый телефон Nokia 3410",  "Art": 1,  "Quantity": 1,  "Price": 0.50,  "Tax": 3,  "Posicion": "",  "Department": 0,  "TypeSale": 3,  "Rezerv": "",  "SumSale": "",  "PSR": 4,  "PPR": 1  }  ],  "Cash": 0.60,  "PayByCard": 0,  "PayByCredit": 0,  "PayByCertificate": 0,  "ClientTel": "",  "BarCodeFooter": {  "BarcodeType": "CODEQR",  "Barcode": "www.pavlyukevich.ru"  } }'.encode('utf-8'))

#a = '{  "BillType": 666, "El":[{"Command" : "30" , "Arg" : [49,1,"Popov",100,4]},{"Command" : "40" , "Arg" : ["Проверка текста.Малый текст.0123456789[43]1234",0]},{"Command" : "40" , "Arg" : ["Широкий>>>>>>>>>[20]>",32]},{"Command" : "40" , "Arg" : ["ВЫСОКИЙ ШРИФТ4567890123456789012345678[42]3",16]},{"Command" : "40" , "Arg" : ["подчеркнуть",128]},{"Command" : "41" , "Arg" : [0,5,0,8,"t=20200203T1604&s=1.00&fn=9287440300026894&i=34014&fp=2972911564&n=1"]},{"Command" : "31" , "Arg" : [0,"a@a-34.ru"]}    ]}'
#requests.post('http://localhost:1212',data=a.encode('utf-8'))
import sys

def fid():
    global id
    o = ord(id) + 1
    if o > 90: o = 65
    id = chr(o)
    return f"{id}"

def int2bit(num, pos):
    return (num & (1 << pos)) >> pos

def bit2error(scod, name):
    s = []
    cod = int(scod)
    #    print(cod)
    for pos in range(8):
        #        print(func(cod, pos))
        if int2bit(cod, pos) == 1:
            s.append(name[pos])
    return s


def cod00(bts):
    fatal_kkt = ['Неверная контрольная сумма NVR', 'Неверная контрольная сумма в конфигурации',
                 'Нет связи с ФН', ' ', ' ', 'ККТ не авторизовано', 'Фатальная ошибка ФН', ' ', '.']
    status_kkt = ['не вызвана Начало работы', 'Нефискальный режим', 'Смена открыта', 'Смена>24часов', 'Архив ФН закрыт',
                  'ФН не зарег.', '', '', 'Не закрыта смена, повторите!']
    status_doc1 = ['Документ закрыт',
                   'Сервисный документ',
                   'Чек на продажу (приход)',
                   'Чек на возврат (возврат прихода)',
                   'Внесение в кассу',
                   'Инкассация',
                   'Чек на покупку (расход)',
                   'Чек на возврат покупки (возврат расхода)']
    status_doc2 = [
        'Документ закрыт',
        'Устанавливается после команды «открыть документ». (Для типов документа 2, 3, 6, 7 - можно вводить товарные позиции.)',
        'Устанавливается после первой команды «Подытог». Можно делать скидки на чек.',
        'Устанавливается после второй команды «Подытог» или после начала команды «Оплата». Можно только производить оплату различными типами платежных средств.',
        'Расчет завершен – требуется закрыть документ.',
        '',
        '',
        '',
        'Команда закрытия документа была дана в ФН, но документ не был завершен. Аннулирование документа невозможно.'
    ]
    # bts: ['0', '4', '0', '']
    # Статус фатального состояния ККТ
    st_fatal = (bit2error(bts[0], fatal_kkt))
    if st_fatal == []:
        st_fatal = '[ Ок ]'
    # Статус текущих флагов ККТ
    st_kkt = (bit2error(bts[1], status_kkt))
    # Статус документа
    st_doc1 = (bit2error(int(bts[2]) // 16, status_doc1))
    st_doc2 = (bit2error(int(bts[2]) % 16, status_doc2))
    print(" -" * 15)
    print(f"Статус ККТ: {st_fatal} {st_kkt} {st_doc1} {st_doc2}")
    print(" -" * 15)

    # e1[arg3 // 16]
    # e2[arg3 % 16]

def cod04(bts):
    status_print = ['Принтер не готов','В принтере нет бумаги','Открыта крышка принтера','Ошибка резчика принтера',
                    '','','','Нет связи с принтером']
    # Статус текущих флагов ККТ
    st_printer = (bit2error(bts[0], status_print))
    print(" -" * 15)
    if st_printer == []:
        st_printer=['Принтер к работе готов!']
    print(f"Состояние Принтера: {st_printer} ")
    print(" -" * 15)

def cod02(bts):
    try:
        if bts[0] == '2': # номер прошивки
            print(" -" * 15)
            print(f"Прошивка: {bts[1]}.{bts[2]}.{bts[3]}")
            print(" -" * 15)
    except:
        print(f"Прошивка: {bts[1]}")


def rus(bbb):
    try:
        b98 = bbb.encode('cp866')
        s88 = ''
        for bbbb in b98:
            s88 += chr(bbbb)
        return s88
    except:
        return bbb

def add_check_sum(command):
    checksum = 0
    # чексумма без первого символа
    i = 0
    for el in command:
        if i == 0:
            i = 1
        else:
            checksum ^= el
#    a = (f"{hex(checksum)}").upper()
    # добавляем чексум в конец
    b = checksum // 16
    c = checksum % 16
    if c > 9 :
        if c == 10: cc = 'A'
        if c == 11: cc = 'B'
        if c == 12: cc = 'C'
        if c == 13: cc = 'D'
        if c == 14: cc = 'E'
        if c == 15: cc = 'F'
    else:
        cc = str(c)

    if b > 9 :
        if b == 10: bb = 'A'
        if b == 11: bb = 'B'
        if b == 12: bb = 'C'
        if b == 13: bb = 'D'
        if b == 14: bb = 'E'
        if b == 15: bb = 'F'
    else:
        bb = str(b)

    command.append(ord(bb))
    command.append(ord(cc))
    ################################
    #print("cc", cc)
    return command


def new_str(num1: object, comm1: object, param1: object) -> object:
    s9 = ''
    for k in param1:
        s9 += f"{k}\x1c"
    nnn = f"\x02PIRI{num1}{comm1}{s9}\x03"
    #print("nnn", nnn)
    ppp = add_check_sum(str_to_byte(nnn))
    #print("ppp", ppp)
    return ppp

'''
def new_str1(num1: object, comm1: object, param1: object) -> object:
    s9 = ''
    for k in param1:
        s9 += f"{k}\x1c"
        x02 = '\x02'
    nnn = f"\x02{num1}{comm1}{s9}\x03"
    ppp = add_check_sum(str_to_byte(nnn))
    return ppp
'''

'''
def str_to_byte(s):
    #tmpBuffer1 = bytearray([])
    tmpBuffer1= b''
    for ss in s:
        #tmpBuffer1.append(ord(ss))
        tmpBuffer1 += ord(ss)
    print("tmpBuffer1=",tmpBuffer1)
    return tmpBuffer1
'''


def thread_function1(name):  # из KKT получаем
    global pport
    global txtpost
    global wait
    global last_cod

    print('Проверка связи с кассой...')
    while True:
        #if wait == False:

            # из ККТ ========
            #--------- блок получения информации ---------------
            bytes_to_read = portin.read(1)  # считываем байт, если
            if bytes_to_read == b'\x06':  #
                print("\t\t... касса ответила на запрос - работает\n","- " * 40)
                #portin.write(bytes_to_read)
            else:
                bytes_to_read += portin.read_until(b"\x03")
                bytes_to_read += portin.read(2)
            # --------- блок получения информации ---------------
                kOut1 = kOut(bytes_to_read)
                bts = byte_to_str(kOut1['data']).split('\x1c')
                print(f"K>{pport}: ", [f'{i}:{kOut1[i]}' for i in [ 'id', 'cod', 'error', 'data']])
                #print(f"kOut1:{kOut1['data']}\tbts:{bts}")
                s = datetime.strftime(datetime.now(), "%H:%M:%S")

                if pport == 1:
                    portout.write(bytes_to_read)
                elif pport == 2:
                    portout2.write(bytes_to_read)
                elif pport == 3: # работа с кассой из консоли
                    print("... работа с кассой из консоли ...")
                    #print(f"K>{pport}: ", [f'{i}:{kOut1[i]}' for i in ['id', 'cod', 'error', 'data']])
                    print(f"{s} K>{pport}: ID:{byte_to_str(kOut1['id'])} COD:{byte_to_str(kOut1['cod'])} ERROR:{byte_to_str(kOut1['error'])}  DATA:{bts}") # for i in ['id', 'cod', 'error', 'data']])")



                elif pport == 4: # работа с POST
                    #self.wfile.write(bytes(s, "utf-8"))
                    #tpost =(f"K>{pport}: ", [f'{i}:{kOut1[i]}' for i in ['id', 'cod', 'error', 'data']])
                    tpost = f"K>{pport}: ID:{byte_to_str(kOut1['id'])} COD:{byte_to_str(kOut1['cod'])} ERROR:{byte_to_str(kOut1['error'])}  DATA:{bts}" # for i in ['id', 'cod', 'error', 'data']])"
                    txtpost += f"{s} {tpost}\n<BR>"
                    print(f"{byte_to_str(kOut1['id'])} = {last_cod}")
                    if byte_to_str(kOut1['id']) == last_cod:#b'31':
                        wait = False
                    #print(f"txtpost:{txtpost}")
                else:
                    print("ERROR PORT!!!!")


                if kOut1['cod'] == b'00':
                    cod00(bts)
                if kOut1['cod'] == b'02':
                    cod02(bts)
                if kOut1['cod'] == b'04':
                    cod04(bts)

                if global1:
                    print(f"K>{pport} : {kOut1}")
                    print(bytes_to_read)
                    print("- " * 35)
                    cod02(bts)
            #wait = True

def thread_function2(name):
    global pport
    global global1

    while True:
        try:
            bytes_to_read = portout.read(1)  # считываем байт, если
            if bytes_to_read == b'\x05':  #
                print("1>Проверка связи")
                portout.write(b'\x06') # portin.write(bytes_to_read)
            elif bytes_to_read == b'\x0A':  #
                print("1>перевод строки")
                portin.write(bytes_to_read)
            else:
                bytes_to_read += portout.read_until(b"\x03")
                bytes_to_read += portout.read(2)
                #print(type(bytes_to_read))
                portin.write(bytes_to_read)
            pport = 1
            kIn1 = kIn(bytes_to_read)
            print(f"1>K: ",[ f'{i}:{kIn1[i]}' for i in ['id','cod','data']])
            if global1:
                print(f"1>K: {kIn1}")
                print(bytes_to_read)
        except e:
            print("Ошибка в функции/ Порт1", e)


def thread_function3(name):
    global pport
    #global wait

    while True:
        #wait = True
        try:
          #if wait == True:
            #wait = False
            bytes_to_read = portout2.read(1)  # считываем байт, если
            if bytes_to_read == b'\x05':  #
                print("2>Проверка связи")
                portout2.write(b'\x06')
            else:
                if bytes_to_read == b'\x0A':  #
                    print("2>перевод строки")
                    portin.write(bytes_to_read)
                else:
                    bytes_to_read += portout2.read_until(b"\x03")
                    bytes_to_read += portout2.read(2)
                #inKKT.append([bytes_to_read, 2])
#                portin.write(bytes_to_read)

                pport = 2
                kIn2 = kIn(bytes_to_read)
                #print(bytes_to_read)
                #print(type(bytes_to_read))
                #print(kIn2)
                #print(type(kIn2))
                #print(type(kIn2['id']))

                print(f"2>K: ", [f'{i}:{kIn2[i]}' for i in ['id', 'cod', 'data']])
                if global1:
                    print(f"2>K: {kIn2}")
                    print(bytes_to_read)

                #if kIn2['cod'] in [b'30', b'31', b'40', b'04', b'00', b'01']:
                    '''
                    # ---------------
                    print('auto...')
                    x02 = '\x02'
                    x1c = '\x1c'
                    x03 = '\x03'
                    id = kIn2['id'].decode(encoding="utf-8", errors="strict")
                    #sss = f'{x02}A021{x1c}0126019473{x1c}{x03}') kIn2['id']
                    sss = f'{x02}{id}021{x1c}0126019473{x1c}{x03}'
                    ssss = add_check_sum(str_to_byte(sss))
                    print(ssss)
                    portout2.write(ssss)
                else:
                    '''
                portin.write(bytes_to_read)



                # ---------------


        except:
            print("Ошибка в модуле получения данных. Порт2")
            logging.error("Ошибка в модуле получения данных. Порт2")




def kIn(s):
    ''' функция конвертирует строку отправляемую в ККТ по разделам '''
    k = dict.fromkeys(['stx','pirit','id','cod','data','etx','crc'])
    #print(pos(b'\x02',s))
    #i = pos(b'\x02', s)
    #s = s[i:]
    k['stx'] = s[0:1]
    k['pirit'] = s[1:5]
    k['etx'] = s[-3:-2]
    k['crc'] = s[-2:]
    k['id'] = s[5:6]
    k['cod'] = s[6:8]
    k['data'] = s[8:-3]
    print(k)
    return(k)

def kOut(s):
    ''' дешифратор строки из ККТ
    функция конвертирует строку получаемую из ККТ по разделам '''

    k = dict.fromkeys(['stx','id','cod','error','data','etx','crc'])
    k['stx'] = s[0:1]
    k['etx'] = s[-3:-2]
    k['crc'] = s[-2:]
    k['id'] = s[1:2]
    k['cod'] = s[2:4]
    k['error'] = s[4:6]
    k['data'] = s[6:-3]
    #print(f"kOut/k={k}")
    return(k)

def byte_to_str(b):
    s = ""
    for i in b:
        s += (chr(i))
    return s

def str_to_byte(s):
    tmpBuffer1 = bytearray([])
    for ss in s:
        tmpBuffer1.append(ord(ss))
    return tmpBuffer1














def thread_maincourceA(name):  #
    global inKKT
    global inSOFT
    global inSOFT2
    global bbegin
    global id
    global pport
    global global1

    l = range(33, 126)
    while True:
        inp = input()
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
            portin.write(sss)

        elif inp in ['Z', 'z', 'Я', 'я']:  # z - отчёт
            pport = 3
            # ll = chr(random.choice(l))
            sss = new_str(fid(), '21', rus('ФИО Кассира'))
            # print(sss)
            # print(f"{sss}")
            print('Z-Отчёт')
            portin.write(sss)

        elif inp in ['restart', 're', 'reboot']:  # restart
            pport = 3
            # ll = chr(random.choice(l))
            sss = new_str(fid(), '9C', "")
            print(sss)
            # print(f"{sss}")
            print('Рестарт ККТ')
            portin.write(sss)


        elif inp in ['00']:  # z - отчёт
            pport = 3
            # ll = chr(random.choice(l))
            sss = new_str(fid(), '00', '0')
            print('3>K:Состояние [00]')
            portin.write(sss)
            pport = 3
            # ll = chr(random.choice(l))
            sss = new_str(fid(), '02', '2')
            print('3>K:Прошивка [2.2]')
            portin.write(sss)
            pport = 3
            # ll = chr(random.choice(l))
            sss = new_str(fid(), '04', '')
            print('3>K:Принтер [4]')
            portin.write(sss)


        elif inp in ['out']:  # 32. Аннулировать документ
            pport = 3
            # ll = chr(random.choice(l))
            sss = new_str(fid(), '32', '')
            # print(sss)
            # print(f"{sss}")
            print('Аннулировать документ')
            portin.write(sss)

        elif inp == 'comproxy':  # проверка связи
            service_request = psutil.win_service_get('ComProxy')  # подключение к службе ComProxy
            print(service_request.name(), service_request.status())  # запрос на имя службы и ее статус
            if service_request.status() == 'stopped':  # условие на перезапуск службы
                subprocess.call('net start ComProxy')
            else:
                print('service running')

        elif inp == '1':  # проверка связи
            portin.write(b'\x05')

        elif inp in ['begin','open', 'открыть']:  # открытие смены
            print('Открыть смену')
            pport = 3
            timeb = strftime("%H%M%S", time.localtime())
            dateb = strftime("%d%m%y", time.localtime())

            # ll = chr(random.choice(l))
            # ll = 'R'
            com = "10"
            param = {timeb, dateb}
            sss = new_str(fid(), com, param)
            # print(sss)
            print(f"3>K:УcтановкаВремени[10]:{sss}")

            portin.write(sss)

            pport = 3
            # ll = chr(random.choice(l))
            # ll = 'O'
            com = "23"
            param = {rus("ФИО Кассира")}
            sss = new_str(fid(), com, param)
            # print(sss)
            print(f"3>K:ОткрытьСмену[23]{sss}")
            portin.write(sss)

        elif inp == 'is_open':
            print("Проверка состояния портов:")
            print(f"PORTIN   {portin.is_open}")
            print(f"PORTOUT  {portout.is_open}")
            print(f"PORTOUT2 {portout2.is_open}")

        elif inp == 'reopen':
            print("Переоткрытие портов")
            #global COMIN
            #portin.port = COMIN
                #= serial.Serial(port=COMIN, timeout=None, baudrate=57600, stopbits=serial.STOPBITS_ONE,
            #                       bytesize=serial.EIGHTBITS)
            #print(f"COMOUT : {COMOUT}")
            #portout = serial.Serial(port=COMOUT, timeout=None, baudrate=57600, stopbits=serial.STOPBITS_ONE,
            #                        bytesize=serial.EIGHTBITS)
            #print(f"COMOUT2: {COMOUT2}")
            #portout2 = serial.Serial(port=COMOUT2, timeout=None, baudrate=57600, stopbits=serial.STOPBITS_ONE,
             #                        bytesize=serial.EIGHTBITS)

            #print(f"PORTIN   {portin.open()}")
            #print(f"PORTOUT  {portout.open()}")
            #print(f"PORTOUT2 {portout2.open()}")



        elif inp == '911':
            pport = 3
            com = input("Консольный режим работы с кассой \nВведите команду : ")
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
                portin.write(sss)
            else:
                print("Отмена отправки")
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
            portin.write(eee)
            print("отправили команду: ")

        elif inp == '888':
            with open('spam.bmp', 'rb') as f:
                data = bytearray(f.read())
            portin.write(data)

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
                portin.write(eee)
                print("отправили команду: ")
                d = input()

        elif inp == 'global1':  # вывод информации
            global1 = True


def kkm_txt(a):
    global pport
    global txtpost
    global wait
    global last_cod
    pport = 4
    txtpost = "" #переменная ответа
    for i in a:
        print(f"{i['Command']:}")
        com =f"{i['Command']}"
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

    #wait = False
    #print(f"wait = {wait}")

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        global wait
        global txtpost
        length = int(self.headers.get('Content-length', 0))
        data = self.rfile.read(length).decode()
        print(data)
        # 3. Extract the "message" field from the request data.
        # print(data.encode('utf-8').decode('utf-8-sig'))
        data = data.replace("\r", "|")
        data = data.replace("\n", "|")
        j = json.loads(data.encode('utf-8').decode('utf-8-sig'))
        #print(f"post.json:{j}")

        wait = True

        if j['BillType'] == 666:
            kkm_txt(j['El'])

        while wait:
            #print(wait)
            time.sleep(0.1)
            pass

        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        #self.wfile.write(txtpost.encode())
        print(f">>>txtpost>>>{txtpost}")
        self.wfile.write(bytes(txtpost, "utf-8"))


        #otv = 'Ok'



        #for i in res9:
        #    self.wfile.write(otv.encode())

    def do_GET(self):
        global txtpost
        print("GET:")
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        #time.sleep(10)
        s0 = '''<style  type = "text/css">
        p
        {
            font - size: 80 %;
        font - family: Georgia, 'Times New Roman', Times, serif;
        color:  # ff3366;
        }
        </style>
        '''
        #self.wfile.write(bytes(s0, "utf-8"))

        self.end_headers()
        # self.wfile.write("Hello World!")
        now = datetime.now()
        s = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S <br>\n \r")
        self.wfile.write(bytes(s, "utf-8"))
        self.wfile.write(bytes(f"<br>{txtpost}<br><p>Сервер кассовых чеков запущен. <br>Работает. <br>Полёт нормальный!!!<br><br><br> \n \r ", "utf-8"))
        # result = self.response.json().get('result')
        # print(result)
        html = ""

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def serve_on_port(sip ,sport):
    try:
        print("Запустили...")
        server = ThreadingHTTPServer((sip, sport), Handler)  # localhost 10.10.8.178
        server.serve_forever()
    except KeyboardInterrupt:
        print("^C received, shutting down server")
        server.socket.close()







# - ------------------------------------

txtpost = ""
pport = 0
spisok_id = ['id','cod','data']


leveld = logging.DEBUG  # INFO
logging.basicConfig(level=leveld, filename='yakassa.log', format='%(asctime)s %(levelname)s:%(message)s')

#pl = platform.uname()
white = True

logging.debug(f" Загружаем конфигурацию ")
if True: #try:
    config = configparser.ConfigParser()
    config.read('yakassa.ini')
    COMIN = config['DEFAULT']['COMPROXYKASSA']  # 'COM7' # порт компрокси для кассы
    COMOUT = config['DEFAULT']['COM1C1']  # 'COM15'  # порт указывается в 1с для подключения кассы
    COMOUT2 = config['DEFAULT']['COM1C2']  # 'COM7'
    #pause_time = float(config['DEFAULT']['Pause'])  #
    #onOut2 = True
    #portOn = 0
#except:
#    print(f"ошибка загрузки ini файла.")
#    exit()
#except:
#    logging.error(f"ошибка загрузки ini файла.")
#    exit()
#p_t = pause_time

inKKT = []
inSOFT = []
inSOFT2 = []
bbegin = False
id = chr(65)
pport = 0
global1 = False
last_cos = ""

try:
    print(f"COMIN : {COMIN}")
    portin = serial.Serial(port=COMIN,timeout=None, baudrate=57600, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
    print(f"COMOUT : {COMOUT}")
    portout = serial.Serial(port=COMOUT, timeout=None, baudrate=57600, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
    print(f"COMOUT2: {COMOUT2}")
    portout2 = serial.Serial(port=COMOUT2, timeout=None, baudrate=57600, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
except OSError as e:
    logging.error(f"ошибка открытия порт {OSE2sv6t6Z29u1ALFA
    rror}")
    print(f"ошибка открытия порт {OSError}")
    i = input()
    exit()

logging.debug(f"порты подключены")

print(f"Программа запущена. Не закрывайте меня. версия {ver}")
#print(f"Порты для подключения:")

print('''Команды :
1 - проверка связи  ККМ
open (открыть) - открытие смены
z - закрытие смены (Z-отчёт)
x - отчёт без гашения (X-отчёт)

911 - консольный режим ввода команд
''')

#PortOnn = {}
wait = True

#def hello():
#    print("hello, world")
#
#t = threading.Timer(1.0, hello)
#t.start()

x = threading.Thread(target=thread_function1, args=(1,))
x.start()
y = threading.Thread(target=thread_function2, args=(1,))
y.start()
z = threading.Thread(target=thread_function3, args=(1,))
portin.write(b'\x05')
z.start()

# - ------------------------------------









IP = "0.0.0.0"
Port = 1212

txtA = ""
maincource = threading.Thread(target=thread_maincourceA, args=(1,))
maincource.start()
print(f"запуск сервера: http://{IP}:{Port}")
serve_on_port(IP,Port)


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