import os
import re
import apt
import sqlite3
import subprocess
from rich import print
from pathlib import Path
from shutil import copy2
from rich.prompt import Prompt

cache = apt.Cache()

db_path = os.path.dirname(__file__)
dbFile = os.path.join(db_path, "apt-pro.db")

home_path = Path.home()
apt_pro_dir = home_path / ".apt-pro"
db = apt_pro_dir / "apt-pro.db"

apt_pro_dir.mkdir(exist_ok=True)
if not db.exists():
    copy2(dbFile, db)
db = str(db)

conn = sqlite3.connect(db)
cursor = conn.cursor()

# Create interrupted_upgrades table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS interrupted_upgrades (
    pkg_name TEXT PRIMARY KEY
)
""")


def mylist():
    pkgs = cursor.execute("SELECT pkg_name FROM pkgs ORDER BY pkg_name").fetchall()
    conn.close()

    results = [pkg[0] for pkg in pkgs]
    print(f"[bold bright_cyan]{results}[/bold bright_cyan]\n")


def upgradable_list():
    pkgs = cursor.execute("SELECT pkg_name FROM pkgs ORDER BY pkg_name").fetchall()
    conn.close()

    imp_pkg = [pkg[0] for pkg in pkgs]

    list_pkg = []

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

    results = [pkg[0] for pkg in pkgs]

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

    if found_pkgs:
        print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{', '.join(found_pkgs)}[/bold yellow] already found in your list\n")


def remove_pkg(packages):
    pkgs = cursor.execute("SELECT pkg_name FROM pkgs ORDER BY pkg_name").fetchall()

    results = [pkg[0] for pkg in pkgs]

    not_found_pkgs = []
    removal_pkgs = []

    for i in (packages):
        if i in results:
            print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{i}[/bold yellow] found in your list")
            try:
                cursor.execute("DELETE FROM pkgs WHERE pkg_name = ?", (i,),)
                removal_pkgs.append(i)
            except sqlite3.ProgrammingError as e:
                print(e)
        else:
            not_found_pkgs.append(i)
    conn.commit()
    conn.close()

    if not_found_pkgs:
        print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{', '.join(not_found_pkgs)}[/bold yellow] not found in your list\n")

    if removal_pkgs:
        print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{', '.join(removal_pkgs)}[/bold yellow] removed from your list\n")


def upgrade_pkg():
    # First check for any interrupted upgrades
    interrupted_pkgs = cursor.execute("SELECT pkg_name FROM interrupted_upgrades").fetchall()
    interrupted_list = [pkg[0] for pkg in interrupted_pkgs]

    if interrupted_list:
        print("\n[bold bright_cyan]Found previously interrupted upgrades:[/bold bright_cyan]")
        for pkg in interrupted_list:
            print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{pkg}[/bold yellow]")

        yes = {'yes','y','ye',''}
        choice = Prompt.ask("\nDo you want to attempt upgrading these packages first? [Y/n]").lower()
        if choice in yes:
            packages_to_upgrade = " ".join(interrupted_list)
            try:
                cmd = ["apt", "install", "-y"] + packages_to_upgrade.split()
                if os.geteuid() != 0:
                    cmd.insert(0, "sudo")

                process = subprocess.run(cmd, check=True)

                if process.returncode == 0:
                    cursor.execute("DELETE FROM interrupted_upgrades")
                    conn.commit()

            except subprocess.CalledProcessError as e:
                print(f"\n[bold bright_red]Package installation failed with error code {e.returncode}[/bold bright_red]")
                return
            except KeyboardInterrupt:
                print("\n[bold bright_red]Upgrade interrupted again. Will retry next time.[/bold bright_red]")
                return

    pkgs = cursor.execute("SELECT pkg_name FROM pkgs ORDER BY pkg_name").fetchall()

    # Get all packages except the interrupted ones
    imp_pkg = [pkg[0] for pkg in pkgs if pkg[0] not in interrupted_list]

    upgradable_pkg_list = []

    for pkg in imp_pkg:
        try:
            if cache[pkg].is_upgradable:
                upgradable_pkg_list.append(pkg)
                print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{pkg}[/bold yellow] {cache[pkg].versions[0].version} {cache[pkg].architecture()} (upgradable from: {cache[pkg].versions[1].version})")
        except KeyError:
            print(f"[bold bright_red]->[/bold bright_red] [bold yellow]{pkg}[/bold yellow] not found")

    upgrade_list_pkg = [pkg.split('/')[0] for pkg in upgradable_pkg_list]

    print("")
    choice_pkg = []
    for pkg in upgrade_list_pkg:
        yes = {'yes','y','ye',''}

        try:
            choice = Prompt.ask(f"Do you want upgrade [bold yellow]{pkg}[/bold yellow] [Y/n]").lower()
        except KeyboardInterrupt:
            print("\n[bold bright_red]Upgrade cancelled.[/bold bright_red]")
            return

        if choice in yes:
            choice_pkg.append(pkg)
        else:
            pass    

    packages_to_upgrade = " ".join(choice_pkg)

    if choice_pkg != []:
        # Store packages in interrupted_upgrades before attempting upgrade
        for pkg in choice_pkg:
            cursor.execute("INSERT OR REPLACE INTO interrupted_upgrades (pkg_name) VALUES (?)", (pkg,))
        conn.commit()

        try:
            cmd = ["apt", "install", "-y"] + packages_to_upgrade.split()
            if os.geteuid() != 0:
                cmd.insert(0, "sudo")

            process = subprocess.run(cmd, check=True)

            # Only clear if the installation was successful
            if process.returncode == 0:
                cursor.execute("DELETE FROM interrupted_upgrades")
                conn.commit()

        except subprocess.CalledProcessError as e:
            print(f"\n[bold bright_red]Package installation failed with error code {e.returncode}[/bold bright_red]")
            conn.commit()  # Keep the interrupted packages in the database
        except KeyboardInterrupt:
            print("\n[bold bright_red]Upgrade interrupted. Will retry these packages next time.[/bold bright_red]")
            conn.commit()  # Make sure interrupted packages are saved


def upgrade_pkg_regex(pattern):
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
    choice = Prompt.ask(f"Do you want to upgrade all matching packages? [Y/n]").lower()

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
