import click
import json
from typing import Optional

from stats.eval import Eval

@click.group
def cli():
    pass

@cli.command
@click.option("-i", "--input-str", type=str, default="")
@click.option("-f", "--filename", type=click.Path(exists=True))
@click.option("-n", "--nreps", type=int, default=1000)
@click.option("-o", "--output", type=str, default="csv", help="csv,json")
@click.option("-d", "--decimals", type=int, default=2, help="decimals")
@click.option("-s", "--seed", type=int, default=None, help="decimals")
def random(input_str: str, filename: click.Path, nreps: int, output: str, decimals: int, seed: Optional[int]):
    if input_str == "":
        with open(str(filename), "r") as f:
            input_str = f.read()

    ev = Eval.from_str(input_str)
    df = ev.random(nreps, seed, decimals)
    df = df.round(decimals)
    if output == "csv":
        click.echo(df.to_csv(index=False), nl=False)
    elif output == "json":
        click.echo(json.dumps(df.to_dict(orient="records")))

if __name__=="__main__":
    cli()
