import requests
from pathlib import Path
import time

OUT = Path("data/dem")
OUT.mkdir(parents=True, exist_ok=True)

tiles = {
    "N30E079": "https://s3.amazonaws.com/elevation-tiles-prod/skadi/N30/N30E079.hgt.gz",
    "N30E080": "https://s3.amazonaws.com/elevation-tiles-prod/skadi/N30/N30E080.hgt.gz",
}

for name, url in tiles.items():
    output = OUT / f"{name}.hgt.gz"

    for attempt in range(1, 4):
        try:
            print(f"Downloading {name} (attempt {attempt}/3)...")

            with requests.get(
                url,
                stream=True,
                timeout=(20, 180)
            ) as response:
                response.raise_for_status()

                with open(output, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)

            size_mb = output.stat().st_size / (1024 * 1024)
            print(f"{name}: {size_mb:.2f} MB")

            # Validate gzip completely.
            import gzip

            with gzip.open(output, "rb") as gz:
                while gz.read(1024 * 1024):
                    pass

            print(f"{name}: DOWNLOAD + GZIP CHECK OK")
            break

        except Exception as error:
            print(f"{name}: FAILED -> {error}")

            if output.exists():
                output.unlink()

            if attempt == 3:
                raise

            time.sleep(3)

print("All DEM downloads completed successfully.")
