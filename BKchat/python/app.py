from flask import Flask,render_template,request,redirect,url_for,session,jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime
import requests
from flask_socketio import SocketIO,emit,send
url = 'http://lingpu.im.tku.edu.tw:35130/api/chat'

app=Flask(__name__)

app.secret_key='BK'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='bk_japanese'
mysql=MySQL(app)
socketio = SocketIO(app)
# 登入

@app.route("/login",methods=['GET','POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE Email = % s AND Password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['User_id'] = user['User_id']
            session['name'] = user['UserName']
            session['email'] = user['Email']
            mesage = "True"
           
            
            return render_template('beginpage.html', mesage = mesage)
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage = mesage)

# 註冊
@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE Email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)
# 登出(未製作)
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('User_id', None)
    session.pop('email', None)
    return redirect('/')


#機器人對話
@app.route("/get",methods=["GET","POST"])
def get():
    msg=request.form["msg"]
    getchatmsg(msg)
    if "拆解" in msg or "解析" in msg:
        new_msg=keep_text_within_quotes(msg)
        chat_respone(new_msg,4)
    else:
        chat_respone(msg,0)
    return ""
def getchatmsg(msg):#使用者訊息回傳至聊天室
    socketio.emit('send_prompt', {'prompt': msg})
    return ""
def getchatresponse(response,zh_response):#機器人訊息回傳至聊天室
    socketio.emit('send_Expample', {'Example': response,'Zh_Example':zh_response})
    return ""
def get_anylze(anylze_response):
    socketio.emit('get_analyze',{'response':anylze_response})
    return""
def chat_completion(prompt, model_engine="gpt35", temperature=0.9, top_p=0.95, max_tokens=1024):
    args = {
        'prompt': prompt,
        'model_engine': model_engine,
        'temperature': temperature,
        'top_p': top_p,
        'max_tokens': max_tokens
    }
    response = requests.post(url, json=args)
    response_json = response.json()
    message = response_json['message']
    return message
def get_prompt(prompt_type, content=""):
    if prompt_type == 1:
        return f"請產生包含「{content}」的單字。"
    elif prompt_type == 2:
        return f"{content}，只需要一句日文例句，不需要補充解釋和翻譯。"
    elif prompt_type == 3:
        return f"「{content}」請自行判斷並解析以上日文句子中使用的單字、文法。例句不需要中文翻譯。例句不需要例句解析。只能用繁體中文回答。不要重複例句內容。若為多個句子需個別解析各個句子。嚴格遵守以下範例格式不要添加任何額外的文字或解析或這句話的意思:「單字解析：<br>- 單字1(若單字為漢字則加上日文平假名，反之若單字為平假名或片假名則什麼都不加，包括漢字、平假名、片假名和中文翻譯。)：單字1詳細解析<br>- 單字2(若單字為漢字則加上日文平假名，反之若單字為平假名或片假名則什麼都不加，包括漢字、平假名、片假名和中文翻譯。)：單字2詳細解析。<br>- 單字3(若單字為漢字則加上日文平假名，反之若單字為平假名或片假名則什麼都不加，包括漢字、平假名、片假名和中文翻譯。)：單字3詳細解析。<br><br>文法解析：<br>- 文法1：文法1解析<br>- 文法2：文法2解析<br>- 文法3：文法3解析<br>。」。嚴格遵守以上範例格式不要添加任何額外的文字或解析或這句話的意思"
    #f"只能用中文回答。「{content}」。請透過條列的方式解析以上日文句子中使用的單字、文法，不需要中文翻譯。若為一個例句或「A は B ですか？」的例句時使用以下範例格式A:「單字解析：<br>- 單字1：單字1解析<br>- 單字2：單字2解析。<br>- 單字3：單字3解析。<br>- 單字4：單字4解析。<br>- 單字5：單字5解析。<br><br>文法解析：<br>- 文法1：文法1解析<br>- 文法2：文法2解析<br>- 文法3：文法3解析<br>- 文法4：文法4解析<br>- 文法5：文法5解析」。若為多個例句則不使用使用範例格式A，改成使用以下範例格式B，「A は B ですか？」的例句則不使用使用範例格式B:「例句1.<br>單字解析：<br>- 單字1：單字1解析<br>- 單字2：單字2解析。<br>- 單字3：單字3解析。<br>- 單字4：單字4解析。<br>- 單字5：單字5解析。<br><br>文法解析：<br>- 文法1：文法1解析<br>- 文法2：文法2解析<br>- 文法3：文法3解析<br>- 文法4：文法4解析<br>- 文法5：文法5解析<br>例句2.<br>單字解析：<br>- 單字1：單字1解析<br>- 單字2：單字2解析。<br>- 單字3：單字3解析。<br>- 單字4：單字4解析。<br>- 單字5：單字5解析。<br><br>文法解析：<br>- 文法1：文法1解析<br>- 文法2：文法2解析<br>- 文法3：文法3解析<br>- 文法4：文法4解析<br>- 文法5：文法5解析<br>例句3.<br>單字解析：<br>- 單字1：單字1解析<br>- 單字2：單字2解析。<br>- 單字3：單字3解析。<br>- 單字4：單字4解析。<br>- 單字5：單字5解析。<br><br>文法解析：<br>- 文法1：文法1解析<br>- 文法2：文法2解析<br>- 文法3：文法3解析<br>- 文法4：文法4解析<br>- 文法5：文法5解析」。"
    elif prompt_type == 4:
        return f"「{content}」翻譯成繁體中文，不需要補充解釋。"
    else:
        return ""
