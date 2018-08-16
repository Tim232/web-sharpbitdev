from sanic import response, Sanic

from functools import wraps

import aiohttp
import asyncio
import base64
import unidecode

import json
import os

app = Sanic(__name__)

with open('data/status_codes.json') as f:
    app.status_codes = json.load(f)


def authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            if request.token == 'hunter2':
                return await f(request, *args, **kwargs)
            return response.json({'error': True, 'message': 'Unauthorized'}, status=401)
        return decorated_function
    return decorator


async def git_commit(session):
    url = 'https://api.github.com/repos/SharpBit/HQ-Bot/contents/data/hq_questions.json'
    base64content = base64.b64encode(open('data/hq_questions.json', "rb").read())
    async with session.get(url + '?ref=master', headers={'Authorization': 'token ' + os.environ.get('github-token')}).json() as data:
        sha = data['sha']
    if base64content.decode('utf-8') + '\n' != data['content']:
        message = json.dumps({
            'message': 'update',
            'branch': 'master',
            'content': base64content.decode('utf-8'),
            'sha': sha
        })

        async with session.put(url, data=message, headers={'Content-Type': 'application/json', 'Authorization': 'token ' + os.environ.get('github-token')}) as resp:
            print(resp)
    else:
        print('Nothing to update.')


@app.listener('before_server_start')
async def create_session(app, loop):
    app.session = aiohttp.ClientSession(loop=loop)


@app.listener('after_server_stop')
async def close_session(app, loop):
    await app.session.close()


@app.route('/')
# @authorized()
async def index(request):
    return response.json({'hello': 'world'})


@app.route('/status/<status>')
async def status_code(request, status):
    try:
        info = app.status_codes[status]
    except KeyError:
        return response.json({'error': True, 'status': status, 'message': 'invalid status'})
    else:
        return response.json({'error': False, 'status': status, 'info': info})


@app.route('/hq')
async def hq_home(request):
    return response.json({
        'endpoints': {
            'GET': ['questions'],
            'POST': ['answer', 'question']
        }
    })


@app.route('/hq/questions')
# @authorized()
async def load_questions(request):
    with open('data/hq_questions.json') as f:
        questions = json.load(f)
    return response.json(questions)


@app.route('/hq/question', methods=['POST'])
# @authorized()
async def submit_question(request):
    data = request.json
    question = data.get('question')
    question_num = data.get('questionNumber')
    answers = data.get('answers')

    # gotta handle bad requests amirite
    if not question or not question_num or not answers:
        return response.json({'error': True, 'message': 'Enter a question, question number, and answers'}, 400)

    with open('data/hq_questions.json', 'r+') as f:
        questions = json.load(f)
        questions.append(data)
        f.seek(0)
        json.dump(questions, f, indent=4)
    await git_commit(app.session)
    return response.json({'error': False, 'message': 'Question successfully submitted'})


@app.route('/hq/answer', methods=['POST'])
# @authorized()
async def submit_answer(request):
    question = request.json.get('question')
    answer = request.json.get('answer')
    if not question or not answer:
        return response.json({'error': True, 'message': 'Enter a question and answer'}, 400)

    with open('data/hq_questions.json', 'r+') as f:
        questions = json.load(f)
        for q in questions:
            if question.lower() == q['question'].lower():
                q['answer'] = answer
        f.seek(0)
        json.dump(questions, f, indent=4)
    await git_commit(app.session)
    return response.json({'error': False, 'message': 'Answer successfully submitted'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT') or 5000)
