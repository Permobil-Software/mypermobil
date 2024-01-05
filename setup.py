import setuptools

setuptools.setup(
    name="mypermobil",
    version="0.1.8",
    description="A Python wrapper for the MyPermobil API",
    url="https://github.com/IsakNyberg/MyPermobil-API",
    author="Isak Nyberg",
    author_email="isak@nyberg.dev",
    license="MIT",
    packages=["mypermobil"],
    install_requires=["aiohttp", "aiocache"],
    test_requires=["pytest", "aiounittest", "aiocache"],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
