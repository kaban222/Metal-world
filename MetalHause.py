import datetime
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit
from threading import Thread
import json

###---база данных---###
Id_BD = {}
PF_BD = {}
BD = {}
def load():
    global BD, Id_BD, PF_BD
    try:
        f1 = open("BAZA/Persons.json", "r")
        BD = json.load(f1)
        f1.close()
    except:
        print("Не удалось загрузить файл  1")

    try:
        f1 = open("BAZA/idd.json", "r")
        Id_BD = json.load(f1)
        f1.close()
    except:
        print("Не удалось загрузить файл  2")

    try:
        f1 = open("BAZA/performers.json", "r")
        PF_BD = json.load(f1)
        f1.close()
    except:
        print("Не удалось загрузить файл  3")

def save():
    global BD
    f1 = open("BAZA/Persons.json", "w")
    json.dump(BD, f1, ensure_ascii=False)
    f1.close()

def save_id():
    global Id_BD
    f1 = open("BAZA/idd.json", "w")
    json.dump(Id_BD, f1, ensure_ascii=False)
    f1.close()

def save_PF():
    global PF_BD
    f1 = open("BAZA/performers.json", "w")
    json.dump(PF_BD, f1, ensure_ascii=False)
    f1.close()

L1 = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "_", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
def new_user(name, password):
    ready_name = name.lower()
    ready_password = password.lower()
    for _i in Id_BD.keys():
        if str(_i).lower() == ready_name:
            return "Имя уже занято!"

    for i in ready_name:
        if i not in L1:
            return "Введите корректное имя! A-Z, a-z, _, 0-9;"

    for i in ready_password:
        if i not in L1:
            return "Введите корректный пароль! A-Z, a-z, _, 0-9;"

    if len(name) < 3:
        return "маленькое имя. от 3 символов"
    elif len(name) > 18:
        return "большое имя. до 18 символов"

    if len(password) > 20:
        return "большой пароль. до 20 символов"
    elif len(password) < 8:
        return "маленький пароль. от 8 символов"

    id_pers = str(PF_BD["idd"])
    date_start = str(datetime.datetime.now()).split(".")[0]

    PF_BD["idd"] += 1
    PF_BD["kol"] += 1

    chat_id = str(PF_BD['chat_id'])
    PF_BD['chat_id'] += 1
    PF_BD["chats"][chat_id] = {"type":"self", "us1":"00000", "us2":f"{id_pers}", "messages":[{"from":"00000", "txt":"Добро пожаловать во вкладку избраное! Это ваш личный чат, можете писать в него например - заметки"}]}
    BD[id_pers] = {"name": name,
                   "password": password,
                   "ava": "defolt.jpg",
                   "chats": [chat_id],
                   "premium": False,
                   "admin": False,
                   "balance": 0,
                   "date": str(date_start)}

    Id_BD[name] = id_pers

    save()
    save_id()
    save_PF()
    return "0"



app = Flask('app')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, allow_unsafe_werkzeug=True)

@app.route('/')
def main():
    try:
        nm_session, ps_session = str(session['name']).split(":")
    except:
        nm_session = "None"

    if nm_session == "None" or nm_session not in Id_BD.keys():
        return render_template("reg.html")
    elif Id_BD[str(nm_session)] in BD.keys() and BD[Id_BD[str(nm_session)]]['password'] != ps_session:
        return render_template("reg.html")

    chats = BD[Id_BD[nm_session]]['chats']
    chat = []
    for i in chats:
        if PF_BD['chats'][i]['us1'] != Id_BD[nm_session]:
            id_sender = PF_BD['chats'][i]['us1']
            if id_sender == "00000":
                namers = "Избраное"
            else:
                namers = BD[id_sender]['name']
        else:
            id_sender = PF_BD['chats'][i]['us2']
            namers = BD[id_sender]['name']

        chat.append({"name":namers, "id":i, "ava": BD[id_sender]['ava']})

    return render_template("chat_hub.html", chat=chat)

@app.route('/linkHub', methods=['GET', 'POST'])
def GoToHub():
    try:
        nm_session, ps_session = str(session['name']).split(":")
    except:
        nm_session = "None"

    if nm_session == "None" or nm_session not in Id_BD.keys():
        return render_template("reg.html")
    elif Id_BD[str(nm_session)] in BD.keys() and BD[Id_BD[str(nm_session)]]['password'] != ps_session:
        return render_template("reg.html")

    chats = BD[Id_BD[nm_session]]['chats']
    chat = []
    for i in chats:
        if PF_BD['chats'][i]['us1'] != Id_BD[nm_session]:
            id_sender = PF_BD['chats'][i]['us1']
            if id_sender == "00000":
                namers = "Избраное"
            else:
                namers = BD[id_sender]['name']
        else:
            id_sender = PF_BD['chats'][i]['us2']
            namers = BD[id_sender]['name']

        chat.append({"name":namers, "id":i, "ava": BD[id_sender]['ava']})

    return render_template("chat_hub.html", chat=chat)

