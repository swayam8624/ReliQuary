# vaults/storage/s3.py
from vaults.storage.base import StorageInterface

class S3Storage(StorageInterface):
    """
    Placeholder for an AWS S3 storage backend.
    
    This implementation will use the 'boto3' library to interact with S3.
    """
    def __init__(self, bucket_name: str, region_name: str):
        self.bucket_name = bucket_name
        self.region_name = region_name
        # TODO: Implement initialization with boto3 client
        pass

    def save_vault(self, vault_id: str, data: bytes):
        # TODO: Implement saving data to S3 using put_object
        pass

    def load_vault(self, vault_id: str) -> bytes:
        # TODO: Implement loading data from S3 using get_object
        pass

    def delete_vault(self, vault_id: str):
        # TODO: Implement deleting data from S3 using delete_object
        pass