"""Discover and download IRIS resources from the Open Data BCN catalog."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CATALOG_URL = (
    "https://opendata-ajuntament.barcelona.cat/data/api/3/action/"
    "package_show?id=iris"
)
RAW_DATA_DIR = Path("data/raw")
USER_AGENT = "barcelona-urban-life-signals/0.1"


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def get_resources() -> list[dict]:
    payload = fetch_json(CATALOG_URL)
    if not payload.get("success"):
        raise RuntimeError("Open Data BCN returned an unsuccessful response.")
    return payload["result"].get("resources", [])


def print_resources(resources: list[dict]) -> None:
    if not resources:
        print("No IRIS resources were returned by the catalog.")
        return

    for number, resource in enumerate(resources, start=1):
        print(f"\n[{number}] {resource.get('name') or 'Unnamed resource'}")
        print(f"    ID:     {resource.get('id', 'unknown')}")
        print(f"    Format: {resource.get('format') or 'unknown'}")
        print(f"    URL:    {resource.get('url') or 'missing'}")
        description = resource.get("description")
        if description:
            print(f"    Notes:  {' '.join(description.split())}")


def safe_filename(resource: dict) -> str:
    url_name = Path(resource["url"].split("?", 1)[0]).name
    resource_name = resource.get("name")
    candidate = (
        resource_name
        if resource_name and (url_name == "download" or "." not in url_name)
        else url_name
    )
    if not candidate:
        candidate = f"{resource['id']}.{resource.get('format', 'data').lower()}"
    return re.sub(r"[^A-Za-z0-9._-]+", "_", candidate)


def download_resource(resources: list[dict], resource_id: str, output_path: Path | None = None) -> Path:
    resource = next((item for item in resources if item.get("id") == resource_id), None)
    if resource is None:
        raise ValueError(f"Resource ID not found in the IRIS catalog: {resource_id}")
    if not resource.get("url"):
        raise ValueError("The selected resource has no download URL.")

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    destination = output_path if output_path is not None else RAW_DATA_DIR / safe_filename(resource)
    if not destination.resolve().is_relative_to(RAW_DATA_DIR.resolve()):
        raise ValueError("Downloads must remain under data/raw/.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(
            f"{destination} already exists; raw downloads are not overwritten."
        )

    request = Request(resource["url"], headers={"User-Agent": USER_AGENT})
    # Install only a complete download, without overwriting an existing snapshot.
    with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".part", delete=False) as output:
        temporary = Path(output.name)
        try:
            with urlopen(request, timeout=120) as response:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
                output.flush()
                length = response.headers.get("Content-Length")
                if length and temporary.stat().st_size != int(length):
                    raise ValueError("Incomplete download; no raw snapshot was installed.")
            os.link(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List live IRIS resources or download one into data/raw."
    )
    parser.add_argument(
        "--download",
        metavar="RESOURCE_ID",
        help="download the resource with this catalog ID",
    )
    parser.add_argument("--download-path", type=Path, help="new snapshot path under data/raw/; requires --download")
    parser.add_argument("--catalog-output", type=Path, help="preserve the full catalog JSON in a new file under data/raw/")
    args = parser.parse_args()
    if args.download_path and not args.download:
        parser.error("--download-path requires --download")
    return args


def main() -> int:
    args = parse_args()
    try:
        payload = fetch_json(CATALOG_URL)
        if not payload.get("success"):
            raise RuntimeError("Open Data BCN returned an unsuccessful response.")
        resources = payload["result"].get("resources", [])
        if args.catalog_output:
            if not args.catalog_output.resolve().is_relative_to(RAW_DATA_DIR.resolve()):
                raise ValueError("Catalog snapshots must remain under data/raw/.")
            args.catalog_output.parent.mkdir(parents=True, exist_ok=True)
            with args.catalog_output.open("x", encoding="utf-8") as stream:
                json.dump(payload, stream, ensure_ascii=False, indent=2)
            print(f"Preserved catalog: {args.catalog_output}")
        print_resources(resources)
        if args.download:
            destination = download_resource(resources, args.download, args.download_path)
            print(f"\nDownloaded without modification to: {destination}")
    except (HTTPError, URLError, TimeoutError, OSError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
