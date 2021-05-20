import os
import psutil
import time

import click
import numpy as np

try:
    from picamera import PiCamera
except ModuleNotFoundError:
    print("No picamera")
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
        print(np.array(img).min(), np.array(img).max())
        img.show()


@click.command()
@click.option("--input-path", type=str, required=True)
@click.option("--output-path", type=str, required=True)
def extract_calibration_image(input_path, output_path):
    input_img = Image.open(input_path)
    input_img = np.array(input_img)[:, :, 1]
    input_img = input_img * (255.0 / input_img.max())
    input_img = input_img.astype(np.uint8)

    output_img = Image.fromarray(input_img)
    output_img.save(output_path)


calibrate.add_command(extract_calibration_image)
calibrate.add_command(preview)


if __name__ == "__main__":
    calibrate()
