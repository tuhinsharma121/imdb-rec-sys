import flask
import logging
from flask import Flask, request
import sys

from rec_platform.src.scoring import recommend,load_rec_model_s3
from rec_platform.src.training import train_and_save_rec_model_s3,crawl_s3

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
app = Flask(__name__)


global imdb_recsys
app.imdb_recsys = load_rec_model_s3()


@app.route('/')
def heart_beat():
    return flask.jsonify({"status": "ok"})


@app.route('/api/v1/schemas/crawl_imdb', methods=['POST'])
def crawl_imdb():
    app.logger.info("Submitting the crawling job")
    input_json = request.get_json()
    crawl_s3()
    response = {"message": "Crawling done!!!"}
    return flask.jsonify(response)


@app.route('/api/v1/schemas/train', methods=['POST'])
def train():
    app.logger.info("Submitting the training job")
    input_json = request.get_json()
    train_and_save_rec_model_s3()
    response = {"message": "Training done!!!"}
    return flask.jsonify(response)


@app.route('/api/v1/schemas/score', methods=['POST'])
def score():
    input_json = request.get_json()
    query = input_json.get("movie_list")
    result = recommend(app.imdb_recsys, query)
    recommendation = dict()
    recommendation['movies'] = list(result)
    return flask.jsonify(recommendation)


if __name__ == "__main__":
    app.run()
