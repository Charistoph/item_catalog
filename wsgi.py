import sys

sys.path.insert(0, '/var/www/catalog')


from catalog import app as application

application.secret_key = 'super_secret_key'

application.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql://'
    'catalog:password@localhost/catalog')
