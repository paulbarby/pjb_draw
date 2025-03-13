from setuptools import setup, find_packages

setup(
    name="drawing_app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pillow",
    ],
    entry_points={
        'console_scripts': [
            'drawing_app=src.main:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A Windows-based drawing application",
)
