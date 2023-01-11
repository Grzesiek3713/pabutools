from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent

setup(name='pabutools',
      version='0.7',
      description='Implementation of PB voting rules and tools for reading Pabulib datasets',
      long_description=(this_directory / "README.md").read_text(),
      long_description_content_type='text/markdown',
      readme = "README.md",
      packages=['pabutools'],
      author_email='g.pierczynski@gmail.com',
      zip_safe=False)
