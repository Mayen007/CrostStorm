from app import create_app, cli, db
from app.models import User, Post, Notification, Message

app = create_app()


cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Message': Message, 'Notification': Notification}


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)