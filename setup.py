from setuptools import setup

setup(
    name="idle-shutdown-monitor",
    version="1.0.0",
    description="AI cluster idle monitoring with REST API",
    packages=[],
    install_requires=[
        "psutil",
        "pynvml",
        "requests",
        "fastapi",
        "uvicorn[standard]",
    ],
)
