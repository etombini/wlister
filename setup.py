from distutils.core import setup

setup(
    name='wlister',
    version='0.1.0',
    author='Elvis Tombini',
    author_email='elvis@mapom.me',
    packages=['wlister'],
    url='https://github.com/etombini/wlister',
    license='LICENSE.txt',
    description='Web application firewall designed to whitelist and/or blacklist HTTP requests.',
    long_description=open('readme.md').read(),
    install_requires=["jsonschema >= 2.3.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP",
    ]
)
