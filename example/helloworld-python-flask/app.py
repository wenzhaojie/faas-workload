import os
import json
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    target = os.environ.get('TARGET', 'World')
    return 'Hello WZJ {}!\n'.format(target)

@app.route('/function', methods=['POST']) 
def foo():
    data = request.get_data()
    _str = data.decode('utf-8')
    print(f"str:{_str}")
    obj = json.loads(_str)
    return f"/function receive obj:{obj}, type:{type(obj)}"


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
