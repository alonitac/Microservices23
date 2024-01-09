from pathlib import Path
from flask import Flask, request, send_file
from detect import run
import uuid
import yaml
from loguru import logger
import os
from werkzeug.utils import secure_filename


with open("data/coco128.yaml", "r") as stream:
    names = yaml.safe_load(stream)['names']

app = Flask(__name__, static_url_path='')
UPLOAD_FOLDER = 'data/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/predict', methods=['POST'])
def predict():
    prediction_id = str(uuid.uuid4())
    logger.info(f'prediction: {prediction_id}. start processing')

    if 'file' not in request.files:
        return 'No file attached', 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    logger.info(f'attached file: {request.files["file"]}')

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    p = Path(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    logger.info(f'predicting {prediction_id}/{p}')

    run(
        weights='yolov5s.pt',
        data='data/coco128.yaml',
        source=p,
        project='static/data',
        name=prediction_id,
        save_txt=True
    )

    logger.info(f'prediction done {prediction_id}/{p}')
    pred_result_img = Path(f'static/data/{prediction_id}/{filename}')

    return send_file(pred_result_img)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)