@app.route('/start_chat', methods=['GET', 'POST'])
def StartChat():
    try:
        nm_session, ps_session = str(session['name']).split(":")
    except:
        nm_session = "None"

    if nm_session == "None" or nm_session not in Id_BD.keys():
        return render_template("reg.html")
    elif Id_BD[str(nm_session)] in BD.keys() and BD[Id_BD[str(nm_session)]]['password'] != ps_session:
        return render_template("reg.html")

    idd = request.args.get('id')
    if idd == Id_BD[nm_session]:
        chats = BD[Id_BD[nm_session]]['chats']
        chat = []
        for i in chats:
            if PF_BD['chats'][i]['us1'] != Id_BD[nm_session]:
                id_sender = PF_BD['chats'][i]['us1']
                if id_sender == "00000":
                    namers = "Избраное"
                else:
                    namers = BD[id_sender]['name']
            else:
                id_sender = PF_BD['chats'][i]['us2']
                namers = BD[id_sender]['name']

            chat.append({"name":namers, "id":i, "ava": BD[id_sender]['ava']})
        return render_template("chat_hub.html", chat=chat)
    else:
        for i in BD[Id_BD[nm_session]]['chats']:
            if PF_BD['chats'][i]['us1'] == idd or PF_BD['chats'][i]['us2'] == idd:
                if PF_BD['chats'][i]['us1'] != Id_BD[nm_session]:
                    id_sender = PF_BD['chats'][i]['us1']
                    if id_sender == "00000":
                        namers = "Избраное"
                    else:
                        namers = BD[id_sender]['name']
                else:
                    id_sender = PF_BD['chats'][i]['us2']
                    namers = BD[id_sender]['name']

                return render_template("home.html", messages=PF_BD['chats'][i]['messages'], ava=BD[id_sender]['ava'], name=BD[id_sender]['name'], user_id=Id_BD[str(nm_session)], chat_id=i)

        #Создание чата!
        chat_id = str(PF_BD['chat_id'])
        PF_BD['chat_id'] += 1
        PF_BD["chats"][chat_id] = {"type":"PRIVATE", "us1":f"{Id_BD[nm_session]}", "us2":f"{idd}", "messages":[]}
        save_PF()

        BD[idd]['chats'].insert(0, chat_id)
        BD[Id_BD[nm_session]]['chats'].insert(0, chat_id)
        save()

        if PF_BD['chats'][chat_id]['us1'] != Id_BD[nm_session]:
            id_sender = PF_BD['chats'][chat_id]['us1']
            if id_sender == "00000":
                namers = "Избраное"
            else:
                namers = BD[id_sender]['name']
        else:
            id_sender = PF_BD['chats'][chat_id]['us2']
            namers = BD[id_sender]['name']

        return render_template("home.html", messages=PF_BD['chats'][chat_id]['messages'], ava=BD[id_sender]['ava'], name=BD[id_sender]['name'], user_id=Id_BD[str(nm_session)], chat_id=chat_id)

@app.route('/chat_hub', methods=["GET", "POS"])
def open_chat_hub():
    try:
        nm_session, ps_session = str(session['name']).split(":")
    except:
        nm_session = "None"

    if nm_session == "None" or nm_session not in Id_BD.keys():
        return render_template("reg.html")
    elif Id_BD[str(nm_session)] in BD.keys() and BD[Id_BD[str(nm_session)]]['password'] != ps_session:
        return render_template("reg.html")

    chats = BD[Id_BD[nm_session]]['chats']
    chat = []
    for i in chats:
        if PF_BD['chats'][i]['us1'] != Id_BD[nm_session]:
            id_sender = PF_BD['chats'][i]['us1']
            if id_sender == "00000":
                namers = "Избраное"
            else:
                namers = BD[id_sender]['name']
        else:
            id_sender = PF_BD['chats'][i]['us2']
            namers = BD[id_sender]['name']

        chat.append({"name":namers, "id":i, "ava": BD[id_sender]['ava']})

    return render_template("chat_hub.html", chat=chat)

@app.route('/openchat', methods=['GET', 'POST'])
def OpenChat():
    try:
        nm_session, ps_session = str(session['name']).split(":")
    except:
        nm_session = "None"

    if nm_session == "None" or nm_session not in Id_BD.keys():
        return render_template("reg.html")
    elif Id_BD[str(nm_session)] in BD.keys() and BD[Id_BD[str(nm_session)]]['password'] != ps_session:
        return render_template("reg.html")

    idd = request.args.get('chat_mPRTID')

    if PF_BD['chats'][idd]['us1'] != Id_BD[nm_session]:
        id_sender = PF_BD['chats'][idd]['us1']
        if id_sender == "00000":
            namers = "Избраное"
        else:
            namers = BD[id_sender]['name']
    else:
        id_sender = PF_BD['chats'][idd]['us2']
        namers = BD[id_sender]['name']

    return render_template("home.html", messages=PF_BD['chats'][idd]['messages'], ava=BD[id_sender]['ava'], name=BD[id_sender]['name'], user_id=Id_BD[str(nm_session)], chat_id=idd)

