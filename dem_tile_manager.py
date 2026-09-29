from pathlib import Path
import gzip
import math
import shutil

import numpy as np
import rasterio
import requests
from rasterio.transform import from_origin


DEM_DIR = Path(__file__).resolve().parent / "data" / "dem"
DEM_DIR.mkdir(parents=True, exist_ok=True)


def tile_name(latitude: float, longitude: float) -> str:
    lat = math.floor(float(latitude))
    lon = math.floor(float(longitude))

    lat_name = f"N{lat:02d}" if lat >= 0 else f"S{abs(lat):02d}"
    lon_name = f"E{lon:03d}" if lon >= 0 else f"W{abs(lon):03d}"

    return f"{lat_name}{lon_name}"


def ensure_dem_tile(latitude: float, longitude: float):
    name = tile_name(latitude, longitude)

    tif_path = DEM_DIR / f"{name}.tif"
    hgt_path = DEM_DIR / f"{name}.hgt"
    gz_path = DEM_DIR / f"{name}.hgt.gz"

    if tif_path.exists():
        return tif_path

    if not hgt_path.exists():
        url = (
            "https://s3.amazonaws.com/"
            f"elevation-tiles-prod/skadi/{name[:3]}/{name}.hgt.gz"
        )

        print(f"Downloading DEM tile: {name}")

        response = requests.get(
            url,
            stream=True,
            timeout=(20, 180)
        )
        response.raise_for_status()

        with open(gz_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        with gzip.open(gz_path, "rb") as src, open(hgt_path, "wb") as dst:
            shutil.copyfileobj(src, dst)

        gz_path.unlink(missing_ok=True)

    data = np.fromfile(hgt_path, dtype=">i2")

    size = int(math.sqrt(data.size))

    if size * size != data.size:
        raise ValueError(
            f"Invalid HGT size for {name}: {data.size}"
        )

    data = data.reshape((size, size))

    lat = math.floor(float(latitude))
    lon = math.floor(float(longitude))

    transform = from_origin(
        lon,
        lat + 1,
        1.0 / (size - 1),
        1.0 / (size - 1)
    )

    with rasterio.open(
        tif_path,
        "w",
        driver="GTiff",
        height=size,
        width=size,
        count=1,
        dtype="int16",
        transform=transform,
        nodata=-32768
    ) as dst:
        dst.write(data, 1)

    print(f"DEM tile ready: {tif_path}")

    return tif_path
