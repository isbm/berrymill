from setuptools import setup, find_packages

setup(name='Berrymill',
      version='0.1',
      description='Kiwi-based Appliance Builder',
      author='Bo Maryniuk',
      author_email='bo@maryniuk.net',
      url='https://github.com/isbm/berrymill',
      packages=find_packages(
          where="src"
          ),
      package_dir={"": "src"},
      #packages=['src/berry_mill', 'src/berry_mill/imgdescr'],
      zip_safe=False,
     )
