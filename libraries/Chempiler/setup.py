from setuptools import setup, find_packages

setup(name="chempiler",
      version="2.0.5",
      description="Chempiler",
      url="http://datalore.chem.gla.ac.uk/Chemputer/Chempiler",
      author="Chempiler contributors",
      license="MIT",
      packages=find_packages(),
      install_requires=[
          "pyserial>=3.3",
          "opencv-python>=3.1",
          "networkx>=2.2",
          "numpy>=1.15",
      ],
      zip_safe=False)
