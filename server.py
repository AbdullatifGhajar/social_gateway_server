from flask import Flask, request
from datetime import datetime
import random
import json
import csv

app = Flask(__name__)
questions = json.load(open('questions.json'))


@app.route('/question')
def send_question():
    app_name = request.args.get('app_name', 'this app')
    language = request.args.get('language', 'english')
    return random.choice(questions)[language].replace('<app_name>', app_name)


answers_file = open('answers.csv', 'a', newline='', buffering=1)
answers_csv_writer = csv.DictWriter(
        answers_file, ('user_id', 'date', 'app_name', 'question', 'answer'))
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
