"""CLI utilities: init DB, seed scenarios."""
import click
from flask.cli import FlaskGroup

from app import create_app
from models.extensions import db

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command("init-db")
def init_db():
    """Create tables."""
    with app.app_context():
        db.create_all()
        click.echo("Database tables created.")


@cli.command("seed")
@click.option("--force", is_flag=True, help="Clear and re-seed agents/scenarios")
def seed(force):
    """Load scenarios and agents from seed JSON."""
    from scripts.seed_db import seed_database

    with app.app_context():
        db.create_all()
        seed_database(force=force)
        click.echo("Seed complete.")


if __name__ == "__main__":
    cli()
