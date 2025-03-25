import json
import torch
from flask import Flask, request
from paddleocr import PaddleOCR
from engine import ocr_on_single


ocr_engine = PaddleOCR(lang='en', use_gpu=torch.cuda.is_available())

def run(urls):
    results = {}
    for url in urls:
        results[url] = ocr_on_single(ocr_engine, url)
    return results

app = Flask(__name__)

@app.route('/run_ocr_single')
def run_ocr_single():
    url = request.args.get('url')
    return {str(url): ocr_on_single(ocr_engine, url)}


@app.route('/run_ocr_batch', methods=['POST'])
def run_ocr_batch():
    urls = json.loads(request.data)["urls"]
    return run(urls)

if __name__ == '__main__':
    app.run(debug=True)
