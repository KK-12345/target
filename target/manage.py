from flask_script import Manager, Server
from target.settings import app
# import ssl
# context = ssl.SSLContext()
# context.use_privatekey_file('server.key')
# context.use_certificate_file('server.crt')

manager = Manager(app)

manager.add_command("runserver", Server(
    host='0.0.0.0',
    port=8800)
)

if __name__ == "__main__":
    manager.run()
