from setuptools import setup

setup(name='nerva2py', version='1.0',
      description='Nervatura OpenShift Python-2.7 Community Cartridge based application',
      author='Csaba Kappel', author_email='csaba.kappel@nervatura.com',
      url='http://www.python.org/sigs/distutils-sig/',

      #  Uncomment one or more lines below in the install_requires section
      #  for the specific client drivers/modules your application needs.
      install_requires=['greenlet', 'gevent',
                          'MySQL-python',
                        #  'pymongo',
                          'psycopg2',
      ],
     )
