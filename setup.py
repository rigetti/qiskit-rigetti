# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = ""

setup(
    long_description=readme,
    name="qiskit-rigetti-provider",
    version="0.3.0",
    description="Provider for running Qiskit circuits on Rigetti QPUs and simulators.",
    python_requires="==3.*,>=3.7.0",
    author="Rigetti Computing",
    packages=["qiskit_rigetti", "qiskit_rigetti.gates", "qiskit_rigetti.hooks"],
    package_dir={"": "."},
    package_data={"qiskit_rigetti": ["*.typed"]},
    install_requires=[
        'importlib-metadata; python_version < "3.8"',
        "numpy==1.*,>=1.20.1",
        "pyquil==3.*,>=3.0.0",
        "qiskit==0.*,>=0.27.0",
    ],
    extras_require={
        "dev": [
            "black==20.*,>=20.8.0.b1",
            "flake8==3.*,>=3.8.1",
            "mypy==0.*,>=0.800.0",
            "pytest==6.*,>=6.2.2",
            "pytest-cov==2.*,>=2.11.1",
            "pytest-httpx==0.*,>=0.9.0",
            "pytest-mock==3.*,>=3.6.1",
        ],
        "docs": [
            "furo==2021.*,>=2021.7.5.b38",
            "myst-parser==0.*,>=0.15.1",
            "sphinx==4.*,>=4.1.1",
            "sphinx-autoapi==1.*,>=1.8.1",
            "sphinx-autobuild==2021.*,>=2021.3.14",
        ],
    },
)
