import os
import psutil
import time

import click
import matplotlib.pyplot as plt
import numpy as np
import torch.nn.functional as F

try:
    from picamera import PiCamera
except ModuleNotFoundError:
    print("No picamera")
from PIL import Image
from scipy.signal import fftconvolve


def _plot_autocorrelation_cross_section(autocorr_cross_section, axis):
    plt.title(f"Autocorrelation Cross Section ({axis} axis)")
    plt.ylabel("Normalized Autocorrelation")
    plt.xlabel(f"{axis} pixel")
    plt.plot(np.arange(len(autocorr_cross_section)), autocorr_cross_section)
    plt.show()


@click.group()
def calibrate():
    pass


@click.command()
@click.option("--psf-path", type=str, required=True)
@click.option("--autocorrelation-out-path", type=str, required=True)
def autocorrelate(psf_path, autocorrelation_out_path):
    psf_pil = Image.open(psf_path)
    psf_np = np.array(psf_pil)
    psf_np = psf_np.sum(axis=2)

    print(f"Pre-normalization: {psf_np.min()}, {psf_np.max()}")
    psf_np = (psf_np - psf_np.mean()) / psf_np.std()
    print(f"Post-normalization: {psf_np.min()}, {psf_np.max()}")

    psf_reversed_np = psf_np[::-1, ::-1]
    psf_autocorr_np = fftconvolve(psf_np, psf_reversed_np, mode="same") / np.prod(
        psf_np.shape
    )
    print(f"Autocorrelation {psf_autocorr_np.min()}, {psf_autocorr_np.max()}")

    print(f"psf_autocorr_np {psf_autocorr_np.shape}")
    autocorr_cross_section = psf_autocorr_np[:, psf_autocorr_np.shape[1] // 2].flatten()
    _plot_autocorrelation_cross_section(autocorr_cross_section, "y")

    autocorr_cross_section = psf_autocorr_np[psf_autocorr_np.shape[0] // 2].flatten()
    _plot_autocorrelation_cross_section(autocorr_cross_section, "x")

    psf_autocorr_pil = Image.fromarray(
        255.0 * ((psf_autocorr_np - psf_autocorr_np.min()) / psf_autocorr_np.max())
    )
    psf_autocorr_pil.convert("RGB").save(autocorrelation_out_path)


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
