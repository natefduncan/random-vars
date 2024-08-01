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

def is_number(x):
    return x.replace('.','',1).isdigit()

@cli.command()
@click.argument("input", type=click.File("rb"))
@click.option("-b", "--breaks", type=str, default=None)
@click.option("-i", "--ignore-blanks", is_flag=True, default=False)
def cum_dist(input, breaks, ignore_blanks):
    # Read data; assume header in first line
    input_lines = input.read().decode("utf-8").split("\n")
    data = {}
    header = input_lines.pop(0).strip()

    # Create counts
    for row in input_lines:
        if row:
            value = row.strip().replace("\"", "")
            value = None if not value else value
            data[value] = data.get(value, 0) + 1
    items = list(data.items())
    if ignore_blanks:
        items = [i for i in items if i[0]]

    # Combine items for sorting
    labels = [i[0] for i in items] 
    sort_keys = [float(label) if label and is_number(label) else 0 for label in labels]
    counts = [i[1] for i in items]

    items = list(zip(labels, sort_keys, counts))
    total_count = sum([i[2] for i in items])

    # Generate output and write to stdout
    output = "\t".join([header, f"{header}_count", f"{header}_per", f"{header}_count_cum", f"{header}_per_cum"])

    break_labels = [i.strip() for i in breaks.split(",")] if breaks else labels
    break_sort_keys = [float(label) if label and is_number(label) else 0 for label in break_labels] if breaks else sort_keys
    break_items = zip(break_labels, break_sort_keys)
    break_items_sorted = sorted(break_items, key=lambda x: x[1])

    prev_count = 0
    for label, sort_key in break_items_sorted:
        count_cum = sum([i[2] for i in items if i[1] <= sort_key])
        per_cum = round(count_cum / total_count, 3)
        count = count_cum - prev_count
        per = round(count / total_count, 3)
        prev_count = count_cum
        row = [label, count, per, count_cum, per_cum]
        row_strs = [str(i) for i in row]
        output += "\n" + "\t".join(row_strs)
    click.echo(output)

if __name__=="__main__":
    cli()
