from flask import Flask, request
from datetime import datetime
import random
import json
import csv
import os

app = Flask(__name__)
questions = json.load(open('questions.json'))


@app.route('/question')
def send_question():
    app_name = request.args.get('app_name', 'this app')
    language = request.args.get('language', 'english')
    return random.choice(questions)[language].replace('<app_name>', app_name)


answers_file = open('answers.csv', 'a', newline='', buffering=1)
answers_csv_writer = csv.DictWriter(
        answers_file, (
            'user_id',
            'date',
            'app_name',
            'question',
            'answer_text',
            'answer_audio_uuid',
            ))
if os.stat('answers.csv').st_size == 0:
    answers_csv_writer.writeheader()


@app.route('/answer', methods=('POST',))
def receive_answer():
    data = request.get_json(force=True)
    answers_csv_writer.writerow({
        'date': datetime.utcnow().isoformat(),
        'user_id': data.get('user_id', 'NULL'),
        'app_name': data.get('app_name', 'NULL'),
        'question': data.get('question', 'NULL'),
        'answer_text': data.get('answer_text', 'NULL'),
        'answer_audio_uuid': data.get('answer_audio_uuid', 'NULL'),
    })
    return 'Thanks for your answer!'


@app.route('/audio', methods=('POST',))
def receive_audio():
    if request.content_length > 5 * 10**6:
        return 'File is too big: ' + request.content_length + ' byte.'

    if 'uuid' not in request.args.keys():
        return 'uuid is required'

    with open('audio/' + request.args['uuid'] + '.aac', 'wb') as f:
        f.write(request.get_data())

    return 'Thanks for your audio answer!'
