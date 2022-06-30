from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
import os
import boto3
import mysql.connector

import os

DATABASE_REGION = 'us-east-2'
DATABASE_CERT = 'cert/us-east-2-bundle.pem'
DATABASE_HOST = os.environ['DATABASE_HOST']
DATABASE_PORT = os.environ['DATABASE_PORT']
DATABASE_USER = os.environ['DATABASE_USER']
DATABASE_NAME = os.environ['DATABASE_NAME']

os.environ['LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN'] = '1'

PORT = int(os.environ.get('PORT'))

rds = boto3.client('rds')
token = rds.generate_db_auth_token(
        DBHostname=DATABASE_HOST,
        Port=DATABASE_PORT,
        DBUsername=DATABASE_USER,
        Region=DATABASE_REGION
    )


def all_books(request):
    message = '<html><head><title>App Runner Private RDS Connect Test</title></head><body>'

    try:
        mydb =  mysql.connector.connect(
            host=DATABASE_HOST,
            user=DATABASE_USER,
            passwd=token,
            port=DATABASE_PORT,
            database=DATABASE_NAME,
            ssl_ca=DATABASE_CERT
        )
 

        mycursor = mydb.cursor()
        mycursor.execute('SELECT name, title, year FROM authors, books WHERE authors.authorId = books.authorId ORDER BY year')
        title = 'Books'
        
        message += '<h1>' + title + '</h1>'
        message += '<ul>'
        for (name, title, year) in mycursor:
            message += '<li>' + name + ' - ' + title + ' (' + str(year) + ')</li>'
        message += '</ul>'
        message += '</body></html>'
    except Exception as e:
        message += '</ul>'
        message += '</body></html>'
        message += 'Database connection failed due to {}'.format(e)
        print('Database connection failed due to {}'.format(e))         

    return Response(message)

if __name__ == '__main__':

    with Configurator() as config:
        config.add_route('all_books', '/')
        config.add_view(all_books, route_name='all_books')
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', PORT, app)
    server.serve_forever()