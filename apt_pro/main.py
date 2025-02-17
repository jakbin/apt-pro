import os
import re
import apt
import sqlite3
from rich import print
from pathlib import Path
from shutil import copy2
from rich.prompt import Prompt

cache = apt.Cache()

db_path = os.path.dirname(__file__)
dbFile = os.path.join(db_path,"apt-pro.db")

home_path = Path.home()
if os.path.isfile(os.path.join(home_path, ".apt-pro/apt-pro.db")):
    db = os.path.join(home_path, ".apt-pro/apt-pro.db")
else:
    if os.path.isdir(os.path.join(home_path, '.apt-pro')):
        copy2(dbFile,os.path.join(home_path, ".apt-pro"))
        db = os.path.join(home_path, ".apt-pro/apt-pro.db")
    else:
        os.mkdir(os.path.join(home_path, '.apt-pro'))
        copy2(dbFile,os.path.join(home_path, ".apt-pro"))
        db = os.path.join(home_path, ".apt-pro/apt-pro.db")

conn  = sqlite3.connect(db)
cursor = conn.cursor()

def mylist():
    pkgs = cursor.execute("SELECT pkg_name FROM pkgs ORDER BY pkg_name").fetchall()
    conn.close()

    results = []
    for i in pkgs:
        for pkg in i:
            results.append(pkg)
    print(f"[bold bright_cyan]{results}[/bold bright_cyan]\n")

def upgradable_list():
    pkgs = cursor.execute("SELECT pkg_name FROM pkgs ORDER BY pkg_name").fetchall()
    conn.close()

    imp_pkg = []
    for i in pkgs:
        for pkg in i:
            imp_pkg.append(pkg)

    list_pkg = []
    upgradable_pkg_list = []

    for pkg in imp_pkg:
        try:
            if cache[pkg].is_upgradable:
                print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{pkg}[/bold yellow] {cache[pkg].versions[0].version} {cache[pkg].architecture()} (upgradable from: {cache[pkg].versions[1].version})")
            else:
                list_pkg.append(pkg)
        except KeyError:
            print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{pkg}[/bold yellow] not found")

    print(f"\nList of packages, that are already up to date =  \n[bold bright_cyan]{list_pkg}[/bold bright_cyan]\n")   

def update_apt():
    os.system('sudo apt update')

def add_pkg(packages):
    pkgs = cursor.execute("SELECT pkg_name FROM pkgs ORDER BY pkg_name").fetchall()

    results = []
    for i in pkgs:
        for pkg in i:
            results.append(pkg)

    found_pkgs = []
    for pkg in packages:
        if pkg in results:
            found_pkgs.append(pkg)
        else:
            try:
                cache[pkg].name
                cursor.execute("INSERT INTO pkgs (id, pkg_name) VALUES (NULL, ?)", (pkg,),)
                print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{pkg}[/bold yellow] added in your list")
            except KeyError:
                print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{pkg}[/bold yellow] [bold bright_red]did not found in apt database[/bold bright_red]")
    conn.commit()
    conn.close()
    print("")
    sep = ", "
    c = sep.join(found_pkgs)
    if c!="":
        print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{c}[/bold yellow] already found in your list\n")


def remove_pkg(packages):
    pkgs = cursor.execute("SELECT pkg_name FROM pkgs ORDER BY pkg_name").fetchall()

    results = []
    for i in pkgs:
        for pkg in i:
            results.append(pkg)

    not_found_pkgs = []
    removal_pkgs = []

    for i in (packages):
        if i in results:
            print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{i}[/bold yellow] founded in your list")
            try:
                cursor.execute("DELETE FROM pkgs WHERE pkg_name = ?", (i,),)
                removal_pkgs.append(i)
            except sqlite3.ProgrammingError as e:
                print(e)            
        else:
            not_found_pkgs.append(i)
    conn.commit()
    conn.close()
    sep = ", "

    c = sep.join(not_found_pkgs)
    if c!="":
        print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{c}[/bold yellow] not found in your list\n")

    b = sep.join(removal_pkgs)
    if b!="":
        print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{b}[/bold yellow] removed from your list\n")

def upgrade_pkg():
    pkgs = cursor.execute("SELECT pkg_name FROM pkgs ORDER BY pkg_name").fetchall()

    imp_pkg = []
    for i in pkgs:
        for pkg in i:
            imp_pkg.append(pkg)

    list_pkg = []
    upgradable_pkg_list = []

    for pkg in imp_pkg:
        try:
            if cache[pkg].is_upgradable:
                upgradable_pkg_list.append(pkg)
                print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{pkg}[/bold yellow] {cache[pkg].versions[0].version} {cache[pkg].architecture()} (upgradable from: {cache[pkg].versions[1].version})")
        except KeyError:
            print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{pkg}[/bold yellow] not found")

    upgrade_list_pkg = []
    for pkg in upgradable_pkg_list:
        a = pkg.split('/')[0]
        upgrade_list_pkg.append(a)

    print("")
    choice_pkg = []
    for pkg in upgrade_list_pkg:
        yes = {'yes','y','ye',''}
        choice = Prompt.ask(f"Do you want upgrade [bold yellow]{pkg}[/bold yellow] [Y/n]").lower()
        if choice in yes:
            choice_pkg.append(pkg)
        else:
            pass    

    sep = " "
    b = sep.join(choice_pkg)
    
    if choice_pkg != []:
        if os.geteuid() == 0:
            os.system(f"apt install {b} -y") 
        else:
            os.system(f"sudo apt install {b} -y")

def upgrade_pkg_regex(pattern):
    # pkgs = cursor.execute("SELECT pkg_name FROM pkgs ORDER BY pkg_name").fetchall()

    # Convert pattern from glob-style to regex
    # Replace * with .* for regex matching
    regex_pattern = pattern.replace('*', '.*')

    print(f"[bold bright_cyan]Checking packages matching pattern: {pattern}[/bold bright_cyan]\n")

    upgrade_list_pkg = []

    for pkg_name in cache.keys():
        if re.match(regex_pattern, pkg_name):
            pkg = cache[pkg_name]
            if pkg.is_upgradable:
                upgrade_list_pkg.append(pkg.name)
                current_version = pkg.installed.version if pkg.installed else "not installed"
                candidate_version = pkg.candidate.version
                
                print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{pkg_name}[/bold yellow] "
                      f"{pkg.architecture()} "
                      f"{candidate_version}, (upgradable from: {current_version})")


    if not upgrade_list_pkg:
        print(f"\n[bold bright_red]No upgradable packages found matching pattern: {pattern}[/bold bright_red]")
        return

    print(f"\n[bold bright_cyan]Found {len(upgrade_list_pkg)} packages to upgrade[/bold bright_cyan]")
    
    # Ask for confirmation before upgrading
    yes = {'yes', 'y', 'ye', ''}
    choice = Prompt.ask(
        f"Do you want to upgrade all matching packages? [Y/n]"
    ).lower()

    if choice in yes:
        packages_to_upgrade = " ".join(upgrade_list_pkg)
        if os.geteuid() == 0:
            os.system(f"apt install {packages_to_upgrade} -y")
        else:
            os.system(f"sudo apt install {packages_to_upgrade} -y")
    else:
        print("\n[bold yellow]Upgrade cancelled[/bold yellow]")

def upgrade_apt_pro():
    os.system("pip3 install apt-pro --upgrade")
