# IMDB Recommendation System for Top 250 Movies

This piece of work is to showcase content based (item-item) recommendation of movies. To do this first top 250 imdb movies are crawled and stored as json leveraging BeautifulSoup package. Then a cosine similarity based recommendation system is built using functionalities of pandas, numpy and scikit-learn.

# You have to follow the following step irrespective of where the code is run &rarr; COMMON_STEP

1. create aws access key and secret key
2. Create an S3 bucket.
3. Set the envoronment variables in ```docker-compose-recsys.yml``` and ```docker-compose-aws.yml```, from ```None``` value to appropriate values.

# How to run this locally?

1. ```git clone https://github.com/tuhinsharma/imdb-rec-sys.git ```
2. ```cd imdb-rec-sys ```
3. Follow ```COMMON_STEP```
4. Use ```docker-compose```
    1. ```docker-compose -f docker-compose-recsys.yml build```
    2. ```docker-compose -f docker-compose-recsys.yml up ```
5. For Crawling : ```curl -H 'Content-Type: application/json' -X POST -d {} http://localhost:6006/api/v1/schemas/crawl_imdb```
6. For Training : ```curl -H 'Content-Type: application/json' -X POST -d {} http:imdb//localhost:6006/api/v1/schemas/train```
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
11. ```git clone https://github.com/tuhinsharma/imdb-rec-sys.git```
12. ```cd imdb-rec-sys```
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

# How to deploy on an EC2 (AWS) using docker-compose?

1. Choose EC2 instance ```ubuntu 16.04 LTS - Xenial (HVM)```
2. Configure security group - ```SSH - custom```, ```HTTP - anywhere```
3. Launch instance using key-value pair - ```tuhin-aws```
4. ssh into EC2 machine - ```ssh -i "tuhin-aws.pem"``` ***```ubuntu```***```@```**```ec2-54-234-224-219.compute-1.amazonaws.com```**
5. ```sudo apt update --fix-missing```
6. ```sudo apt install -y docker.io```
7. ```sudo apt install -y docker-compose```
11. ```git clone https://github.com/tuhinsharma/imdb-rec-sys.git```
12. ```cd imdb-rec-sys```
13. Update the docker-compose-recsys.yml with suitable ```ACCESS_KEY``` and ```SECRET_ACCESS_KEY``` and ```AWS_BUCKET_NAME```. Port mapping should be ```"80:6006"```
8. ```sudo docker-compose -f docker-compose-recsys.yml build```
9. ```sudo docker-compose -f docker-compose-recsys.yml up ```

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

# How to deploy on an ECS using docker-compose?

1. configure ```aws``` with ```ACCESS_KEY``` and ```SECRET_ACCESS_KEY```
2. ```git clone https://github.com/tuhinsharma/imdb-rec-sys.git```
3. ```cd imdb-rec-sys```
4. ```aws ecr create-repository --repository-name recsys-ubuntu```
5. ```$(aws ecr get-login --no-include-email --region us-east-1)```
6. ```docker build -t recsys-ubuntu -f Dockerfile.ubuntu .```
7. ```docker tag recsys-ubuntu:latest 184213940252.dkr.ecr.us-east-1.amazonaws.com/recsys-ubuntu:latest```
8. ```docker push 184213940252.dkr.ecr.us-east-1.amazonaws.com/recsys-ubuntu:latest```
9. Update the docker-compose-aws.yml with suitable ```ACCESS_KEY``` and ```SECRET_ACCESS_KEY``` and ```AWS_BUCKET_NAME```. Port mapping should be ```"80:6006"```. ```image``` should be ```184213940252.dkr.ecr.us-east-1.amazonaws.com/recsys-ubuntu```
10. ```ecs-cli configure --region us-east-1 --cluster fastfilmz-analytics-cluster```
11. ```ecs-cli up --keypair tuhin-aws --capability-iam --size 1 --instance-type t2.micro --force --cluster fastfilmz-analytics-cluster --region us-east-1```
12. ```ecs-cli compose --project-name imdb-recsys --file docker-compose-aws.yml up```
13. In case Outdated ECS Agent - ```aws ecs update-container-agent --cluster fastfilmz-analytics-cluster --container-instance bc7e2a68-1be6-48d2-85a6-7f08232f298b```
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

14. If done with the service ```ecs-cli down```