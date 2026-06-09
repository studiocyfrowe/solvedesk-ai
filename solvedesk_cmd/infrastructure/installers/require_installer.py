import subprocess
import sys
import importlib
from pathlib import Path
from dotenv import load_dotenv
import os

import typer

class RequireInstaller():
    def __init__(self):
        self.require_file = os.getenv('REQUIRE_FILE')

    def load_requirements(self) -> list[str]:
        path = Path(self.require_file)

        if not path.exists():
            return []

        packages = []

        for line in path.read_text(
            encoding="utf-8"
        ).splitlines():

            line = line.strip()
            if not line or line.startswith("#"):
                continue

            package_name = (
                line
                .split("==")[0]
                .split(">=")[0]
                .split("<=")[0]
                .strip()
            )

            packages.append(package_name)

        return packages


    def get_missing_packages(
        packages: list[str]
    ) -> list[str]:

        missing = []

        for package in packages:

            normalized_name = (
                package
                .replace("-", "_")
            )

            try:
                importlib.import_module(
                    normalized_name
                )

            except ImportError:
                missing.append(package)

        return missing


    def install_requirements(self) -> bool:
        packages = self.load_requirements(self.requirements_file)

        if not packages:

            typer.echo(
                "requirements.txt not found or empty"
            )

            return False

        missing_packages = self.get_missing_packages(packages)
        if not missing_packages:
            typer.echo("All requirements already installed\n")
            return True

        typer.echo(
            "\nMissing packages:\n"
        )

        for package in missing_packages:
            typer.echo(f"- {package}")

        typer.echo(
            "\nInstalling missing packages...\n"
        )

        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    *missing_packages
                ],
                check=True,
                text=True
            )

        except subprocess.CalledProcessError:
            typer.echo(
                "\nInstallation failed\n"
            )
            return False

        still_missing = self.get_missing_packages(
            packages
        )

        if still_missing:
            typer.echo(
                "\nSome packages are still missing:\n"
            )

            for package in still_missing:
                typer.echo(f"- {package}")

            return False

        typer.echo(
            "\nDependencies installed successfully\n"
        )

        return True