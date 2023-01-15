from setuptools import setup, find_packages


class ProjectSetup:
    """Wraps project's settings as a package."""

    NAME = 'tracker'
    LICENSE = 'MIT'
    REQUIRES_PYTHON = '>=3.8'

    @classmethod
    def init_setup(cls) -> None:
        """Run setup."""
        setup(
            license=cls.LICENSE,
            packages=find_packages(),
            python_requires=cls.REQUIRES_PYTHON,
            install_requires=(
                *cls.get_requirements(),
            ),
        )

    @staticmethod
    def get_requirements() -> list:
        """List only core libs to run the project."""
        with open('requirements/core.txt') as dependencies:
            requirements = dependencies.read().splitlines()
        return requirements[:-1]


ProjectSetup.init_setup()
