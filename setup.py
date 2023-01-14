from setuptools import setup

with open('requirements/core.txt') as req:
    req = req.read().splitlines()

setup(
    python_requires='>=3.8',
    install_requires=(
        *req,
    ),
)
