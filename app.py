
from flask import Flask , render_template
from flask import Response
from flask import request
from lib import utils

from databases.face_demographics import face_demographics

import json
import databases as db

app = Flask(__name__)


@app.route("/data/test/group/demographics", methods=["GET"])
def demographics_group():
    fd = face_demographics()
    result = fd.get_summary_demographics_groups()
    print(result)

    js = json.dumps(
        {
        "success": "true",
        "data": result
        }
    )

    resp = Response(js, status=200, mimetype='application/json')
    return resp




@app.route("/")
def hello():
   # return "Hello World!"
    return render_template('index.html')


if __name__ == "__main__":
    app.run("127.0.0.1", port=3030, debug=True)