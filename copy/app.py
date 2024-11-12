import sqlite3
import json
from datetime import datetime  # datetime 삽입
from flask import Flask, render_template, request, redirect, jsonify  # 노드에서 인포트해오는거랑 똑같은거

app = Flask(__name__)  # flask를 앱이라는 변수에 넣어놓은거

# 127.0.0.1/ @app을 사용하는데 라우팅을 하겠다 어디로 라우팅? /로 라우팅하겠다 기본페이지로 들어왔을때 아래에 있는 함수를 실행하겠다. /로 끝나는 그 시점에 아래 함수 실행을 하겠다(=이 템플릿을 라우팅하겠다) //아래 페이지를 라우팅하겠다.


@app.route('/')
def home():
    conn = sqlite3.connect('postData.db')  # db연결(접속)
    conn.row_factory=sqlite3.Row
    cursor = conn.cursor()  # sql 쿼리 수행을 위해 필요한 객체
    cursor.execute("SELECT * FROM T_Board where delDT is null ORDER BY regDT DESC")
    data_list = cursor.fetchall()
    # sqlite랑 연결을 해서 rendering 할때 데이터를 같이 뿌려준다.
    # render_template <- 화면을 띄울때 필요한 함수
    return render_template('blog.html', data_list=data_list)


@app.route('/write')  # 페이지 뿌려주는 용도
def write():
    return render_template('blog_write.html')

@app.route('/rp')  # 페이지 뿌려주는 용도
def rp():
    conn = sqlite3.connect('postData.db')  # db연결(접속)
    cursor = conn.cursor()  # sql 쿼리 수행을 위해 필요한 객체
    cursor.execute("SELECT * FROM T_Board where delDT is not null ORDER BY regDT DESC")
    data_list = cursor.fetchall()
    # sqlite랑 연결을 해서 rendering 할때 데이터를 같이 뿌려준다.
    # render_template <- 화면을 띄울때 필요한 함수
    return render_template('blog_rp.html', data_list=data_list)


@app.route('/api/write2', methods=['POST'])
def api_test():
    # param = json.loads(request.get_data(), encoding='utf-8')
    title = request.form["Title"]
    contents = request.form["Contents"]

    # return "".format(title,contents)

    conn = sqlite3.connect('postData.db')
    cursor = conn.cursor()

    data_list = (None, title, contents, datetime.today(), None)

    cursor.execute("INSERT INTO T_Board VALUES(?,?,?,?,?);", data_list)

    conn.commit()

    return "Success"


@app.route('/edit/<idx>')
def edit(idx):
    conn = sqlite3.connect('postData.db')  # postdb 연결
    cursor = conn.cursor()
    query = "SELECT * FROM T_Board WHERE boardIdx = '{}'".format(idx)
    data_list = cursor.execute(query)
    data_list = cursor.fetchall()

    return render_template("blog_edit.html", title=data_list[0][1], contents=data_list[0][2], index=data_list[0][0]
                           )


@app.route('/api/edit', methods=['POST'])
def api_edit():

    edit_title = request.form["Title"]
    edit_contents = request.form["Contents"]
    edit_idx = request.form["Idx"]

    conn = sqlite3.connect('postData.db')
    cursor = conn.cursor()
    query = "UPDATE T_Board SET title='{}', contents='{}' WHERE boardIdx='{}'".format(
        edit_title, edit_contents, edit_idx)

    # (boardIdx가 {idx}인 게시물의 제목,내용을 불러오는 함수...?)
    cursor.execute(query)
    conn.commit()

    return "Edit Success!!"

  
@app.route('/check/<idx>') 
def check(idx):
    conn = sqlite3.connect('postData.db')  # postdb 연결
    cursor = conn.cursor()
    query = "SELECT * FROM T_Board WHERE boardIdx = '{}'".format(idx)
    data_list = cursor.execute(query)
    data_list = cursor.fetchall()

    return render_template("blog_check.html", title=data_list[0][1], contents=data_list[0][2], index=data_list[0][0]
                            )


@app.route('/search/<keyword>')
def api_search(keyword):
    conn = sqlite3.connect('postData.db')  # db연결(접속)
    conn.row_factory=sqlite3.Row
    cursor = conn.cursor()  # sql 쿼리 수행을 위해 필요한 객체
    query = "SELECT * FROM T_Board where delDT is null and title like '%{}%' ORDER BY regDT DESC".format(keyword)
    cursor.execute(query)
    data_list = cursor.fetchall()
    # sqlite랑 연결을 해서 rendering 할때 데이터를 같이 뿌려준다.
    # render_template <- 화면을 띄울때 필요한 함수
    return render_template('blog_search.html', data_list=data_list)

@app.route('/api/remove', methods=['POST'])
def api_remove():

    edit_idx = request.form["Idx"]

    conn = sqlite3.connect('postData.db')
    cursor = conn.cursor()
    query = "UPDATE T_Board SET delDT = datetime() WHERE boardIdx='{}'".format(edit_idx)

    cursor.execute(query)
    conn.commit()

@app.route('/api/restore', methods=['POST'])
def api_restore():

    idx = request.form["Idx"]

    conn = sqlite3.connect('postData.db')
    cursor = conn.cursor()
    query = "UPDATE T_Board SET delDT = null WHERE boardIdx='{}'".format(idx)

    cursor.execute(query)
    conn.commit()


@app.route('/riot')  
def result():
    return render_template('blog_riot.html')

@app.route('/search', methods=['POST'])
def search():
    summoner_name = request.form['summoner_name']
    api_key = 'RGAPI-18965d80-71d0-4119-b897-cd79a9ad5528'
    region = 'kr'  # Example: 'na1' for North America
    url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        summoner_data = response.json()
        summoner_id = summoner_data['id']
        match_url = f'https://{region}.api.riotgames.com/lol/match/v4/matchlists/by-account/{summoner_id}?api_key={api_key}'
        match_response = requests.get(match_url)
        if match_response.status_code == 200:
            match_data = match_response.json()
            matches = match_data['matches']
            return render_template('riot_result.html', summoner_name=summoner_name, matches=matches)
        else:
            return "Error fetching match data"
    else:
        return "Summoner not found"




if __name__ == "__main__":
    app.run(port=4005, debug=True)
