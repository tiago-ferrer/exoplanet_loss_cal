from setuptools import setup, find_packages

setup(
    name="exoplanet_loss",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "pandas>=1.3.0",
        "requests>=2.25.0",
        "flask>=2.0.0",
    ],
    author="Tiago",
    author_email="tiago@example.com",
    description="A package for exoplanet mass loss calculations",
    keywords="exoplanet, astronomy, astrophysics",
    url="https://github.com/yourusername/exoplanet_loss",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
    python_requires=">=3.8",
)