def chat_respone(text,content_type):
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        match content_type:
            case 1:
                new_text=get_prompt(1,text)
            case 2:
                new_text=get_prompt(2,text)
            case 3:
                new_text=text[2]
                text=text[1]
            case 4:
                new_text=get_prompt(3,text)
            case _:
                new_text=text
        
        if content_type==4:
            response=chat_completion(new_text)
            formatted_response=format_anylze(response)
        else:
            sentences = new_text.split('\n')
            jp_prompt = "你是一位日語母語者，你只能使用日文回答所有對話，不可以使用英文或中文'"+ get_prompt(5) +'\n'.join([f"{i + 1}.{sentence}" for i, sentence in enumerate(sentences)])+"'"
            response=chat_completion(jp_prompt)
            if content_type==2 or content_type==3:
                anylize_response=chat_completion(get_prompt(3,response))
                get_anylze(format_anylze(anylize_response))
            formatted_response = format_response(response)
        zh_response=chat_translate_respone(get_prompt(4,response))
        format_zh_response=format_response(zh_response)
        getchatresponse(formatted_response,format_zh_response)
        if 'User_id' in session and session['User_id']:
            Chat_history(text,current_time,response,format_zh_response)
            
        return ""
def chat_translate_respone(text):
    response=chat_completion(text)
    return response
def format_response(response):
    response_lines = response.split('\n')
    formatted_response = '<br>'.join(response_lines)
    return formatted_response
def format_anylze(response):
    response_lines = response.split('\n')
    formatted_response = '<br>'.join(response_lines)
    return formatted_response
def keep_text_within_quotes(text):
    result = re.findall(r'\"(.+?)\"', text)
    new_text = ' '.join(result)
    return new_text
def Chat_history(content,senttime,response,zh_response):
    User_ID=session['User_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO chat_history VALUES (% s, % s, % s, % s,% s)', (User_ID,senttime, content,response,zh_response ))
    mysql.connection.commit()
    return 0
