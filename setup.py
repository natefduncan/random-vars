from setuptools import setup, find_packages

def get_reqs():
    with open('requirements.txt', "r") as f:
        return f.readlines()

setup(
    name='rv',
    version='0.1.0',
    py_modules=find_packages(), 
    install_requires=get_reqs(), 
    entry_points={
        'console_scripts': [
            'rv = rv.main:cli',
        ],
    },
)


