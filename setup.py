"""forgeUltra setuptools."""

from setuptools import find_packages, setup

setup(
    name="forge_ultra",
    version="0.1.0",
    description="Isaac Lab forge task scaffold with KUKA-SHARPA assets staged for adaptation.",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    package_data={
        "forge_ultra.tasks.forge.agents": ["*.yaml"],
        "forge_ultra.tasks.factory.agents": ["*.yaml"],
        "forge_ultra.tasks.simtoolreal_sharpa.agents": ["*.yaml"],
    },
    install_requires=[],
)
