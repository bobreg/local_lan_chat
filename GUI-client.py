import tkinter
import socket
import os
import threading
from tkinter import messagebox
import sys
import winsound
import shutil

# GUI клиента реализован при помощи Tkinter. Сама программа многооконна (главное окно + окна чатов)
# Из-за этого многие элементы окон объявленны в виде  globals()['text_dialog{}'.format(send_to_who)]
# Это позволяет привязать элемент окна к конкретному чату и с точки зрения программы похожие элементы не будут
# иметь одинаковые имена


def send(who):  # функция посыла сообщения кому-нибудь
    mail = who + '|&' + globals()['entry_dialog{}'.format(who)].get(1.0, 'end') + '|&' + login  # соберём сообщение из (кому посылаем + разделитель + сообщение которое возьмём из Entry окна + от кого)
    globals()['text_dialog{}'.format(who)].insert('end', 'My message' + ': ' + globals()['entry_dialog{}'.format(who)].get(1.0, 'end') + '\n')  # то что отправили отобразим в окне
    with open('.\\history\\{}.txt'.format(who), 'a') as history:  # запись того что отправили в текстовый файл
        history.write('My message' + ': ' + globals()['entry_dialog{}'.format(who)].get(1.0, 'end') + '\n')
    globals()['entry_dialog{}'.format(who)].delete(1.0, 'end')  # почистим поле ентри
    channel.send(mail.encode('utf-8'))  # отправляем собранное сообщение


def recvs():
    global data  # дата - переменная которая хранит в себе то что прислал сервер
    while True:  # в бесконечном цикле мониторим сообщения сервера
        try:
            data = channel.recv(1024).decode('utf-8')  # если что-то приходит, то декодируес это
            data = data.split('|&')  # разбираем сообщение по разделителю
            print(data)
        except ConnectionResetError:
            messagebox.showwarning('(¬_¬)', message='Сервер недоступен.\n\n(ノ º□º)ノ ⌒ ┴----┴')
            os._exit(0)  # если сервер недоступен, завершим работу клиента


def check_new_message():  # функция, которая относится непосредственно к окну чата с кем-то
    global data
    window_client.after(100, check_new_message)  # данную функцию перезапускаем раз в 100 мс
    if data != '':  # если есть сообщение от сервера, то
        if data[0] == 'add_new_person':  # если первый элемент сообщения add_new_person
            list_contacts.delete(0, 'end')  # очистим список людей которые подключены к серверу
            for i in data[1:-1]:  # срез т.к. в конец списока людей добавляется пустая строка
                list_contacts.insert(0, i)  # после add_new_person далее по списоку все кто подключён к серверу. перепишем заново список контактов
        elif data[0] == 'are_you_ok':  # are_you_ok (первый элемент в сообщении) это сообщение от сервера, спрашивает в сети ли мы и живы ли мы
            channel.send(b'i_am_ok|&')  # отправим ответ
        else:
            try:  # если пришло от кого-нибудь сообщение, а окно чата не открыто, то оно откроется и там отобразится сообщение
                globals()['text_dialog{}'.format(data[2])].insert('end', data[2] + ': ' + data[1] + '\n', 'right')
                with open('.\\history\\{}.txt'.format(data[2]), 'a') as history:
                    history.write(data[2] + ': ' + data[1] + '\n')
                if flag_icq.get() == 1:
                    winsound.PlaySound('icq.wav', winsound.SND_FILENAME)
            except KeyError:
                message_window(data[2])
                globals()['text_dialog{}'.format(data[2])].insert('end', data[2] + ': ' + data[1] + '\n', 'right')
                with open('.\\history\\{}.txt'.format(data[2]), 'a') as history:
                    history.write(data[2] + ': ' + data[1] + '\n')
                if flag_icq.get() == 1:
                    winsound.PlaySound('icq.wav', winsound.SND_FILENAME)
            except tkinter._tkinter.TclError:
                message_window(data[2])
                globals()['text_dialog{}'.format(data[2])].insert('end', data[2] + ': ' + data[1] + '\n', 'right')
                with open('.\\history\\{}.txt'.format(data[2]), 'a') as history:
                    history.write(data[2] + ': ' + data[1] + '\n')
                if flag_icq.get() == 1:
                    winsound.PlaySound('icq.wav', winsound.SND_FILENAME)
        data = ''  # очистим переменную дата и будем ждать новое сообщение от сервера


