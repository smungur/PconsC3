from __future__ import division
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

extension = Extension(
    name="_predict_parallel",
    sources=["_predict_parallel.pyx"],
    include_dirs=[numpy.get_include()],
    extra_compile_args='-O2 -march=native -pipe -g0 -fopenmp'.split(),
    extra_link_args='-O2 -march=native -pipe -g0 -fopenmp'.split()
)

setup(
    name='_predict_parallel',
    ext_modules=cythonize(extension)
)

