from flask import Flask, request, jsonify, make_response, Response
from flask_cors import CORS
import psycopg2
import os
import json
import requests

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

CORS(app)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8080')
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def send_simple_message(data):
    return requests.post(
        "https://api.mailgun.net/v3/sandbox018225051754486dac08e65225831082.mailgun.org/messages",
        auth=("api", "key-4ba62a3bddb3d4369784ab95f9a56810"),
        data={"from": data['customerName']+" "+data['customerEmail'],
              "to": "Bowen <bowenzhou222@gmail.com>",
              "subject": data['customerSubject'],
              "text": data['customerMessage']})

@app.route('/send', methods=['POST'])
def send_messages():    
    data = json.loads(request.data.decode('ascii'))
    customer_name = data['customerName']
    customer_email = data['customerEmail']
    customer_phone_number = data['customerPhoneNumber']
    customer_subject = data['customerSubject']
    customer_message = data['customerMessage']
    print(request.cookies)
    if len(customer_email) == 0:
        resp = Response('Please provide your email.', status=400)
        return resp

    if len(customer_message) == 0:
        resp = Response('Please do not send empty message', status=400)
        return resp

    mailgun_response = send_simple_message(data)

    if not mailgun_response.ok:
        resp = Response('Error when sending message. Please try again later.', status=mailgun_response.status_code)
        return resp

    conn = psycopg2.connect(
        database='cammy',
        user='postgres',
        host='127.0.0.1',
    )

    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (name, email, phone_number, subject, message) VALUES (%s, %s, %s, %s, %s)", (customer_name, customer_email, customer_phone_number, customer_subject, customer_message))
    conn.commit()    
    cursor.close()
    conn.close()

    resp = Response('Successful', status=200)
    resp.headers['set-cookie'] = 'cammyCookie=' + customer_email
    return resp


@app.route('/login', methods=['GET'])
def login():    
    data = json.loads(request.data.decode('ascii'))
    customer_email = data['email']
    customer_password = data['password']

    if len(customer_email) == 0:
        resp = Response('Please enter your email.', status=400)
        return resp

    if len(customer_password) == 0:
        resp = Response('Please enter your password', status=400)
        return resp

    conn = psycopg2.connect(
        database='cammy',
        user='postgres',
        host='127.0.0.1',
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (customer_email, customer_password))
    records = cursor.fetchall()    
    cursor.close()
    conn.close()

    if len(records) == 0:
        resp = Response('Invalid email or password', status=400)
        resp.headers['set-cookie'] = 'cammyCookie=' + ''
        return resp

    resp = Response(jsonify({'email': customer_email}), status=200)
    resp.headers['set-cookie'] = 'cammyCookie=' + customer_email
    return resp


@app.route('/register', methods=['POST'])
def register():
    data = json.loads(request.data.decode('ascii'))
    customer_email = data['email']
    customer_password = data['password']

    if len(customer_email) == 0:
        resp = Response('Please enter your email.', status=400)
        return resp

    if len(customer_password) == 0:
        resp = Response('Please enter your password', status=400)
        return resp

    conn = psycopg2.connect(
        database='cammy',
        user='postgres',
        host='127.0.0.1',
    )

    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (customer_email, customer_password))
    conn.commit()
    cursor.close()
    conn.close()

    resp = make_response(jsonify({'email': customer_email}))
    resp.status = '200'
    resp.headers['set-cookie'] = 'cammyCookie=' + customer_email
    return resp


@app.route('/user/get', methods=['GET'])
def getUser():
    receivedCookie = request.cookies
    if 'cammyCookie' in request.cookies:
        cammyCookie = request.cookies['cammyCookie']
        if len(cammyCookie) > 0:
            conn = psycopg2.connect(
                database='cammy',
                user='postgres',
                host='127.0.0.1',
            )

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (cammyCookie,))
            records = cursor.fetchall()
            cursor.close()
            conn.close()

            if len(records) == 0:
                resp = Response('No user found', status=404)
                return resp
            resp = make_response(jsonify({'email': cammyCookie}))
            resp.status = '200'
            resp.headers['set-cookie'] = 'cammyCookie=' + cammyCookie
            return resp

    resp = Response('Please login', status=404)
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
