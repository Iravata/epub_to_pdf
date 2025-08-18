from setuptools import setup, find_packages

setup(
    name="epub-to-pdf",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "epub-to-pdf=src.cli:main",
        ],
    },
    install_requires=[
        "click>=8.0.0",
        "reportlab>=3.6.0",
        "ebooklib>=0.18",
        "beautifulsoup4>=4.10.0",
        "Pillow>=8.3.0",
        "PyPDF2>=3.0.0",
        "lxml>=4.6.0",
        "cssutils>=2.0.0",
        "psutil>=5.8.0",
        "pathlib2>=2.3.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "pytest-mock>=3.6.0"
        ]
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Convert EPUB files to PDF with advanced features and robust error handling",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/epub_to_pdf",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/epub_to_pdf/issues",
        "Documentation": "https://github.com/yourusername/epub_to_pdf/blob/main/API_DOCUMENTATION.md",
        "Source Code": "https://github.com/yourusername/epub_to_pdf",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing :: Markup",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="epub pdf convert ebook cli click",
    license="MIT",
)