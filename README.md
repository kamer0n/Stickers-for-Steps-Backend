# StepsServer

## About

This is the back-end server developed for the Stickers for Steps app. It is written in Python using Django and DjangoRestFramework.

## Installation  

1. Clone repo

2. Install requirements:

`pip install -r requirements.txt`  

3. Set environmental variables:

`AWS_ACCESS_KEY_ID`     
`AWS_SECRET_ACCESS_KEY`     
`AWS_STORAGE_BUCKET_NAME`      
`DATABASE_URL`  
`USE_S3 (TRUE or FALSE)`    
`chatAPI`   
`chatSecret`


4. Ensure database structure is up to date:

`python manage.py makemigrations`  
`python manage.py migrate`  

5. Run the server:  
`python manage.py runserver`  