@app.route('/linkReg', methods=['GET', 'POST'])
def GoToReg():
    try:
        nm_session, ps_session = str(session['name']).split(":")
    except:
        nm_session = "None"

    if nm_session == "None" or nm_session not in Id_BD.keys():
        return render_template("reg.html")
    elif Id_BD[str(nm_session)] in BD.keys() and BD[Id_BD[str(nm_session)]]['password'] != ps_session:
        return render_template("reg.html")

    return render_template("reg.html")

@app.route('/linkVhod', methods=['GET', 'POST'])
def GoToVhod():
    try:
        nm_session, ps_session = str(session['name']).split(":")
    except:
        nm_session = "None"

    return render_template("vhod.html")

@app.route('/openMenu', methods=['GET', 'POST'])
def GoToMenu():
    try:
        nm_session, ps_session = str(session['name']).split(":")
    except:
        nm_session = "None"

    if nm_session == "None" or nm_session not in Id_BD.keys():
        return render_template("reg.html")
    elif Id_BD[str(nm_session)] in BD.keys() and BD[Id_BD[str(nm_session)]]['password'] != ps_session:
        return render_template("reg.html")

    return render_template("Mypage.html", ava=BD[Id_BD[nm_session]]['ava'], username=BD[Id_BD[nm_session]]['name'])

@app.route('/linkFind', methods=['GET', 'POST'])
def GoToFind():
    users = []
    for i, y in BD.items():
        if i != "00000":
            users.append({"name":y["name"], "ava":y["ava"], "idd":i})

    return render_template("find.html", users=users)

@app.route('/reg', methods=['GET', 'POST'])
def registartion():
    name = request.form['name']
    password = request.form['password']

    status = new_user(name, password)
    if status == "0":
        session['name'] = str(name) + ":" + str(password)

        chats = BD[Id_BD[name]]['chats']
        chat = []
        for i in chats:
            if PF_BD['chats'][i]['us1'] != Id_BD[name]:
                id_sender = PF_BD['chats'][i]['us1']
                if id_sender == "00000":
                    namers = "Избраное"
                else:
                    namers = BD[id_sender]['name']
            else:
                id_sender = PF_BD['chats'][i]['us2']
                namers = BD[id_sender]['name']

            chat.append({"name":namers, "id":i, "ava": BD[id_sender]['ava']})

        return render_template("chat_hub.html", chat=chat)
    else:
        return render_template("reg.html", error=status)

@app.route('/login', methods=['GET', 'POST'])
def vhod():
    name = request.form['name']
    password = request.form['password']

    if name not in Id_BD.keys():
        return render_template("vhod.html", error="Это имя не зарегестрировано")
    if BD[Id_BD[name]]['password'] != password:
        return render_template("vhod.html", error="неверно введено имя или пароль")
    else:
        session['name'] = str(name) + ":" + str(password)
        chats = BD[Id_BD[name]]['chats']
        chat = []
        for i in chats:
            if PF_BD['chats'][i]['us1'] != Id_BD[name]:
                id_sender = PF_BD['chats'][i]['us1']
                if id_sender == "00000":
                    namers = "Избраное"
                else:
                    namers = BD[id_sender]['name']
            else:
                id_sender = PF_BD['chats'][i]['us2']
                namers = BD[id_sender]['name']

            chat.append({"name":namers, "id":i, "ava": BD[id_sender]['ava']})

        return render_template("chat_hub.html", chat=chat)


####для чата
@socketio.on('message')
def handle_message(message):
    try:
        nm_session, ps_session = str(session['name']).split(":")
    except:
        nm_session = "None"

    if nm_session == "None" or nm_session not in Id_BD.keys():
        return render_template("reg.html")
    elif Id_BD[str(nm_session)] in BD.keys() and BD[Id_BD[str(nm_session)]]['password'] != ps_session:
        return render_template("reg.html")

    print(message)
    txt, user, chat = str(message).split(":::::")
    id_user = Id_BD[nm_session]

    chek = False
    for i in txt:
        if i != " " and i != "" and i != " ":
            chek = True
            break

    if chat not in BD[Id_BD[nm_session]]['chats']:
        pass
    else:
        if chek:
            if len(txt) > 2025:
                pass
            else:
                PF_BD['chats'][chat]['messages'].append({"from":id_user, "txt":txt})
                save_PF()
                msg = {"txt":txt, "from":id_user, "chat_id":chat}
                emit('message', msg, broadcast=True)

def keep_alive():
    socketio.run(app, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    load()
    keep_alive()