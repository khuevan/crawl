from flask import Flask, request, render_template

from setting import HOST, PORT, DEBUG
from utils import get_data, data_collection, openbrowser
from bson.json_util import dumps

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
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


if __name__ == '__main__':
    driver = openChrome()
    app.run(HOST, PORT, DEBUG)
