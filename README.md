# IMDB Recommendation System for Top 250 Movies

This piece of work is to showcase content based (item-item) recommendation of movies. To do this first top 250 imdb movies are crawled and stored as json leveraging BeautifulSoup package. Then a cosine similarity based recommendation system is built using functionalities of pandas, numpy and scikit-learn.

# You have to follow the following step irrespective of where the code is run &rarr; COMMON_STEP

1. create aws access key and secret key
2. Create an S3 bucket.
3. Set the envoronment variables in ```docker-compose-recsys.yml``` and ```docker-compose-aws.yml```, from ```None``` value to appropriate values.

# How to run this locally?

1. ```git clone https://github.com/tuhinsharma/imdb_rec_sys.git ```
2. ```cd imdb_rec_sys ```
3. Follow ```COMMON_STEP```
4. Use ```docker-compose```
    1. ```docker-compose -f docker-compose-recsys.yml build```
    2. ```docker-compose -f docker-compose-recsys.yml up ```
5. For Crawling : ```curl -H 'Content-Type: application/json' -X POST -d {} http://localhost:6006/api/v1/schemas/crawl_imdb```
6. For Training : ```curl -H 'Content-Type: application/json' -X POST -d {} http://localhost:6006/api/v1/schemas/train```
7. For Recommendation : ```curl -H 'Content-Type: application/json' -X POST -d '{"movie_list": ["The Green Mile","Witness for the Prosecution"]}' http://localhost:6006/api/v1/schemas/score```


# How to deploy on an EC2 (AWS) instance using Flask and Nginx?

1. Choose EC2 instance Ubuntu 16.04 LTS - Xenial (HVM)
2. Configure security group - SSH - custom, HTTP - anywhere
3. Launch instance using key-value pair - tuhin-aws
4. ssh into EC2 machine - ```ssh -i "tuhin-aws.pem"``` ***```ubuntu```***```@```**```ec2-54-234-224-219.compute-1.amazonaws.com```**
5. ```sudo apt update --fix-missing```
6. ```sudo apt install -y python3-pip```
7. ```sudo apt install -y nginx```
8. open ```nginx.conf``` file &rarr; ```sudo vi /etc/nginx/nginx.conf``` &rarr; change ```user  ```***```ubuntu```***```;``` and add ```server_names_hash_bucket_size 128;``` in the http block
9. open ```virtual.conf``` file &rarr; ```sudo vi /etc/nginx/conf.d/virtual.conf``` &rarr; add 
```
server {
    listen       80;
    server_name  ec2-54-234-224-219.compute-1.amazonaws.com;
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```
10. ```sudo systemctl start nginx```
11. ```git clone https://github.com/tuhinsharma/imdb_rec_sys.git```
12. ```cd imdb_rec_sys```
13. Follow ```COMMON_STEP```
13. ```sudo pip3 install -r requirements.txt``` 
14. ```cp ./rec_platform/deployment/app.py ./app.py```
14. ```sudo systemctl restart nginx```
15. ```gunicorn --pythonpath / -b localhost:8000 -k gevent -t 900 app:app -w 5 &```
* In local system:-
```curl -H 'Content-Type: application/json' -X POST -d '{"movie_list": ["The Green Mile","Witness for the Prosecution"]}' http://ec2-54-234-224-219.compute-1.amazonaws.com/api/v1/schemas/score```
The output should be:-
```
{
  "movies": [
    "L.A. Confidential", 
    "Salinui chueok", 
    "Les diaboliques", 
    "12 Angry Men", 
    "Double Indemnity", 
    "Chinatown", 
    "On the Waterfront", 
    "A Wednesday", 
    "Se7en", 
    "The Usual Suspects"
  ]
}
```
* In remote system do ```pkill gunicorn``` and ```sudo systemctl stop nginx```if service no longer needed.

# How to deploy on an EC2 (AWS) cluster using docker-compose?





