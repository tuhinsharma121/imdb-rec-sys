import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from rec_platform.src.rec_constants import *
from util.data_store.local_filesystem import LocalFileSystem
from util.data_store.s3_data_store import S3DataStore


def transpose_set(x, col_name):
    values = x[col_name]
    for value in values:
        x[value] = 1
    return x


def transpose_value(x, col_name):
    value = str(x[col_name])
    x[value] = 1
    return x


class ImdbRecSys(object):
    def __init__(self, matrix, movie_names):
        self.matrix = matrix
        self.movie_names = movie_names

    def save(self, data_store):
        if type(data_store) is LocalFileSystem:
            data_store.write_pickle_file(data=self.matrix, filename=SIMILARITY_MATRIX_FILENAME)
            data_store.write_pickle_file(data=self.movie_names, filename=MOVIE_LIST_FILENAME)
        if type(data_store) is S3DataStore:
            temp_data_store = LocalFileSystem("/tmp/")
            temp_data_store.write_pickle_file(data=self.matrix, filename=SIMILARITY_MATRIX_FILENAME)
            temp_data_store.write_pickle_file(data=self.movie_names, filename=MOVIE_LIST_FILENAME)
            data_store.upload_file("/tmp/" + SIMILARITY_MATRIX_FILENAME, SIMILARITY_MATRIX_FILENAME)
            data_store.upload_file("/tmp/" + MOVIE_LIST_FILENAME, MOVIE_LIST_FILENAME)
        return None

    @classmethod
    def load(cls, data_store):
        if type(data_store) is LocalFileSystem:
            matrix = data_store.read_pickle_file(filename=SIMILARITY_MATRIX_FILENAME)
            movie_names = data_store.read_pickle_file(filename=MOVIE_LIST_FILENAME)
        if type(data_store) is S3DataStore:
            data_store.download_file(SIMILARITY_MATRIX_FILENAME, "/tmp/" + SIMILARITY_MATRIX_FILENAME)
            data_store.download_file(MOVIE_LIST_FILENAME, "/tmp/" + MOVIE_LIST_FILENAME)
            temp_data_store = LocalFileSystem("/tmp/")
            matrix = temp_data_store.read_pickle_file(filename=SIMILARITY_MATRIX_FILENAME)
            movie_names = temp_data_store.read_pickle_file(filename=MOVIE_LIST_FILENAME)
        return ImdbRecSys(matrix=matrix, movie_names=movie_names)

    @classmethod
    def train(cls, data_store):
        # The crawled data of top 250 movies are loaded in pandas dataframe for further processing
        dataframe = data_store.read_json_file_into_pandas_df(filename=MOVIE_DATA_FILENAME)

        # movie names are seperately cached for O(1) access of the data during prediction
        movie_names = np.array(dataframe['movie_name'])

        # Create OnehotEncoder representation for columns ['actors','writers',
        # 'genres','director','movie_year','keywords']

        res = dataframe.apply(transpose_set, 1, args=(['actors'])). \
            apply(transpose_set, 1, args=(['writers'])). \
            apply(transpose_set, 1, args=(['keywords'])). \
            apply(transpose_value, 1, args=(['director'])). \
            apply(transpose_value, 1, args=(['movie_year'])). \
            apply(transpose_set, 1, args=(['genres']))

        # Remove the categorical columns from the dataframe as the information is encoded as Onehotencoder
        res.drop(labels=['actors', 'writers', 'genres', 'director', 'movie_year', 'movie_name', 'keywords'], axis=1,
                 inplace=True)

        # Scale the values of continuous columns
        res[['critic_count', 'rating', 'user_count']] /= res[['critic_count', 'rating', 'user_count']].max()

        # For onehotcode representation fill the nan values by 0.0
        res.fillna(value=0.0, inplace=True)

        # Use Scikit-Learn cosine similarity to calculate the distance
        similarity_matrix = cosine_similarity(res)

        # Initialize the ImdbRecSys object with the values of the similarity matrix and the movie names as nparray
        return ImdbRecSys(matrix=similarity_matrix, movie_names=movie_names)

    def predict(self, query, top_n=10):
        # get the movie index from the query
        movie_ix = np.where(np.in1d(self.movie_names, query))[0]

        # get the relevant rows from the similarity matrix
        matrix_rows = self.matrix[movie_ix, :]
        if matrix_rows.shape[0] == 0:
            return np.array(['one or more than one movies are not found'])

        # in case there are more than one movies calculate the mean of
        # the similarity scores for each of the candidate movies
        rows_mean = matrix_rows.mean(axis=0)

        # sort the movie indices based on the increasing order of the similarity score
        top_movie_ix = np.argsort(rows_mean)

        # remove the movie indices of the query and select top 10 movies
        ix = np.where(np.in1d(top_movie_ix, movie_ix))[0]
        top_movie_ix = np.delete(top_movie_ix, ix)

        # taking top_n movie indices based on similarity score
        top_n_movie_ix = np.flip(top_movie_ix, axis=0)[:top_n]

        return self.movie_names[top_n_movie_ix]
