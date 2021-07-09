__version__ = "1.0.0"

import argparse
import os
import re
from rich import print
from rich.console import Console
console = Console()


def main(cwd=None):

	my_parser = argparse.ArgumentParser(description="check, update and upgrade your packages from here")

	my_parser.add_argument('-l','-list',
							action="store_true",
							dest="list",
							help='check list of upgradable packages from your list')

	my_parser.add_argument('-ud',"-update",
							action="store_true",
							dest="update",
							help="update your full packages list")

	my_parser.add_argument('-ml',"-mylist", 
							action="store_true",
							dest="mylist",
							help="print your list")

	my_parser.add_argument('-a',"-add",
							metavar="packages", 
							nargs="*",
							help="add packages in your list")

	my_parser.add_argument('-r',"-remove",
							metavar="packages", 
							nargs="*",
							help="remove packages from your list")

	my_parser.add_argument('-v',"-version",
							action="store_true",
							dest="version",
							help="check version of sachet")

	my_parser.add_argument("-new",
						action="store_true",
						dest="new",
						help="update sachet to latest version")


	args = my_parser.parse_args()

	list = bool(args.list)
	update = bool(args.update)
	mylist= bool(args.mylist)
	add = bool(args.a)
	remove = bool(args.r)
	version = bool(args.version)
	new = bool(args.new)

	here = os.path.dirname(__file__)
	file = os.path.join(here,"a.txt")


	if (args.list):
		pkg_list = os.popen("apt list --upgradable")
		outputs = pkg_list.readlines()

		with open(file) as f:
			add = f.read()
			f.close()

		imp_pkg = re.sub("[^\w]"," ", add).split()

		list_pkg = []

		up_list_pkg = []

		for pkg in imp_pkg:
			if pkg in str(outputs):
			# if re.search(r'\b' + pkg + r'\b', str(outputs)):
				console.print(f"[bold bright_red]{pkg}[/bold bright_red] found on")
				up_list_pkg.append(pkg)
				for i in outputs:
					#if pkg in i:
					if i.startswith(pkg):
						print(f"[bold bright_blue]->[/bold bright_blue] [bold yellow]{i}[/bold yellow]")
			else:
				list_pkg.append(pkg)

		print(f"List of packages, thats are already up to date =  \n[bold bright_cyan]{list_pkg}[/bold bright_cyan]")	
		print("")

	elif mylist:
		with open(file) as f:
			add = f.read()
			f.close()

		imp_pkg = re.sub("[^\w]"," ", add).split()	
		print(f"[bold bright_cyan]{imp_pkg}[/bold bright_cyan]")

	elif update:
		os.system('sudo apt update')

	elif (args.a)==[] or (args.a)!=None:

		if (add):
			with open(file) as f:
				add = f.read()
				f.close()

			imp_pkg = re.sub("[^\w]"," ", add).split()

			found_pkgs = []

			not_found_pkgs = []

			for i in (args.a):
				if i in imp_pkg:
					found_pkgs.append(i)
				else:
					not_found_pkgs.append(i)	

			sep = ", "
			a = sep.join(found_pkgs)

			if a!="":
				print(f"[bold bright_red]{a}[/bold bright_red] already in your list")		
			
			imp_pkg.extend(not_found_pkgs)

			b = sep.join(imp_pkg)

			with open(file, "w") as f:
				f.write(b)
				f.close()

			# print(imp_pkg)
			c = sep.join(not_found_pkgs)
			if c!="":
				print(f"[bold bright_magenta]{c}[/bold bright_magenta] package added in your list")
		else:
			print("[bold bright_red]no package given[/bold bright_red]")	

	elif (args.r)==[] or (args.r)!=None:

		if (remove):
			with open(file) as f:
				add = f.read()
				f.close()

			imp_pkg = re.sub("[^\w]"," ", add).split()

			not_found_pkgs = []
			removal_pkgs = []

			for i in (args.r):
				try:
					imp_pkg.remove(i)
					removal_pkgs.append(i)
				except:
					not_found_pkgs.append(i)				
					pass	
			# print(imp_pkg)	

			sep = ", "

			c = sep.join(not_found_pkgs)
			if c!="":
			    print(f"[bold bright_red]{c}[/bold bright_red] not found in your list")

			a = sep.join(imp_pkg)

			with open(file, "w") as f:
				f.write(a)
				f.close()

			b = sep.join(removal_pkgs)
			if b!="":
				print(f"[bold bright_magenta]{b}[/bold bright_magenta] removed from your list")
		else:
			print("[bold bright_red]no package given[/bold bright_red]")

	elif version:
		print(__version__)

	elif new:
		os.system("pip3 install sachet --upgrade")

	else:
		print("run sachet -h for help")

if __name__ == "__main__":
    main()
