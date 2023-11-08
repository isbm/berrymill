from setuptools import setup, find_packages

setup(name='Berrymill',
      version='0.1',
      description='Appliance builder',
      author='Bo Maryniuk',
      author_email='bo@maryniuk.net',
      url='https://github.com/isbm/berrymill',
      packages=find_packages(
          where='src',
          include=['berry_mill', 'berry_mill.imgdescr']
      ),
      zip_safe=False,
     )
