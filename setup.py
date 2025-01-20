from setuptools import find_packages, setup

__version__ = '1.0.0'
package_name = 'spector'

setup(
    name=package_name,
    version=__version__,
    author="Spector3702",
    packages=find_packages(),
    entry_points={'console_scripts': [
        'run-server = spector.app.main:main',
    ]},
    include_package_data=True,
    package_data={
        # If any package contains *.<ext>, include them:
        '': ['*.md', '*.yaml', '*.json'],
    },

    install_requires=[
        'chromadb',
        'fastapi',
        'langchain',
        'langchain-community',
        'langchain-openai',
        'langgraph',
        'langgraph-checkpoint-postgres',
        'pydantic',
        'pypdf',
        'uvicorn',
        'prometheus-client'
    ]
)
