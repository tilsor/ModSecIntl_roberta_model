import os
from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)
setup(
   name='server-roberta',
   version='0.4.2',
   description='To classify, BPE, ROBERTA and SVM are used',
   long_description_content_type="text/markdown",
   long_description="README",
   author='Tilsor',
   author_email='tilsor@tilsor.com.uy',
   setup_requires='setuptools',
   entry_points={
        'console_scripts': ['server-roberta=serverRoberta.server:main']},
   packages=['serverRoberta'],
   data_files=[('serverRoberta', ['serverRoberta/config.ini'])],
   py_modules=['serverRoberta.roberta_pb2', 'serverRoberta.roberta_pb2_grpc'],
   include_package_data=True,
   install_requires=['fairseq==0.10.0', 'scipy==1.5.0', 'scikit-learn==0.23.1','numpy==1.23.5','pandas==1.3.4','pyparsing==3.0.6','torch==1.10.0','tqdm==4.62.3','wget==3.2','grpcio-tools==1.29.0','requests'],
)
