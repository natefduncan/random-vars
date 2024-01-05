import click

from rv.eval import Eval

@click.group
def cli():
    pass

@cli.command
@click.argument("input-str", type=str)
@click.option("--nreps", type=int, default=1000)
def random(input_str: str, nreps: int):
    ev = Eval.from_str(input_str)
    click.echo(ev.random(nreps))

# x ~ norm(1, 2); y ~ exp(1); z = x*y; 

if __name__=="__main__":
    cli()
