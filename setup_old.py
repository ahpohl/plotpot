from setuptools import setup, find_packages
import os, subprocess

version_py = os.path.join(os.path.dirname(__file__), 'plotpot/version.py')

try:
    version_git = subprocess.check_output(["git", "describe", "--always", "--dirty"]).rstrip().decode('utf-8')
except:
    with open(version_py, 'r') as fh:
        version_git = fh.read().strip().split('=')[-1].replace('"','')
        fh.close()

version_msg = "# Do not edit this file, pipeline versioning is governed by git tags"
line = version_msg + os.linesep + "__version__=\"" + version_git +'\"'

with open(version_py, 'w') as fh:
    fh.write(line)
    fh.close()

setup(
    name='plotpot',
    version="".format(ver=version_git),
    description='A python module for plotting potentiostat data',
    author='Alexander Pohl',
    author_email='alex@ahpohl.com',
    url='https://github.com/ahpohl/plotpot.git',
    license='MIT',
    packages=find_packages(),
)