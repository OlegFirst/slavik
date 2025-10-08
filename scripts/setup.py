from setuptools import setup, find_packages

setup(
    name="bcm-ai-platform",
    version="1.0.0",
    packages=find_packages(include=['shared', 'shared.*', 'intelligent_core', 'intelligent_core.*']),
    package_dir={
        'intelligent_core': 'intelligent-core',
    },
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
        "prometheus-client>=0.19.0",
    ],
)
