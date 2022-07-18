from flask import Flask, request, render_template, Response
from keywords import keywords
from settings import HOST, PORT, DEBUG
from utils import get_data, data_collection, check_keyword, openbrowser

from bson.json_util import dumps

app = Flask(__name__)


@app.route('/')
def welcome():
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def response():
    url = request.form['name']
    data = get_data(driver=driver, url=url)
    return render_template('result.html', url=url, data=dumps(data))


@app.route('/check_url', methods=['POST'])
def check_url():
    try:
        req = request.json
        url = req['url']
        texts = get_data(driver, url)
        text = [txt['text'] for txt in texts['texts']]
        data = {
            "successfully": True,
            "vipham": check_keyword(text, keywords)
        }
    except Exception as e:
        data = {
            "successfully": False,
            "msg": str(e)
        }

    return Response(dumps(data), mimetype='json')


@app.route('/check_text', methods=['POST'])
def check_text():
    try:
        req = request.json
        text = req['text']
        data = {
            "successfully": True,
            "vipham": check_keyword([text], keywords)
        }
    except Exception as e:
        data = {
            "successfully": True,
            "msg": str(e)
        }

    return Response(dumps(data), mimetype='json')


if __name__ == '__main__':
    driver = openbrowser()
    app.run(HOST, PORT, DEBUG)
