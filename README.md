## Install

* Install docker. See [here](https://docs.docker.com/get-docker/).
* build docker image. Just do this once at the beginning.
```
docker build -t david_ocr .
```
* run docker image.
```
docker run -p 8080:8080 david_ocr
```

## Access the API

* Single url

Open browser and try `http://<SERVER_IP>:<PORT>/run_ocr_single?url=<URL_TO_IMAGE>`.

Example: `http://127.0.0.1:5000/run_ocr_single?url=https://images.chestertons.co.uk/assets/r/market/epcs/101/747/Lr101747060.jpg`

* Multiple urls

Prepare `request.json` in this [schema](./request_sample.json) with your URLs.

Run `curl -i -H 'Content-type: text/plain' -X POST -d @request.json 'http://<SERVER_IP>:<PORT>/run_ocr_batch'`

Example: `curl -i -H 'Content-type: text/plain' -X POST -d @request_sample.json 'http://localhost:5000/run_ocr_batch'`
