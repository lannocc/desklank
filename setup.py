import setuptools


def run():
    setuptools.setup(
        name='desklank',
        version = findversion('.', 'desklank'),
        author='LANNOCC (Shawn A. Wilson)',
        author_email='lannocc@yahoo.com',
        url='https://github.com/lannocc/desklank',
        packages=setuptools.find_packages(),
        description='Text-mode peer-to-peer encrypted communication utilizing' \
            + ' LANK protocol and DeskApp framework',
        long_description_content_type='text/markdown',
        long_description=open('README.md').read(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        install_requires=[
            'appdirs',
            'deskapp >= 0.0.4',
            'lank >= 0.4.7',
            'pillow',
            'pystray',
            'requests',
        ],
        entry_points = {
            'console_scripts': [
                'desklank=desklank.__main__:run',
            ],
        },
        include_package_data=True,
        #data_files = [
        #    ('share/applications', ['com.lannocc.desklank.desktop']),
        #],
    )


def findversion(root, name):
    '''versioning strategy taken from
       http://stackoverflow.com/a/7071358/7203060'''

    import re
    from os.path import join

    vfile = join(root, name, "__version__.py")
    vmatch = re.search(r'^__version__ *= *["\']([^"\']*)["\']',
        open(vfile, "rt").read(), re.M)

    if vmatch:
        version = vmatch.group(1)
        print ("Found %s version %s" % (name, version))
        return version

    else:
        raise RuntimeError("Expecting a version string in %s." % (vfile))


if __name__ == '__main__':
    run()

