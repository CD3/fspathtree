from distutils.core import setup
setup(
  name = 'fspathtree',
  packages = ['fspathtree'],
  version = '0.0',
  license='MIT',
  description = 'A small utility for wrapping trees (nested dict/list) that allows filesystem-like path access, including walking up with "../".',
  author = 'CD Clark III',
  author_email = 'clifton.clark@gmail.com',
  url = 'https://github.com/CD3/fspathtree',
  keywords = ['dict', 'tree', 'filesystem path'],
  install_requires=[],
  classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
  ],
  python_requires='>=3.4',
)
