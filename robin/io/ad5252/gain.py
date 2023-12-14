import ad5252
import click


@click.command()
@click.option("--write", default=None, help="Write to one or both channels")
@click.option("--read", is_flag=True, help="Read from both channels")
def main(write, read):
    ad = ad5252.AD5252()
    if write is not None:
        if "," in write:
            res = [float(part.strip()) for part in write.split(",")]
        else:
            res = 2 * [float(write.strip())]
        [ad.write(value, channel) for channel, value in enumerate(res)]
    if read is not None:
        res = [ad.read(channel) for channel in [0, 1]]
        print(" ".join([str(val) for val in res]))


if __name__ == "__main__":
    main()
