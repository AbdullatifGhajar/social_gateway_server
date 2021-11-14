import csv
from datetime import datetime
import json
import os
from functools import wraps
from random import randrange
from dotenv import load_dotenv

from flask import Flask, request

app = Flask(__name__)

load_dotenv()

SUPPORTED_LANGUAGES = ('english',)
DEFAULT_LANGUAGE = 'english'
DEFAULT_QUESTION_TYPE = 'normal'
LINE_BUFFERING = 1
KEY = os.environ.get('KEY')


def main(testing=False, injected_questions=None, injected_write_answer=None,
         injected_write_audio=None):
    global questions, write_answer, write_audio

    # dependency injection for testing
    if testing:
        questions = injected_questions
        write_answer = injected_write_answer
        write_audio = injected_write_audio
        return

    with open('questions.json') as f:
        questions = json.load(f)

        for question in questions:
            for key in SUPPORTED_LANGUAGES:
                assert key in question

    # not using "with", keep the file open as long as the server is running
    # newline='' is recommended for csv, buffering=1 means line buffering
    answers_file = open('answers.csv', 'a', newline='',
                        buffering=LINE_BUFFERING)
    answers_csv_writer = csv.DictWriter(
        answers_file, (
            'user_id',
            'date',
            'app_name',
            'question',
            'answer_text',
            'answer_audio_uuid',
        ))

    # only write header if file is empty
    if os.stat(answers_file.name).st_size == 0:
        answers_csv_writer.writeheader()

    def write_answer(row):
        answers_csv_writer.writerow(row)

    def write_audio(file_name, data):
        with open(file_name, 'wb') as f:
            f.write(data)


def key_required(func):
    @wraps(func)
    def check_key(*args, **kwargs):
        if(request.args.get('key', '') == KEY):
            return func(*args, **kwargs)
        else:
            return 'invalid key', 401

    return check_key


@app.route('/browser/question')
@key_required
def send_question():
    app_name = request.args.get('app_name', 'this app')
    question_type = request.args.get('question_type', DEFAULT_QUESTION_TYPE)

    def is_suitable(question):
        suitable = True
        suitable &= question.get('question_type', 'normal') == question_type

        if 'whitelist' in question:
            suitable &= app_name in question['whitelist']

        if 'blacklist' in question:
            suitable &= app_name not in question['blacklist']

        return suitable

    suitable_questions = [
        question for question in questions if is_suitable(question)]

    language = request.args.get('language', DEFAULT_LANGUAGE)
    question_id = request.args.get('question_id',
                                   randrange(len(suitable_questions)))

    question_template = suitable_questions[int(question_id)][language]
    return question_template.replace('<app_name>', app_name)


@app.route('/browser/answer', methods=('POST',))
@key_required
def receive_answer():
    data = request.get_json(force=True)
    write_answer({
        'date': datetime.utcnow().isoformat(),
        'user_id': data.get('user_id', 'NULL'),
        'app_name': data.get('app_name', 'NULL'),
        'question': data.get('question', 'NULL'),
        'answer_text': data.get('answer_text', 'NULL'),
        'answer_audio_uuid': data.get('answer_audio_uuid', 'NULL'),
    })
    # if answer_audio_uuid is set the data should be sent to /audio
    return 'Thanks for your answer!'


@app.route('/browser/audio', methods=('POST',))
@key_required
def receive_audio():
    # TODO: rename assertions
    if 'uuid' not in request.args.keys():
        return 'UUID is required.', 400

    if not request.content_length:
        return 'Audio data is required.', 400

    if request.content_length > 5 * 10**6:
        return 'File is too big: ' + request.content_length + ' byte.', 400

    write_audio('audio/' + request.args["uuid"] + '.aac', request.get_data())

    return 'Thanks for your audio answer!'


main()

if __name__ == '__main__':
    app.run(
        # ssl_context='adhoc',
        host='0.0.0.0')
