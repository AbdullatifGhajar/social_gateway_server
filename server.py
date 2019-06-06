from flask import Flask, request
import random
from datetime import datetime
import csv

app = Flask(__name__)

questions = [
    'What do you expect of using <app_name> right now?',
    'question 2',
    'question 3']

@app.route('/question')
def send_question():
    app_name = request.args.get('app_name', 'this app')
    return random.choice(questions).replace('<app_name>', app_name)

answers_file = open('answers.csv', 'a', newline='', buffering=1)
answers_csv_writer = csv.DictWriter(answers_file,
    ('user_id', 'date', 'app_name', 'question', 'answer'))
answers_csv_writer.writeheader()

@app.route('/answer', methods=('POST',))
def receive_answer():
    data = request.get_json(force=True)
    answers_csv_writer.writerow({
        'user_id': data.get('user_id', 'NULL'),
        'date': datetime.utcnow().isoformat(),
        'app_name': data.get('app_name', 'NULL'),
        'question': data.get('question', 'NULL'),
        'answer': data.get('answer', 'NULL'),
    })
    return 'Thanks for your answer!'
