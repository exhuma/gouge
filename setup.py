from setuptools import setup, find_packages

dependencies = [
    'blessings'
]

setup(
    name="chisel",
    version=open('chisel/version.txt').read().strip(),
    packages=find_packages(),
    install_requires=dependencies,
    requires=dependencies,
    provides=['chisel'],
    obsoletes=['gouge'],
    include_package_data=True,
    author="Michel Albert",
    author_email="michel@albert.lu",
    description="Collection of logging formatters.",
    license="BSD",
    url="https://github.com/exhuma/chisel",
    classifiers=[
        'Development Status :: 3 - Alpha',
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
