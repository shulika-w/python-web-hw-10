import os
import django

from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Connection to mongodb
client = MongoClient(
    "mongodb://localhost:27017/",
    server_api=ServerApi('1')
)

db = client.hw_10

# Path to django DB models (postgres)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hw_project.settings")
django.setup()

from quotes.models import Quote, Tag, Author

# Get all authors from MongoDB
authors = db.authors.find()

# Fill data in postgress using QuerySet command get_or_create (Django ORM)
for author in authors:
    Author.objects.get_or_create(
        fullname=author["fullname"],
        born_date=author["born_date"],
        born_location=author["born_location"],
        description=author["description"]
    )

# get quotes from MongoDB
quotes = db.quotes.find()

for quote in quotes:
    tags = []
    for tag in quote['tags']:
        t, *_ = Tag.objects.get_or_create(name=tag)
        tags.append(t)
    # check if quote exists (0-not exist, 1-exist)
    exist_quote = bool(len(Quote.objects.filter(quote=quote['quote'])))
    # if quote not exist - creat a new
    if not exist_quote:
        # Get author from MongoDB
        author = db.authors.find_one({'_id': quote['author']})
        # Find author (a) in postgress
        a = Author.objects.get(fullname=author['fullname'])
        # Add quote to postgress
        q = Quote.objects.create(
            quote=quote['quote'],
            author=a
        )
        # add relation field( tags to the quote)
        for tag in tags:
            q.tags.add(tag)

# to start script use: python -m utils.postgres_migration