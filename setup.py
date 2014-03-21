from setuptools import setup

setup(
    name='opml-checker',
    version='0.0.1',
    author='yhchan',
    author_email='yihuan.chan@gmail.com',
    packages=['opml_checker'],
    url='https://github.com/yhchan/opml-checker',
    license='MIT',
    description='OPML URL checker',
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': [
            'opml-checker = opml_checker.opml_checker:main',
        ]
    },
    install_requires=[
        "lxml",
        "requests",
        "gevent",
        "more-itertools",
    ],
    zip_safe=False
)
