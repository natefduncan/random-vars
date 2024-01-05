import click

@click.group
def cli():
    pass

@cli.command
def random():
    pass

# x ~ norm(1, 2); y ~ exp(1); z = x*y 

if __name__=="__main__":
    cli()
