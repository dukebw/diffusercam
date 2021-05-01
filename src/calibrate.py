import os
import time

import click
from picamera import PiCamera


@click.group()
def calibrate():
    pass


@click.command()
@click.option("--output-path", type=str, required=True)
def preview(output_path):
    camera = PiCamera()

    camera.start_preview()
    while True:
        time.sleep(2)
        camera.capture(output_path)


calibrate.add_command(preview)


if __name__ == "__main__":
    calibrate()
