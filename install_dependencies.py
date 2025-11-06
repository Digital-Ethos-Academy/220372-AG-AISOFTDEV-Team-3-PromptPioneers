"""
Dependency Installation Utility

This module provides automatic installation of required packages for the
LangGraph agent functionality. It checks if packages are available and
installs them if missing.
"""

import sys
import importlib
import subprocess


def install_if_missing(package: str) -> None:
    """
    Check if a package is installed and install it if missing.
    
    Args:
        package: Name of the package to check/install.
    """
    try:
        importlib.import_module(package)
        print(f"✓ {package} is already installed")
    except ImportError:
        print(f"⚠ {package} not found, installing...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", package]
            )
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")
            raise


def install_langgraph_dependencies() -> None:
    """
    Install all required dependencies for LangGraph agent functionality.
    
    Packages installed:
    - langgraph: Graph-based agent framework
    - langchain: Core LangChain library
    - langchain_community: Community integrations
    - langchain_openai: OpenAI integration
    - faiss-cpu: Vector similarity search
    - pypdf: PDF text extraction
    """
    packages = [
        'langgraph',
        'langchain',
        'langchain_community',
        'langchain_openai',
        'faiss-cpu',
        'pypdf'
    ]
    
    print("=" * 60)
    print("Installing LangGraph Dependencies")
    print("=" * 60)
    
    for package in packages:
        install_if_missing(package)
    
    print("=" * 60)
    print("✓ All dependencies installed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    """Run dependency installation when executed directly."""
    try:
        install_langgraph_dependencies()
    except Exception as e:
        print(f"\n✗ Installation failed: {e}")
        sys.exit(1)
