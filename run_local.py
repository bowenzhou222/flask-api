from flask import Flask, request, jsonify, make_response, Response
import psycopg2
import os
import json
import requests

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
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

    if len(customer_email) == 0:
        return Response('Please provide your email.', status=400)

    if len(customer_message) == 0:
        return Response('Please do not send empty message', status=400)

    mailgun_response = send_simple_message(data)
    print(mailgun_response.ok)
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
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
