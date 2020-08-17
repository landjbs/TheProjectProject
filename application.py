import sys

from app import create_app, config

# get desired config
try:
    config_name = sys.argv[1]
    from werkzeug.utils import import_string
    config = import_string(f'app.config.{config_name}_config')
except IndexError:
    config = config.production_config
print(f'CONFIG: {config}')

application = create_app(config)

if __name__ == '__main__':
    application.run()
