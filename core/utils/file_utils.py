"""
File utility functions for ReliQuary platform.
Provides functions for secure file operations, path handling, and file management.
"""

import os
import hashlib
import json
import shutil
from typing import Union, Optional, Dict, Any
from pathlib import Path


def secure_delete_file(file_path: Union[str, Path]) -> bool:
    """
    Securely delete a file by overwriting it with random data before deletion.
    
    Args:
        file_path (Union[str, Path]): Path to the file to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return True
            
        # Get file size
        file_size = path.stat().st_size
        
        # Overwrite file with random data
        with open(path, "r+b") as file:
            file.write(os.urandom(file_size))
            file.flush()
            os.fsync(file.fileno())
        
        # Delete the file
        path.unlink()
        return True
    except Exception:
        return False


def calculate_file_hash(file_path: Union[str, Path], algorithm: str = "sha256") -> str:
    """
    Calculate the hash of a file using the specified algorithm.
    
    Args:
        file_path (Union[str, Path]): Path to the file
        algorithm (str): Hash algorithm to use (default: sha256)
        
    Returns:
        str: Hexadecimal representation of the file hash
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the algorithm is not supported
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    hash_obj = hashlib.new(algorithm)
    
    with open(path, "rb") as file:
        # Read file in chunks to handle large files
        for chunk in iter(lambda: file.read(8192), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def safe_write_file(file_path: Union[str, Path], content: Union[str, bytes], 
                   encoding: str = "utf-8", backup: bool = True) -> bool:
    """
    Safely write content to a file with optional backup of existing file.
    
    Args:
        file_path (Union[str, Path]): Path to the file to write
        content (Union[str, bytes]): Content to write to the file
        encoding (str): Encoding to use for string content (default: utf-8)
        backup (bool): Whether to create a backup of existing file (default: True)
        
    Returns:
        bool: True if write was successful, False otherwise
    """
    path = Path(file_path)
    
    try:
        # Create backup if requested and file exists
        if backup and path.exists():
            backup_path = path.with_suffix(path.suffix + ".backup")
            shutil.copy2(path, backup_path)
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content to file
        if isinstance(content, str):
            with open(path, "w", encoding=encoding) as file:
                file.write(content)
        else:
            with open(path, "wb") as file:
                file.write(content)
        
        return True
    except Exception:
        return False


def safe_read_file(file_path: Union[str, Path], encoding: str = "utf-8") -> Optional[Union[str, bytes]]:
    """
    Safely read content from a file.
    
    Args:
        file_path (Union[str, Path]): Path to the file to read
        encoding (str): Encoding to use for reading text files (default: utf-8)
        
    Returns:
        Optional[Union[str, bytes]]: File content or None if reading failed
    """
    path = Path(file_path)
    
    try:
        if not path.exists():
            return None
            
        # Try to read as text first
        try:
            with open(path, "r", encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            # If that fails, read as binary
            with open(path, "rb") as file:
                return file.read()
    except Exception:
        return None


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get detailed information about a file.
    
    Args:
        file_path (Union[str, Path]): Path to the file
        
    Returns:
        Dict[str, Any]: Dictionary containing file information
    """
    path = Path(file_path)
    
    if not path.exists():
        return {"exists": False}
    
    stat = path.stat()
    
    return {
        "exists": True,
        "size": stat.st_size,
        "created": stat.st_ctime,
        "modified": stat.st_mtime,
        "accessed": stat.st_atime,
        "is_file": path.is_file(),
        "is_directory": path.is_dir(),
        "permissions": oct(stat.st_mode)[-3:],
        "hash": calculate_file_hash(path) if path.is_file() else None
    }


def ensure_directory_exists(directory_path: Union[str, Path]) -> bool:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path (Union[str, Path]): Path to the directory
        
    Returns:
        bool: True if directory exists or was created successfully, False otherwise
    """
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def clean_directory(directory_path: Union[str, Path], 
                   preserve_extensions: Optional[list] = None) -> int:
    """
    Remove all files from a directory, optionally preserving files with certain extensions.
    
    Args:
        directory_path (Union[str, Path]): Path to the directory to clean
        preserve_extensions (Optional[list]): List of file extensions to preserve (e.g., ['.txt', '.json'])
        
    Returns:
        int: Number of files deleted
    """
    path = Path(directory_path)
    if not path.is_dir():
        return 0
    
    deleted_count = 0
    
    for item in path.iterdir():
        if item.is_file():
            # Check if we should preserve this file
            if preserve_extensions:
                if item.suffix.lower() in [ext.lower() for ext in preserve_extensions]:
                    continue
            
            # Delete the file
            try:
                item.unlink()
                deleted_count += 1
            except Exception:
                pass
        elif item.is_dir():
            # Recursively clean subdirectories
            deleted_count += clean_directory(item, preserve_extensions)
            
            # Remove empty directory
            try:
                item.rmdir()
            except Exception:
                pass
    
    return deleted_count


# Example usage
if __name__ == "__main__":
    # Example of calculating file hash
    import tempfile
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("This is a test file for ReliQuary")
        temp_file_path = temp_file.name
    
    try:
        # Calculate hash
        file_hash = calculate_file_hash(temp_file_path)
        print(f"File hash: {file_hash}")
        
        # Get file info
        info = get_file_info(temp_file_path)
        print(f"File info: {info}")
        
        # Test safe read/write
        safe_write_file(f"{temp_file_path}.copy", "Copied content")
        content = safe_read_file(f"{temp_file_path}.copy")
        print(f"Read content: {content}")
        
    finally:
        # Clean up
        os.unlink(temp_file_path)
        if os.path.exists(f"{temp_file_path}.copy"):
            os.unlink(f"{temp_file_path}.copy")