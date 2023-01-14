import argparse
from .main import *
from apt_pro import __version__

package_name = "apt-pro"

example_uses = '''example:
   apt-pro list
   apt-pro mylist
   apt-pro add package_name
   apt-pro remove package_name'''

def main(argv = None):
    parser = argparse.ArgumentParser(prog=package_name, description="check, update and upgrade your packages from your custom list", epilog=example_uses, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="check list of upgradable packages from your list")

    mylist_parser = subparsers.add_parser("mylist", help="print your list")

    add_parser = subparsers.add_parser('add', help="add packages in your list")
    add_parser.add_argument("packages", nargs='+',)

    remove_parser = subparsers.add_parser('remove', help="remove packages from your list")
    remove_parser.add_argument("packages", nargs='+',)

    updateapt_parser = subparsers.add_parser('update', help="update your apt packages list")

    upgradepkg_parser = subparsers.add_parser('upgrade', help="upgrade your packages from your custom list")

    newJkb_parser = subparsers.add_parser('new', help="upgrade apt-pro to latest version")    

    parser.add_argument('-v',"--version",
                            action="store_true",
                            dest="version",
                            help="check version of deb")

    args = parser.parse_args(argv)

    if args.command == "mylist":
        return mylist()
    elif args.command == "list":
        return upgradable_list()
    elif args.command == "add":
        return add_pkg(args.packages)
    elif args.command == "remove":
        return remove_pkg(args.packages)
    elif args.command == "upgrade":
        return upgrade_pkg()
    elif args.command == "update":
        return mylist()
    elif args.command == "new":
        return new()
    elif args.version:
        return __version__
    else:
        parser.print_help()

if __name__ == "__main__":
    raise SystemExit(main())