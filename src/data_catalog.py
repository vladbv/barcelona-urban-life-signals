"""Discover and download IRIS resources from the Open Data BCN catalog."""

from __future__ import annotations

import argparse
import json
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


def download_resource(resources: list[dict], resource_id: str) -> Path:
    resource = next((item for item in resources if item.get("id") == resource_id), None)
    if resource is None:
        raise ValueError(f"Resource ID not found in the IRIS catalog: {resource_id}")
    if not resource.get("url"):
        raise ValueError("The selected resource has no download URL.")

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    destination = RAW_DATA_DIR / safe_filename(resource)
    if destination.exists():
        raise FileExistsError(
            f"{destination} already exists; raw downloads are not overwritten."
        )

    request = Request(resource["url"], headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=120) as response, destination.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        resources = get_resources()
        print_resources(resources)
        if args.download:
            destination = download_resource(resources, args.download)
            print(f"\nDownloaded without modification to: {destination}")
    except (HTTPError, URLError, TimeoutError, OSError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
