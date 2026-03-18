from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="healthcare-cpabe-system",
    version="1.0.0",
    author="Healthcare Security Team",
    author_email="security@healthcare.example.com",
    description="Secure Healthcare Data Access System using CP-ABE, AES-256, and SHA-3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/healthcare/cpabe-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pycryptodome>=3.19.0",
        "charm-crypto>=0.50",
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
        "sqlalchemy>=2.0.23",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.0",
        "click>=8.1.7",
        "colorama>=0.4.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.1",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "cpabe-setup=scripts.setup_system:main",
            "cpabe-user=scripts.create_user:main",
            "cpabe-encrypt=scripts.encrypt_file:main",
            "cpabe-decrypt=scripts.decrypt_file:main",
        ],
    },
)
