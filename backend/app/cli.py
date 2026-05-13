import asyncio
import argparse
from app.yandex_client import yandex_telemost_auth, refresh_telemost_cookies, create_conference


async def main():
    parser = argparse.ArgumentParser(description="Yandex Telemost CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Auth command
    auth_parser = subparsers.add_parser("auth", help="Authenticate with Yandex Telemost")

    # Refresh command
    refresh_parser = subparsers.add_parser("refresh", help="Refresh Telemost cookies")

    # Create conference command
    create_parser = subparsers.add_parser("conference", help="Create a new Telemost conference")

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


if __name__ == "__main__":
    asyncio.run(main())
