from setuptools import setup, find_packages

setup(
    name="gouge",
    version=open('gouge/version.txt').read().strip(),
    packages=find_packages(),
    install_requires=[
        'blessings',
    ],
    include_package_data=True,
    author="Michel Albert",
    author_email="michel@albert.lu",
    description="Collection of logging formatters.",
    license="private",
    url="https://github.com/exhuma/gouge",
)
