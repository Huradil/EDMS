from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("project/users/cython_generate_keys.pyx",
                          language_level=3)
)




# setup.py:
#
# from setuptools import setup
# from Cython.Build import cythonize
#
# setup(
#     ext_modules=cythonize("crypto_utils.pyx", language_level=3)
# )
#
#
# command:
# python setup.py build_ext --inplace
