import re

import requests
from bs4 import BeautifulSoup


class ImdbCrawler(object):
    def __init__(self, index_url):
        self.index_url = index_url
        self.imdb_url = "http://www.imdb.com"

    def get_actors(self, movie_soup):
        actors = movie_soup.findAll("div", {"class": "credit_summary_item"})[2].getText()
        movie_actors = actors.split("|")[0].replace(",", "").split("\n\n")[1:]
        movie_actors = [movie_actor.replace("\n", "").strip() for movie_actor in movie_actors]
        return movie_actors

    def get_director(self, movie_soup):
        director = movie_soup.findAll("div", {"class": "credit_summary_item"})[0].getText()
        movie_director = director.split("\n")[3].strip()
        return movie_director

    def get_writers(self, movie_soup):
        writers = movie_soup.findAll("div", {"class": "credit_summary_item"})[1].getText()
        movie_writers = writers.split("|")[0].replace(",", "").split("\n\n")[1:]
        movie_writers = [movie_writer.split("(")[0].strip() for movie_writer in movie_writers]
        return movie_writers

    def get_genres(self, movie_soup):
        genres = movie_soup.findAll("div", {"class": "see-more inline canwrap"})[1].getText()
        movie_genres = genres.replace("\xa0|", "").strip().split('\n')[1:]
        movie_genres = [movie_genre.strip() for movie_genre in movie_genres]
        return movie_genres

    def get_rating(self, movie_soup):
        rating = movie_soup.find("div", {"class": "ratingValue"}).getText()
        movie_rating = rating.rstrip().split("/")[0].strip()
        return movie_rating

    def get_keywords(self, movie_soup):
        keywords = movie_soup.findAll("div", {"class": "see-more inline canwrap"})[0].getText()
        movie_keywords = keywords.replace("Plot Keywords:", "").strip().split('\n|')[:-1]
        movie_keywords = [movie_keyword.strip() for movie_keyword in movie_keywords]
        return movie_keywords

    def get_user_review_count(self, movie_soup):
        count = movie_soup.find("div", {"class": "hiddenImportant"}).getText().strip()
        user_count = count.split('\n')[0].split(" ")[0].replace(',', "")
        return user_count

    def get_critic_review_count(self, movie_soup):
        count = movie_soup.find("div", {"class": "hiddenImportant"}).getText().strip()
        critic_count = count.split('\n')[1].split(" ")[0].replace(',', "")
        return critic_count

    def get_soup(self, url):
        req = requests.get(url)
        page = req.text
        soup = BeautifulSoup(page, 'html.parser')
        return soup

    def run(self, top_n=250):
        result_array = list()
        index_soup = self.get_soup(self.index_url)
        for i in range(top_n):
            result = dict()
            content = str(index_soup.findAll('td', {'class': 'titleColumn'})[i])
            movie_name = str(re.findall('>(.*?)</a>', content)[0])
            movie_year = index_soup.findAll('span', {'class': 'secondaryInfo'})[i].getText()[1:-1]

            href = str(re.findall('<a href="(.*?)\?', content)[0])
            movie_url = self.imdb_url + href

            movie_soup = self.get_soup(url=movie_url)

            result['movie_name'] = movie_name
            result['movie_year'] = movie_year
            result['actors'] = self.get_actors(movie_soup)
            result['director'] = self.get_director(movie_soup)
            result['writers'] = self.get_writers(movie_soup)
            result['genres'] = self.get_genres(movie_soup)
            result['rating'] = self.get_rating(movie_soup)
            result['keywords'] = self.get_keywords(movie_soup)
            result['user_count'] = self.get_user_review_count(movie_soup)
            result['critic_count'] = self.get_critic_review_count(movie_soup)

            result_array.append(result)

        return result_array
