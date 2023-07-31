# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
from markupsafe import Markup
import openai
import markdown
import markdown.extensions.fenced_code
import markdown.extensions.codehilite
import mysql.connector

# 更换代理地址
import os
os.environ["http_proxy"] = "10.***********"
os.environ["https_proxy"] = "10.***********"

openai.api_key = 'sk-dLjpRaIQdQXs35qBbkFJMbSHQurDv'
app = Flask(__name__)
messages = []

# 用于将对话历史存储到MySQL数据库
def save_to_database(user_input, ai_response):
    # 连接到MySQL数据库
    connection = mysql.connector.connect(host="localhost", user="root", password="1", database="1")
    cursor = connection.cursor()

    # 将对话历史插入到数据库中
    insert_query = "INSERT INTO conversation_history (user_input, model_response) VALUES (%s, %s)"
    data = (user_input, ai_response)
    cursor.execute(insert_query, data)

    # 提交更改并关闭连接
    connection.commit()
    cursor.close()
    connection.close()

# 用于删除历史对话记录
def clear_table(table_name):
    # 连接到MySQL数据库
    connection = mysql.connector.connect(host="localhost", user="root", password="1", database="1")
    cursor = connection.cursor()

    # 执行删除表格内容的SQL语句
    delete_query = f"DELETE FROM {table_name}"
    cursor.execute(delete_query)

    # 提交更改并关闭连接
    connection.commit()
    cursor.close()
    connection.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_input = request.form['user_input']
    # print(user_input)
    messages.append({'role': 'user', 'content': user_input})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    ai_response = completion.choices[0].message['content']
    # print(ai_response)
    messages.append({'role': 'assistant', 'content': ai_response})
    print(messages)
    save_to_database(user_input, ai_response)# 将对话历史存储到MySQL数据库
    return  Markup(markdown.markdown(ai_response, extensions=['fenced_code', 'codehilite']))

@app.route('/reset')
def reset():
    global messages
    messages = []
    table_name = "conversation_history"  # 替换为你要清空内容的表格名
    clear_table(table_name)# 清空数据库表格内容
    return "Conversation history has been reset."

if __name__ == '__main__':   
    app.run(debug=True)
