from setuptools import setup

setup(
    name='stately',
    version='0.0.1',
    packages=[
        'src/stately'
    ],
    install_requires=[
        'django==1.10.1',
        'django-jsonfield==1.0.1',
        'django-cors-middleware==1.3.1',
        'pyyaml==3.12'
    ],
    extras_require={
        'dev': ['bpython']
    }
)
