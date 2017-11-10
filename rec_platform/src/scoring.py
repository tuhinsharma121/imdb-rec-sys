from rec_platform.src.config import *
from rec_platform.src.recommender import ImdbRecSys
from util.data_store.local_filesystem import LocalFileSystem
from util.data_store.s3_data_store import S3DataStore


def recommend(rec_sys, query):
    result = rec_sys.predict(query=query)
    return result


def load_rec_model_local():
    data_store = LocalFileSystem(src_dir="./rec_platform/data")
    rec_sys = ImdbRecSys.load(data_store=data_store)
    return rec_sys


def load_rec_model_s3():
    data_store = S3DataStore(src_bucket_name=AWS_BUCKET_NAME, access_key=AWS_S3_ACCESS_KEY_ID,
                             secret_key=AWS_S3_SECRET_ACCESS_KEY)
    rec_sys = ImdbRecSys.load(data_store=data_store)
    return rec_sys


if __name__ == '__main__':
    rec_sys = load_rec_model_local()
    query = ['The Shawshank Redemption']
    result = recommend(rec_sys, query)
    print(result)
    query = ['The Godfather', 'The Dark Knight', 'Cool Hand Luke']
    result = recommend(rec_sys, query)
    print(result)
    rec_sys = load_rec_model_s3()
    query = ['The Shawshank Redemption']
    result = recommend(rec_sys, query)
    print(result)
    query = ['The Godfather', 'The Dark Knight', 'Cool Hand Luke']
    result = recommend(rec_sys, query)
    print(result)