# def get_latest_messages():
#     if 'User_id' in session and session['User_id']:
#         User_ID = int(session['User_id'])
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT * FROM chat_history WHERE User_id = % s ORDER BY Message_Date_Time ASC LIMIT 50', (User_ID, ))
#         messages = cursor.fetchall()
#         data_list=[]
#         for entry in messages:
#             question=entry['User_Content']
#             answer=entry['Bot_Response']
#             jsonl_data = {
#             "messages": [
#                 {"role": "system", "content": "你是一位日語母語者，你只能使用日文回答所有回答，不可以使用英文或中文"},
#                 {"role": "user", "content": question},
#                 {"role": "assistant", "content": answer}
#             ]
#         }
#             data_list.append(jsonl_data)
            
#         return data_list

def get_message():
    if 'User_id' in session and session['User_id']:
        User_ID=int(session['User_id'])
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM chat_history WHERE User_id = % s', (User_ID, ))
        messages=cursor.fetchall()
        return messages
    else:
        return ""
#單字例句
@app.route("/selectvoc",methods=["POST"])
def selectvoc():
    JapaneseVoc=request.form.get('voc')#選取的單字
    msg="請給我'"+JapaneseVoc+"'的例句"
    getchatmsg(msg)
    chat_respone(msg,2)
    
    return ""
#文法例句
@app.route("/getGrammer",methods=["POST"])
def getGrammer():
    search_index=request.form.get("search_index")
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM grammer_prompt WHERE Grammer_Index = % s', (search_index, ))
    grammer_prompt=cursor.fetchone()
    grammer_Type = grammer_prompt.get('Grammer_Type')
    grammer_Prompt=grammer_prompt.get('Grammer_Prompt')
    msg="請給我'"+grammer_Type+"'的例句"
    grammer_dict={1:msg,2:grammer_Prompt}
    getchatmsg(msg)
    chat_respone(grammer_dict,3)
    return ""


#頁面
@app.route("/")
@app.route("/begin")
def Homepage():
    if 'User_id' in session and session['User_id']:
        return render_template("beginpage.html",mesage='True')
    else:
        return render_template("beginpage.html",mesage='False')

@app.route("/chatbot")
def chatbot():
    messages=get_message()
    return render_template("chatbot.html", messages=messages)

@app.route("/50")
def letter():
    if 'User_id' in session and session['User_id']:
        return render_template("50.html",mesage='True',address='/50')
    else:
        return render_template("50.html",mesage='False')
@app.route("/map")
def jmap():
    if 'User_id' in session and session['User_id']:
        return render_template("map.html",mesage='True',address='/map')
    else:
        return render_template("map.html",mesage='False')


@app.route("/N5voc")
def N5voc():
    page='a'
    if 'User_id' in session and session['User_id']:
        return render_template("N5voc.html",mesage='True',address='/N5voc')
    else:
        return render_template("N5voc.html",mesage='False')
@app.route("/NewTable",methods=["GET","POST"])
def NewTabke():
    if request.method=='POST':
        page = request.form.get('char')
    return render_template("/N5vocTable.html",Voc=getvoc(page))
@app.route('/getvoc')
def getvoc(page):
    VOC_Result = {}
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM voc WHERE Page_index=% s',(page,))
    VOC_ALL = cursor.fetchall()
    for row in VOC_ALL:
        char = row['Voc_index']
        if char not in VOC_Result:
            VOC_Result[char] = []
        VOC_Result[char].append(row)
    return VOC_Result



@app.route("/N5gra")
def N5gra():
    if 'User_id' in session and session['User_id']:
        return render_template("N5gra.html",mesage='True',address='/N5gra')
    else:
        return render_template("N5gra.html",mesage='False')
@app.route("/story")
def story():
    if 'User_id' in session and session['User_id']:
        return render_template("story.html",mesage='True',address='story')
    else:
        return render_template("story.html",mesage='False')
@app.route("/ReadAloud")
def read():
    if 'User_id' in session and session['User_id']:
        return render_template("ReadAloud.html",mesage='True',address='/ReadAloud')
    else:
        return render_template("ReadAloud.html",mesage='False')

if __name__=='__main__':
    
    
    socketio.run(app,debug=True,host='0.0.0.0',port='5000')

