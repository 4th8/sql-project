import datetime
def count():
    diff = datetime.datetime(2016, 9, 03) - datetime.datetime.today()
    days = diff.days
    print days

count()