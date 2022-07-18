from flask import Flask, request, render_template, Response
from keywords import keywords
from settings import HOST, PORT, DEBUG
from utils import get_data, data_collection, openbrowser, check_keyword, crawl_data
from bson.json_util import dumps

app = Flask(__name__)


@app.route('/')
def welcome():
    return render_template('index.html')


@app.route('/result', methods=['GET', 'POST'])
def response():
    if request.method == 'POST':
        url = request.form['name']
        data = get_data(url, driver)
        return render_template('result.html', url=url, data=dumps(data))
    else:
        data = data_collection.find()
        return dumps(data)


@app.route('/check', methods=['GET', 'POST'])
def check():
    if request.method == 'POST':
        req = request.json
        type = req['type']
        if type == 'url':
            try:
                texts = get_data(driver, req['data'])
                text = [txt['text'] for txt in texts['texts']]
                data = {
                    "status": "success",
                    "vipham": check_keyword(text, keywords)
                }
            except:
                data = {
                    "status": "fail",
                    "msg": "Error"
                }
            return Response(dumps(data), mimetype='json')
        else:
            return Response(dumps({"vipham": check_keyword([req['data']], keywords)}), mimetype='json')


if __name__ == '__main__':
    driver = openbrowser()
    app.run(HOST, PORT, DEBUG)
