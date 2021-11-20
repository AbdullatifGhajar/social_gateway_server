from flask import Flask, request
import csv
from datetime import datetime
import json
import os
import random
import dotenv
from functools import wraps

dotenv.load_dotenv()  # take environment variables from .env.


app = Flask(__name__)

SUPPORTED_LANGUAGES = ('english',)
DEFAULT_LANGUAGE = 'english'
DEFAULT_PROMPT_TYPE = 'normal'
LINE_BUFFERING = 1
KEY = os.environ.get('KEY')


def main(testing=False, injected_prompts=None, injected_write_answer=None,
         injected_write_audio=None):
    global prompts, write_answer, write_audio

    # dependency injection for testing
    if testing:
        prompts = injected_prompts
        write_answer = injected_write_answer
        write_audio = injected_write_audio
        return

    with open('prompts.json') as input_file:
        prompts = json.load(input_file)

        for prompt in prompts:
            for key in SUPPORTED_LANGUAGES:
                assert key in prompt

    # not using "with", keep the file open as long as the server is running
    # newline='' is recommended for csv, buffering=1 means line buffering
    answers_file = open('answers.csv', 'a', newline='',
                        buffering=LINE_BUFFERING)
    answers_csv_writer = csv.DictWriter(
        answers_file, (
            'user_id',
            'date',
            'app_name',
            'prompt',
            'answer_text',
            'answer_audio_uuid',
        ))

    # only write header if file is empty
    if os.stat(answers_file.name).st_size == 0:
        answers_csv_writer.writeheader()

    def write_answer(row):
        answers_csv_writer.writerow(row)

    def write_audio(file_name, data):
        with open(file_name, 'wb') as output_file:
            output_file.write(data)


def key_required(func):
    @wraps(func)
    def check_key(*args, **kwargs):
        if(request.args.get('key', '') == KEY):
            return func(*args, **kwargs)
        else:
            return 'invalid key', 401

    return check_key


@app.route('/browser/prompt')
@key_required
def send_prompt():
    app_name = request.args.get('app_name', 'this app')
    prompt_type = request.args.get('prompt_type', DEFAULT_PROMPT_TYPE)

    def is_suitable(prompt):
        suitable = True
        suitable &= prompt.get('prompt_type', 'normal') == prompt_type

        if 'whitelist' in prompt:
            suitable &= app_name in prompt['whitelist']

        if 'blacklist' in prompt:
            suitable &= app_name not in prompt['blacklist']

        return suitable

    suitable_prompts = [
        prompt for prompt in prompts if is_suitable(prompt)]

    language = request.args.get('language', DEFAULT_LANGUAGE)
    chosen_prompt = random.choice(suitable_prompts)

    return {
        'content': chosen_prompt[language].replace('<app_name>', app_name),
        'answerable': chosen_prompt['answerable']
    }


@app.route('/browser/answer', methods=('POST',))
@key_required
def receive_answer():
    data = request.get_json(force=True)
    write_answer({
        'date': datetime.utcnow().isoformat(),
        'user_id': data.get('user_id', 'NULL'),
        'app_name': data.get('app_name', 'NULL'),
        'prompt': data.get('prompt', 'NULL'),
        'answer_text': data.get('answer_text', 'NULL'),
        'answer_audio_uuid': data.get('answer_audio_uuid', 'NULL'),
    })
    # if answer_audio_uuid is set the data should be sent to /audio
    return {
        'message': 'Thanks for your answer!'
    }


@app.route('/browser/audio', methods=('POST',))
@key_required
def receive_audio():
    # TODO: rename assertions
    if 'uuid' not in request.args.keys():
        return {
            'message': 'UUID is required.'
        }, 400

    if not request.content_length:
        return {
            'message': 'Audio data is required.'
        }, 400

    if request.content_length > 5 * 10**6:
        return {
            'message': f'File is too big: {request.content_length} byte.'
        }, 400

    write_audio('audio/' + request.args["uuid"] + '.aac', request.get_data())

    return {
        'message': 'Thanks for your audio answer!'
    }


main()

if __name__ == '__main__':
    app.run(
        # ssl_context='adhoc',
        host='0.0.0.0')
