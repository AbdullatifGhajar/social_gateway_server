from flask import Flask, request
import random
from datetime import datetime
import csv

app = Flask(__name__)

questions = [
    'What do you expect of using <app_name> right now?',
    'question 2',
    'question 3']

app_names = [
    'this app',
    'Instagram',
    'Snapchat',
    'WhatsApp',
    'Facebook',
    'Facebook Messenger',
    'Signal',
    'Telegram'
]

@app.route('/question')
def send_question():
    app_id = int(request.args.get('app_id', '0'))
    return random.choices(questions)[0].replace('<app_name>', app_names[app_id])

answers_csv_writer = csv.DictWriter(
    open('answers.csv', 'a', newline='', buffering=1),
    ('user_id', 'date', 'app_id', 'question_id', 'answer'))
answers_csv_writer.writeheader()

@app.route('/answer', methods=('POST',))
def receive_answer():
    answers_csv_writer.writerow({
        'user_id': request.args.get('user_id', 'NULL'),
        'date': datetime.utcnow().isoformat(),
        'app_id': request.args.get('app_id', 'NULL'),
        'question_id': request.args.get('question_id', 'NULL'),
        'answer': request.args.get('answer', 'NULL'),
    })
    return 'Thanks for your answer!'
