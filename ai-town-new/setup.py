from setuptools import setup, find_packages

setup(
    name="ai-town-new",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "langchain==0.1.16",
        "langchain-openai==0.0.8",
        "openai==1.12.0",
        "python-dotenv==1.0.0",
        "tiktoken>=0.5.2",
        "dashscope",
        "langchain-community==0.0.38"
    ],
    author="AI Town Development Team",
    description="A multi-agent simulation environment with students, teachers, and interactive world",
    python_requires=">=3.8",
)