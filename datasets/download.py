# Python Standard Library
import bz2
import os

# Third-party Libraries
import requests
from tqdm import tqdm

filename = "simplewiki-latest-pages-articles.xml.bz2"
output_file = filename[:-4]

url = f"https://dumps.wikimedia.org/simplewiki/latest/{filename}"

if os.path.exists(output_file):
    print(f"{output_file} already exists, skipping download and decompression.")
else:
    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))

    CHUNK_SIZE = 1024 * 1024  # 1 MB

    with (
        open(filename, "wb") as f,
        tqdm(
            desc=filename,
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar,
    ):
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            f.write(chunk)
            bar.update(len(chunk))

    print("Download complete.")

    with (
        bz2.open(filename, "rb") as f_in,
        open(output_file, "wb") as f_out,
        tqdm(
            desc="Decompressing",
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar,
    ):
        while chunk := f_in.read(CHUNK_SIZE):
            f_out.write(chunk)
            bar.update(len(chunk))

    print("Decompression complete.")

    os.remove(filename)
