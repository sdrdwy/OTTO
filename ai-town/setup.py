from setuptools import setup, find_packages

setup(
    name="ai-town",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain==0.1.16",
        "langchain-openai==0.0.8",
        "openai==1.12.0",
        "python-dotenv==1.0.0",
        "tiktoken==0.5.1"
    ],
    author="AI Town Developer",
    author_email="ai-town@example.com",
    description="A multi-agent simulation environment with memory and world modeling",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/ai-town",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
)