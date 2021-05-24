import os
import psutil
import time

import click
import numpy as np
import torch.nn.functional as F

try:
    from picamera import PiCamera
except ModuleNotFoundError:
    print("No picamera")
from PIL import Image
from scipy.signal import fftconvolve


@click.group()
def calibrate():
    pass


@click.command()
@click.option("--psf-path", type=str, required=True)
def autocorrelate(psf_path):
    psf_pil = Image.open(psf_path)
    psf_np = np.array(psf_pil)
    psf_np = psf_np.sum(axis=2)
    # background = np.mean(psf_np[5:15, 5:15])
    # psf_np = psf_np - background
    print(psf_np.shape)
    print(f"Pre-normalization: {psf_np.min()}, {psf_np.max()}")
    psf_np = (psf_np - psf_np.mean()) / psf_np.std()
    # psf_np = 2.0 * ((psf_np - psf_np.min()) / psf_np.max()) - 1.0
    print(f"Post-normalization: {psf_np.min()}, {psf_np.max()}")
    psf_reversed_np = psf_np[::-1, ::-1]
    psf_autocorr = fftconvolve(psf_np, psf_reversed_np, mode="same")
    print(f"Autocorrelation {psf_autocorr.min()}, {psf_autocorr.max()}")
    Image.fromarray(
        255.0 * ((psf_autocorr - psf_autocorr.min()) / psf_autocorr.max())
    ).show()


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


calibrate.add_command(autocorrelate)
calibrate.add_command(extract_calibration_image)
calibrate.add_command(preview)


if __name__ == "__main__":
    calibrate()
