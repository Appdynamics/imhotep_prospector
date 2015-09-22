from setuptools import setup, find_packages

setup(
    name='imhotep_prospector',
    version='0.0.2',
    packages=find_packages(),
    url='',
    license='MIT',
    author='',
    author_email=' ',
    description='An imhotep plugin for prospector validation',
    requires=['prospector'],
    entry_points={
        'imhotep_linters': [
            '.py = imhotep_prospector.plugin:Prospector'
        ],
    },
)
