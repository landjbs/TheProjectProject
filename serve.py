from app import create_app, config

application = create_app()

if __name__ == '__main__':
    application.run(host='127.0.0.1')
