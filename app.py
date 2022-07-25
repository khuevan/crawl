from time import perf_counter

from flask import Flask, request, render_template, Response
from keywords import keywords
from settings import HOST, PORT, DEBUG
from utils import get_data, check_keyword, openbrowser, openchrome
from flask_cors import CORS

from bson.json_util import dumps

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.secret_key = b'_5#y2Lasdasd"F4Q8z\n\xec]/'

@app.route('/')
def welcome():
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def response():
    url = request.form['name']
    data = get_data(driver=driver, url=url)
    return render_template('result.html', url=url, data=dumps(data))


@app.route('/api/check_url', methods=['POST'])
def check_url():
    try:
        url = request.values.get('Url')
        data = get_data(driver, url)
        text = [txt['text'] for txt in data['texts']]
        violation, brand = check_keyword(text, keywords)
        json = {
            "Successfully": True,
            "Is violation": violation,
            "Brand": list(brand),
            "Text": ' '.join(map(str, text)),
            "Images": data['images']
        }
    except Exception as e:
        json = {
            "Successfully": False,
            "Exception": str(e),
            "Images": []
        }
    return Response(dumps(json), mimetype='json')


@app.route('/api/check_text', methods=['POST'])
def check_text():
    try:
        text = request.values.get('Text')
        violation, brand = check_keyword([text], keywords)
        json = {
            "Successfully": True,
            "Is violation": violation,
            "Brand": brand
        }
    except Exception as e:
        json = {
            "Successfully": False,
            "Exception": str(e)
        }
    return Response(dumps(json), mimetype='json')


if __name__ == '__main__':
    driver = openbrowser()
    app.run(HOST, PORT, debug=DEBUG)
