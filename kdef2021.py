#from kassa2 import rus
#from kassa2 import new_str
#from kassa2 import add_check_sum
#from femail import send_email_with_attachment
#import requests
#import platform
#import time

#https://stackoverflow.com/questions/59110136/why-is-pythons-serial-read-serial-read-until-returning-garbage-after-4-bytes
#https://pypi.org/project/pyshtrih/#id4
# драйвер кассы
#https://www.programcreek.com/python/?code=oleg-golovanov%2Fpyshtrih%2Fpyshtrih-master%2Fpyshtrih%2Fprotocol.py#


txthelp = '''- - - - - - - - - - - - - - 
Команды :
1 \t\t- проверка связи  ККМ
open\t- открытие смены
z \t\t- закрытие смены (Z-отчёт)
x \t\t- отчёт без гашения (X-отчёт)

911 \t- консольный режим ввода команд

proxy\t-проверка работы comproxy
is_open\t-проверка состояния портов

00\t\t-состояние кассы (флаги) 
? \t\t- вывод подсказки
- - - - - - - - - - - - - -
'''


def fid():
    o = ord(fid.id) + 1
    if o > 90: o = 65
    fid.id = chr(o)
    return f"{fid.id}"


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
    #print(k)
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
    try:
        tmpBuffer1 = bytearray([])
        for ss in s:
            tmpBuffer1.append(ord(ss))
    except:
        print(f"Error {s}, {tmpBuffer1}")
    return tmpBuffer1







