import importlib.metadata
import sys

def get_package_versions():
    packages = [
        "langchain",
        "langchain-community",
        "PyPDF2",
        "pdfplumber",
        "pymupdf",
        "sentence-transformers",
        "chromadb",
        "faiss-cpu",
        "streamlit",
        "python-dotenv",
        "pyyaml",
        "pandas",
        "pydantic",
        "langchain-openai"
    ]
    
    versions = {}
    versions["python"] = sys.version.split()[0]
    
    for package in packages:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "Not installed"
            
    return versions

def print_versions():
    print("Package Versions:")
    print("-" * 30)
    versions = get_package_versions()
    for pkg, ver in versions.items():
        print(f"{pkg}: {ver}")

if __name__ == "__main__":
    print_versions()
