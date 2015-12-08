from setuptools import setup

setup(name='FlaskApp',
      version='1.0',
      description='PTL Schedule Flask app',
      author='Alex Maksimov',
      author_email='frohenk@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
     install_requires=['Flask>=0.10.1', 'mysql-connector-python'],
     )
