from setuptools import setup, find_packages

setup(
    name="talentproof",
    version="1.0.0",
    description="Sovereign 2-Way Developer Proof & Recruiter Milestone Escrow Kernel",
    author="Aamir Zameer [Az.]",
    author_email="aamirmalikzameer@gmail.com",
    url="https://github.com/Amz34/talentproof-protocol",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "talentproof=talentproof.cli.main:main",
        ],
    },
)
