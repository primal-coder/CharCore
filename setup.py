from setuptools import setup, find_packages

setup(
    name='CharCore',
    version='0.0.1',
    author='James Evans',
    author_email='joesaysahoy@gmail.com',
    description='A game engine.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/primal-coder/CharCore',
    packages=find_packages(),
    install_requires=[
        'pyglet',
        'pymunk',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    keywords='game engine'
)