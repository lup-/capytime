import asyncio
import argparse
import os
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from app.yandex_client import yandex_telemost_auth, refresh_telemost_cookies, create_conference
from app.database import connect_db, close_db, get_db
from app.config import settings

STATIC_DIR = Path(__file__).parent / "static"


async def generate_sitemap(output_path: str, base_url: str):
    await connect_db()
    db = get_db()

    slugs = []
    if db is not None:
        cursor = db.psychologists.find(
            {"slug": {"$exists": True, "$ne": ""}},
            {"slug": 1, "_id": 0},
        )
        async for doc in cursor:
            slugs.append(doc["slug"])

    await close_db()

    urlset = Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    static_pages = [("/", "1.0"), ("/info", "0.7")]

    for f in sorted(STATIC_DIR.rglob("*.json")):
        rel = f.relative_to(STATIC_DIR)
        page_path = "/" + str(rel.with_suffix(""))
        has_slash = "/" in str(rel.with_suffix(""))
        priority = "0.8" if not has_slash else "0.7"
        static_pages.append((page_path, priority))

    for path, priority in static_pages:
        url = SubElement(urlset, "url")
        loc = SubElement(url, "loc")
        loc.text = f"{base_url}{path}"
        prio = SubElement(url, "priority")
        prio.text = priority

    for slug in slugs:
        url = SubElement(urlset, "url")
        loc = SubElement(url, "loc")
        loc.text = f"{base_url}/booking/{slug}"
        prio = SubElement(url, "priority")
        prio.text = "0.9"

    rough_string = tostring(urlset, encoding="unicode")
    reparsed = minidom.parseString(rough_string)
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + reparsed.toprettyxml(indent="  ")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    print(f"Sitemap generated: {output_path} ({len(slugs)} psychologists)")


async def main():
    parser = argparse.ArgumentParser(description="CapyTime CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Auth command
    auth_parser = subparsers.add_parser("auth", help="Authenticate with Yandex Telemost")

    # Refresh command
    refresh_parser = subparsers.add_parser("refresh", help="Refresh Telemost cookies")

    # Create conference command
    create_parser = subparsers.add_parser("conference", help="Create a new Telemost conference")

    # Sitemap command
    sitemap_parser = subparsers.add_parser("sitemap", help="Generate sitemap.xml")
    sitemap_parser.add_argument("--output", default="/app/dist/client/sitemap.xml", help="Output path for sitemap.xml")
    sitemap_parser.add_argument("--url", default=settings.FRONTEND_URL, help="Base URL for the site")

    args = parser.parse_args()

    if args.command == "auth":
        success = await yandex_telemost_auth()
        print(f"Auth result: {'Success' if success else 'Failed'}")
    elif args.command == "refresh":
        success = await refresh_telemost_cookies()
        print(f"Refresh result: {'Success' if success else 'Failed'}")
    elif args.command == "conference":
        url = await create_conference()
        if url:
            print(f"Conference URL: {url}")
        else:
            print("Failed to create conference")
    elif args.command == "sitemap":
        await generate_sitemap(args.output, args.url)


if __name__ == "__main__":
    asyncio.run(main())
