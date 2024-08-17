from setuptools import setup, find_packages

setup(
    name='qrows',
    version='1.0',
    packages=find_packages(),
    install_requires=['qiskit'],
    entry_points={
        'qiskit.providers': [
            'qrows_backend = qrows.backend:QrowsBackend'
        ]
    }
)