def message_window(send_to_who):  # функция создания окна сообщения и переменная которая хранит в себя выделенного персонажа из контакт листа
    print(send_to_who)
    dialog_window = tkinter.Tk()  # создадим окно для отправки сообщения
    dialog_window.title('dialog_with_{}'.format(send_to_who))
    dialog_window.geometry('420x650')

    frame_text_dialog = tkinter.Frame(dialog_window, height=30, width=55)  # фрейм для того чтобы прикрутить в него text поле и скролл
    frame_text_dialog.place(x=0, y=0)

    globals()['text_dialog{}'.format(send_to_who)] = tkinter.Text(frame_text_dialog, bg='gray92', width=50, height=30, wrap='word')  # поле где выводится история переписки
    globals()['text_dialog{}'.format(send_to_who)].pack(side='left')
    globals()['text_dialog{}'.format(send_to_who)].tag_configure('left', justify='left')  # пара тегов в которых описано свойство для сдвига текста вправо или лево
    globals()['text_dialog{}'.format(send_to_who)].tag_configure('right', justify='right')

    scroll_text = tkinter.Scrollbar(frame_text_dialog, command=globals()['text_dialog{}'.format(send_to_who)].yview)
    scroll_text.pack(side='right', fill='y')
    globals()['text_dialog{}'.format(send_to_who)]['yscrollcommand'] = scroll.set
    scroll_text['command'] = globals()['text_dialog{}'.format(send_to_who)].yview  # тут не ставить скобки после yview. не будет работать!

    globals()['entry_dialog{}'.format(send_to_who)] = tkinter.Text(dialog_window, width=50, height=5, relief='groove')  # поле ввода текста
    globals()['entry_dialog{}'.format(send_to_who)].place(x=0, y=500)
    globals()['button_dialog{}'.format(send_to_who)] = tkinter.Button(dialog_window, text='Отправить', command=lambda: send(send_to_who))  # кнопка отправки сообщения (вызывает функцию send и передаёт ей send_to_who)
    globals()['button_dialog{}'.format(send_to_who)].place(x=100, y=600)

    globals()['button_clear_history_with{}'.format(send_to_who)] = tkinter.Button(dialog_window, text='Удалить историю', command=lambda: os.remove('.\\history\\'+send_to_who+'.txt'))
    globals()['button_clear_history_with{}'.format(send_to_who)].place(x=300, y=600)

    try:
        os.makedirs('history')  # создадим папку в которую будем сохранять историю
    except FileExistsError:
        pass
    if os.path.exists('.\\history\\{}.txt'.format(send_to_who)) is True:
        with open('.\\history\\{}.txt'.format(send_to_who)) as history:
            for i in history:
                if i.split(':')[0] == 'My message':
                    globals()['text_dialog{}'.format(send_to_who)].insert('end', i, 'left')
                else:
                    globals()['text_dialog{}'.format(send_to_who)].insert('end', i, 'right')
    else:
        with open('.\\history\\{}.txt'.format(send_to_who), 'w') as history:
            pass
        # globals()['history_wiht_{}'.format(send_to_who)] = open('.\\history\\{}.txt'.format(send_to_who), 'w')


# ---------------------------Создание главного окна----------------------------
window_client = tkinter.Tk()
window_client.title('Ъ')
window_client.geometry('140x470')

label_text = tkinter.Label(window_client, text='Контакты\nв сети', font='Arial 10')
label_text.place(x=30, y=3)

frame_list_contacts = tkinter.Frame(window_client, height=20, width=25)
frame_list_contacts.place(x=0, y=40)

list_contacts = tkinter.Listbox(frame_list_contacts, height=15, width=20, selectmode='single')
list_contacts.pack(side='left')

scroll = tkinter.Scrollbar(frame_list_contacts, command = list_contacts.yview)
scroll.pack(side='right', fill='y')
list_contacts['yscrollcommand'] = scroll.set
scroll['command'] = list_contacts.yview  # тут не ставить скобки после yview. не будет работать!

button1 = tkinter.Button(window_client, text='Написать', command=lambda: message_window(list_contacts.get(list_contacts.curselection()[0])))  # Кнопка открытия чата с выделенным персонажем
button1.place(x=30, y=300)                                                                                                                    # не открывать два окна одновременно с одним
                                                                                                                                            # человеком
label_text3 = tkinter.Label(window_client, text='Ъуъ - Посланник!\n', font='Arial 11', relief='groove')
label_text3.place(x=5, y=415)

label_text2 = tkinter.Label(window_client, text='от Alex_Chel_man', font='Arial 7')
label_text2.place(x=20, y=435)

flag_icq = tkinter.IntVar()

icq_check = tkinter.Checkbutton(window_client, text='Вкл звук', variable=flag_icq)
icq_check.place(x=20, y=380)

button1_clear_history = tkinter.Button(window_client, text='Очистить всю\nисторию', command=lambda : shutil.rmtree('.\\history', ignore_errors=False, onerror=None))
button1_clear_history.place(x=20, y=330)

# ------------------------Сокет---------------------------------
people = []
channel = socket.socket()
try:
    #channel.connect(('10.81.27.115', 54125))
    channel.connect(('172.20.194.242', 54125))
except ConnectionRefusedError:
    messagebox.showwarning('(¬_¬)', message='Сервер недоступен.\n\n(ノ º□º)ノ ⌒ ┴----┴')
    os._exit(0)  # если сервер недоступен, завершим работу клиента
login = os.getlogin()  # возьмёт из системы наш логин для отправки серверу
channel.send(login.encode('utf-8'))
data = channel.recv(1024).decode('utf-8')
data = data.split('|&')
print(data)
for i in data[1:-1]:  # срез т.к. в конец списока людей добавляется пустая строка
    list_contacts.insert(0, i)
data = ''
recvfrom = threading.Thread(target=recvs)  # запуск в параллельном потоке ожидание сообщений от сервера
recvfrom.start()
window_client.after_idle(check_new_message)  # запуск в другом паралельном потоке (метод after tkinter) функции которая следит за переменной data и в случае если data
                                             # не пуста то сообщение будет разобрано и обработано
window_client.protocol('WM_DELETE_WINDOW', lambda :os._exit(0))  # если главное окно закроется по крестику, то выполнение программы остановится
window_client.mainloop()
