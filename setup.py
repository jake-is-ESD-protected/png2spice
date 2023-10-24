from setuptools import setup, find_packages

setup(
    name='schematicLT',
    version='0.0.1',
    author='Konya, Tschavoll',
    author_email='your@email.com',
    description='Assortment of line tracing tools for analytic schematic recognition',
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    classifiers=[
        'Development Status :: not released yet',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    url='https://github.com/jake-is-ESD-protected/schematic-line-tracing',
    license='MIT',
    keywords='schematic, image recognition',
)
