import click
import json

from rv.eval import Eval

@click.group
def cli():
    pass

@cli.command
@click.argument("input-str", type=str)
@click.option("-n", "--nreps", type=int, default=1000)
@click.option("-o", "--output", type=str, default="csv", help="csv,json")
@click.option("-d", "--decimals", type=int, default=2, help="decimals")
def random(input_str: str, nreps: int, output: str, decimals: int):
    ev = Eval.from_str(input_str)
    df = ev.random(nreps)
    df = df.round(decimals)
    if output == "csv":
        click.echo(df.to_csv(index=False))
    elif output == "json":
        click.echo(json.dumps(df.to_dict(orient="records")))

if __name__=="__main__":
    cli()
