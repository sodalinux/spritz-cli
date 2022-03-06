from typing import List
from multiprocessing import Process
import typer
import os
import requests
import shutil
import glob

app = typer.Typer()

CACHE_DIR=f"{os.path.expanduser('~')}/.cache/spritz"

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def check_url(url: str):
    response = requests.get(url)

    if response.status_code != 200:
        return False
    
    return True

def runInParallel(*fns):
    proc = []
    for fn in fns:
        p = Process(target=fn)
        p.start()
        proc.append(p)
    for p in proc:
        p.join()

def download_pkgbuild(package: str):
    base_url = f"https://aur.archlinux.org/{package}.git"
    os.system(f"git clone -q --depth 1 {base_url} {CACHE_DIR}/{package}")
    os.system(f"(cd {CACHE_DIR}/{package} && makepkg -si)")
    

def save_pkgbuild(package: str, path: str):
    base_url = f"https://aur.archlinux.org/{package}.git"
    os.system(f"git clone -q --depth 1 {base_url} {CACHE_DIR}/{package}")
    os.system(f"(cd {CACHE_DIR}/{package} && makepkg -sf)")
    pkg = glob.glob(f"{CACHE_DIR}/{package}/*.pkg.tar.zst")[0]
    dst = shutil.copy(pkg, path)
    typer.echo(f"{color.BOLD}{color.GREEN}==>{color.END}{color.BOLD} Package has been successfully saved to {dst}")


@app.command()
def install(packages: List[str]):
    """Install packages from the AUR onto your system."""

    pkg_queue = []
    if not os.path.isdir(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    typer.echo(f"{color.BOLD}{color.GREEN}==>{color.END}{color.BOLD} Verifying packages...")
    for package in packages:
        base_url = f"https://aur.archlinux.org/packages/{package}"
        if not check_url(base_url):
            return typer.echo(f"'{package}' is not a valid package. Please try again.")

        if os.path.isdir(f"{CACHE_DIR}/{package}"):
            shutil.rmtree(f"{CACHE_DIR}/{package}", ignore_errors=True)
        typer.echo(f"{color.BOLD}{color.GREEN}==>{color.END}{color.BOLD} Downloading PKGBUILD for {package}")

    for package in packages:
        download_pkgbuild(package)
    


@app.command()
def remove(packages: str):
    """Remove a package installed from the AUR from your system."""
    os.system(f"sudo pacman -Rs {packages}")

@app.command()
def search(packages: str):
    """Search for a package on the AUR."""
    typer.echo(f"{packages}")

@app.command()
def save(path: str, packages: List[str]):
    """Like the install command, but saves the package to a specfied folder."""
    pkg_queue = []
    if not os.path.isdir(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    if not os.path.isdir(path):
        return typer.echo(
            f"{color.BOLD}{color.RED}ERROR:{color.END}{color.BOLD}" 
            " Path does not exist. Please enter a valid path."
            )

    if not os.access(path, os.W_OK):
        return typer.echo(
            f"{color.BOLD}{color.RED}ERROR:{color.END}{color.BOLD}"
            " You do not have permission to write to the path you specified."
            )

    typer.echo(f"{color.BOLD}{color.GREEN}==>{color.END}{color.BOLD} Verifying packages...")
    for package in packages:
        base_url = f"https://aur.archlinux.org/packages/{package}"
        if not check_url(base_url):
            return typer.echo(f"'{package}' is not a valid package. Please try again.")

        if os.path.isdir(f"{CACHE_DIR}/{package}"):
            shutil.rmtree(f"{CACHE_DIR}/{package}", ignore_errors=True)
        typer.echo(f"{color.BOLD}{color.GREEN}==>{color.END}{color.BOLD} Downloading PKGBUILD for {package}")

    for package in packages:
        save_pkgbuild(package, path)

@app.command()
def update(packages: str):
    """Updates your system and also updates any AUR packages you have installed."""
    print("Updating...")


if __name__ == "__main__":
    app()