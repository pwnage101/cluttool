from setuptools import setup
setup(
    name="cluttool",
    version="wip", # i.e. this version doesn't even work yet.
    packages=find_packages(),
    entry_points={
        'gui_scripts': [
            'cluttool = cluttool:cli',
        ]
    },
    install_requires=['click>=6.7<8.0'],
    author="Troy Sankey",
    author_email="sankeytms@gmail.com",
    description="create and convert 3D/color LUTs",
    license="GPLv3",
    keywords="lut hald clut 3dl 3d color",
    classifiers=[
        (
            'License :: OSI Approved'
            ':: GNU General Public License v3 or later (GPLv3+)'),
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
