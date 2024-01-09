from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
import requests
from loguru import logger

app = Flask(__name__, static_url_path='')

YOLO_URL = os.environ['YOLO5_URL']
if not YOLO_URL.startswith('http://'):
    logger.error('YOLO5_URL env var must starts with `http://`')
    exit(1)
app.config['UPLOAD_FOLDER'] = 'static/data'


@app.route('/', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    p = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    logger.info(f'request detect service with {p}')

    res = requests.post(f'{YOLO_URL}/predict', files={
        'file': (p, open(p, 'rb'), 'image/png')
    })

    if res.status_code == 200:
        logger.info(f'response from yolo service with {res.status_code}')

        output_image_path = "output_image.jpg"  # Replace with your desired output file name
        with open(app.config['UPLOAD_FOLDER'] + '/' + output_image_path, "wb") as output_file:
            output_file.write(res.content)

        return render_template('result.html', filename=f'data/{output_image_path}')

    else:
        logger.error(res.text)
        return render_template('result.html', filename=f'data/{filename}')


@app.route("/", methods=['GET'])
def home():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8082, debug=True)
