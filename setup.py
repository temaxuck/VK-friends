from setuptools import setup, find_packages

setup(
    name="vkfriends",
    version="0.0.1",
    packages=find_packages(),
    install_requires=["requests", "click"],
    entry_points="""
    [console_scripts]
    vkfriends=cli:run
    """,
)
