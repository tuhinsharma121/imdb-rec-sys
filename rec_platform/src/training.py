from time import time

from rec_platform.src.config import *
from rec_platform.src.crawler import *
from rec_platform.src.rec_constants import *
from rec_platform.src.recommender import ImdbRecSys
from util.data_store.local_filesystem import LocalFileSystem
from util.data_store.s3_data_store import S3DataStore


def train_and_save_rec_model(data_store):
    rec_sys = ImdbRecSys.train(data_store)
    rec_sys.save(data_store=data_store)


def train_and_save_rec_model_local():
    data_store = LocalFileSystem(src_dir="./rec_platform/data/")
    train_and_save_rec_model(data_store=data_store)


def train_and_save_rec_model_s3():
    data_store = S3DataStore(src_bucket_name=AWS_BUCKET_NAME, access_key=AWS_S3_ACCESS_KEY_ID,
                             secret_key=AWS_S3_SECRET_ACCESS_KEY)
    train_and_save_rec_model(data_store=data_store)


def crawl(data_store):
    index_url = "http://www.imdb.com/chart/top?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=2417962742&pf_rd_r=0M85G1V8JHW928EHBETF&pf_rd_s=right-4&pf_rd_t=15506&pf_rd_i=moviemeter&ref_=chtmvm_ql_3"
    im = ImdbCrawler(index_url=index_url)
    json_data = im.run(top_n=MOVIE_COUNT)
    data_store.write_json_file(filename=MOVIE_DATA_FILENAME, contents=json_data)


def crawl_local():
    data_store = LocalFileSystem(src_dir="./rec_platform/data/")
    crawl(data_store=data_store)


def crawl_s3():
    data_store = S3DataStore(src_bucket_name=AWS_BUCKET_NAME, access_key=AWS_S3_ACCESS_KEY_ID,
                             secret_key=AWS_S3_SECRET_ACCESS_KEY)
    crawl(data_store=data_store)
    return None


if __name__ == '__main__':
    t0 = time()
    crawl_local()
    crawl_s3()
    train_and_save_rec_model_local()
    train_and_save_rec_model_s3()
    print('running time : ', time() - t0)
