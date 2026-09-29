import rasterio
from rasterio.transform import from_origin
from pathlib import Path
import numpy as np

dem_dir = Path(r".\data\dem")

for hgt_file in dem_dir.glob("*.hgt"):
    data = np.fromfile(hgt_file, dtype=">i2")

    size = int(np.sqrt(data.size))

    if size * size != data.size:
        raise ValueError(
            f"Invalid HGT size in {hgt_file.name}: {data.size} samples"
        )

    data = data.reshape((size, size))

    name = hgt_file.stem + ".tif"

    tile_name = hgt_file.stem
    lat = int(tile_name[1:3])
    lon = int(tile_name[4:7])

    pixel_size = 1.0 / 3600.0

    transform = from_origin(
        lon,
        lat + 1,
        pixel_size,
        pixel_size
    )

    output = dem_dir / name

    with rasterio.open(
        output,
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

    print(f"Created: {output}")

print("HGT -> GeoTIFF conversion complete.")
