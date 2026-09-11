"""Include canonical schemas and policy in wheels without a second source copy."""
from pathlib import Path
import shutil
from setuptools import setup
from setuptools.command.build_py import build_py


class BuildWithContracts(build_py):
    def run(self):
        super().run()
        for name in ("schemas", "policy"):
            source = Path(__file__).parent / name
            destination = Path(self.build_lib) / "cost_router" / "data" / name
            shutil.copytree(source, destination, dirs_exist_ok=True)


setup(cmdclass={"build_py":BuildWithContracts})
