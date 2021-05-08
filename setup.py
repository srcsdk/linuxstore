from setuptools import setup

setup(
    name="linuxstore",
    version="1.0.0",
    author="srcsdk",
    author_email="srcsdk@users.noreply.github.com",
    description="gui package manager for linux",
    url="https://github.com/srcsdk/linuxstore",
    py_modules=["store", "layout", "detect_os"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "linuxstore=store:main",
        ],
    },
)
