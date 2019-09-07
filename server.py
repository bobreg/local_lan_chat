import socket
import threading
import time
# Сервер написан без графического интерфейса. Его задача ожидать подключения от клиентов. Для каждого нового клиента
# запускать отдельный поток в котором будут ожидаться сообщения от клиента.
# Все подключившиеся клиенты вносятся в словарь клиентов в виде: логин: "данные для отправки сообщения".
# Когда подключается новый клиент, то после подключения всем клиентам рассылается обновлённый список логинов клиентов.
# Тех кто подключился.
#
# Также в самом начале запускается поток в котором происходит проверка на то что все подключившиеся клиенты ещё подключены.
# Если они вдруг отключились, то поток удалит данного клиента из словаря клиентов и отправит остальным кто ещё подключён
# список подключенных логинов клиентов.
#
# Также при отключении клиента завершится поток который ожидает от него сообщения.


def add_client():  # функция ожидания подключения новых клиентов
    global conn_addr
    while True:
        people_in_net_work = 'add_new_person|&'  # перенная в которую записываются логины подключённых клиентов через разделитель
        conn, addr = channel.accept()  # ожидание подключения нового клиента
        print('connect: ', addr)
        login = conn.recv(1024)  # приём логина того кто сейчас подключился
        conn_addr[login.decode('utf-8')] = conn  # запишем в словарь клиентов нового клиента: логин:"данные для отправки сообщений"
        for i in conn_addr.keys():  # наполним переменную логинами
            people_in_net_work += i + '|&'
        for i in conn_addr:  # каждому подключенному клиенту отправим список подключённых клиентов
            conn_addr[i].send(people_in_net_work.encode('utf-8'))
        globals()['client_{}'.format(login.decode('utf-8'))] = threading.Thread(target=communication, args=(conn, addr))  # запустим поток для входящих сообщений
        globals()['client_{}'.format(login.decode('utf-8'))].start()  # от подключившегося клиента


def communication(con, add):  # функция ожидания входящих сообщений. Запускается в отдельном потоке для каждого клиента
    global answer
    while True:
        try:  # это чтобы если клиент неожиданно отключится, бесконечный цикл завершится и поток остановится
            data = con.recv(1024).decode('utf-8')  # это как input. ждёт данные
            print(data)
            if data.split('|&')[0] != 'i_am_ok':
                conn_addr[data.split('|&')[0]].send(data.encode('utf-8'))
            else:
                if data.split('|&')[0] == 'i_am_ok':
                    answer = data.split('|&')[0]
        except ConnectionResetError:
            break


def check_man():  # функция проверки подключены ли ещё клиенты. запускается в отдельном потоке
    global answer
    while True:  # в бесконечном цикле кадому клиенту из словаря клиентов отправляется запрос
        if len(conn_addr) != 0:
            off_client = []
            flag_new_list_client = False
            for i in conn_addr.keys():
                try:
                    conn_addr[i].send(b'are_you_ok|&')  # запрос
                    if answer == 'i_am_ok':  # если клиент не ответит то ...
                        print(i + ' Жив!')
                except ConnectionResetError:  # вслучае разрыва соединения
                    off_client += [i]  # добавим в специальную переменную логины тех кто отключился
                    flag_new_list_client = True  # возведём флаг для отправки нового списка клиентов тем кто не отключился
                    print(i + ' отвалился. Slacker')
            for i in off_client:  # почистим словарь
                conn_addr.pop(i)
            if flag_new_list_client is True:  # если флаг тру, то отправим всем остальным новый список клиентов
                people_in_net_work = 'add_new_person|&'
                if len(conn_addr) > 0:
                    for i in conn_addr.keys():
                        people_in_net_work += i + '|&'
                    for i in conn_addr:
                        conn_addr[i].send(people_in_net_work.encode('utf-8'))
                flag_new_list_client = False
            print(conn_addr.keys())
        time.sleep(10)  # усыпим поток на время


conn_addr = dict()
channel = socket.socket()
channel.bind(('', 54125))
channel.listen(10)
answer = ''
check_client = threading.Thread(target=check_man)
check_client.start()
add_client()
