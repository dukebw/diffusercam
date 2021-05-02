import os
import psutil
import time

import click
from picamera import PiCamera
from PIL import Image


@click.group()
def calibrate():
    pass


@click.command()
@click.option("--output-path", type=str, required=True)
def preview(output_path):
    camera = PiCamera()

    while True:
        time.sleep(2)
        for proc in psutil.process_iter():
            if proc.name() == "display":
                proc.kill()

        camera.capture(output_path)
        img = Image.open(output_path)
        img.show()


calibrate.add_command(preview)


if __name__ == "__main__":
    calibrate()
