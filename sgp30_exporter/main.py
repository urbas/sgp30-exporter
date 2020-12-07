import click

from sgp30_exporter import app


@click.command()
@click.option(
    "--listen-address",
    default="0.0.0.0",
    help="The address on which to listen for HTTP requests.",
    show_default=True,
)
@click.option(
    "--listen-port",
    default=9895,
    help="The port on which to listen for HTTP requests.",
    show_default=True,
)
def main(listen_address, listen_port):
    app.create_app().run(host=listen_address, port=listen_port)
