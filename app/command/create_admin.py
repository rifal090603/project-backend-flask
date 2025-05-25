from flask.cli import with_appcontext
import click
from app.models.auth_models import User
from app import db

@click.command('create-admin')
@with_appcontext
@click.option('--username', prompt=True, help='Username untuk admin')
@click.option('--email', prompt=True, help='Email untuk admin')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password untuk admin')
def create_admin(username, email, password):
    admin = User.query.filter((User.username == username) | (User.email == email)).first()
    if admin:
        click.echo(f"User dengan username '{username}' atau email '{email}' sudah terdaftar.")
        return
    
    admin = User(username=username, email=email, role='admin')

    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
  
    print(f"Admin sudah terdaftar: {admin.username} ({admin.email})")