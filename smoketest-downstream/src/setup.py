from setuptools import Extension, setup

setup(ext_modules=[Extension("smoke", ["smoke.c"])])
