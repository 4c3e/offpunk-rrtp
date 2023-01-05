from setuptools import setup

setup(
    name='offpunk',
    version='1.8',
    description="Offline-First Gemini/Web/Gopher/RSS reader and browser",
    author="Ploum",
    author_email="offpunk@ploum.eu",
    url='https://sr.ht/~lioploum/offpunk/',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'Development Status :: 4 - Beta',
    ],
    py_modules = ["offpunk"],
    entry_points={
        "console_scripts": ["offpunk=offpunk:main"]
    },
    install_requires=[],
)
