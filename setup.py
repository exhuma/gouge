from setuptools import setup, find_packages

dependencies = [
    'blessings'
]

setup(
    name="gouge",
    version=open('gouge/version.txt').read().strip(),
    packages=find_packages(),
    install_requires=dependencies,
    requires=dependencies,
    provides=['gouge'],
    include_package_data=True,
    author="Michel Albert",
    author_email="michel@albert.lu",
    description="Collection of logging formatters.",
    license="BSD",
    url="https://github.com/exhuma/gouge",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Logging',
    ],
)
