# Moving most of the s3 funtionality here, as a module, reduces the monolithic nature of the webotron.py script,
# allows the functions to be called elsewhere so long as module is included
# and also removes the if __name__ == "__main__": problem wherein this wont be satisfied if
# the package is run as a module from elsewhere
"""Classes for s3 buckets"""
import mimetypes
from pathlib import Path
import functools

import boto3
from botocore.exceptions import ClientError

from hashlib import md5
from webotron import util


class BucketManager:
    """Manage an s3 bucket"""

    # aws breaks large files into chunks of this size, thus comparing hash can break down as large files will be broken into multiple chunks with given etags
    CHUNK_SIZE = 8388608

    # init function that initialises the instance with the relevant data
    def __init__(self, session):
        """Create a BucketManager object."""
        # initialise the s3 resource so it can be called by the bucket manager in webotron
        self.session = session
        self.s3 = self.session.resource("s3")
        # we can use this transfer config to specify how we upload files
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_chunksize=self.CHUNK_SIZE, multipart_threshold=self.CHUNK_SIZE
        )

        self.manifest = {}

    def get_region_name(self, bucket):
        """Get buckets region name"""
        bucket_location = self.s3.meta.client.get_bucket_location(Bucket=bucket.name)
        # location object is set for all locations except us-east-1 where it is null
        return bucket_location["LocationConstraint"] or "us-east-1"

    def get_bucket_url(self, bucket):
        """Get website URL for this bucket."""
        return "http://{}.{}".format(
            bucket.name, util.get_endpoint(self.get_region_name(bucket)).host
        )

    # Having this and the fn below allows the webotron script to talk to the bucket manager, not the s3 resource. This keeps things compartmentalised.
    def all_buckets(self):
        """Get an iterator of all buckets"""
        return self.s3.buckets.all()

    def all_objects(self, bucket_name):
        """Get an iterator of all objects in a bucket"""
        return self.s3.Bucket(bucket_name).objects.all()

    def init_bucket(self, bucket_name):
        """Initialise a new bucket, or get it if its already created"""
        bucket = None
        try:
            bucket = self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": self.session.region_name
                },
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
                bucket = self.s3.Bucket(bucket_name)
            else:
                raise e

        return bucket

    def set_policy(self, bucket):
        # if we wanted more flexibility we could set some args in the policy which people could choose themselves
        """Set bucket policy to be readable by everyone"""
        policy = (
            """
        {
            "Version":"2012-10-17",
            "Statement":[{
            "Sid":"PublicReadGetObject",
            "Effect":"Allow",
            "Principal": "*",
                "Action":["s3:GetObject"],
                "Resource":["arn:aws:s3:::%s/*"]
                }
            ]
        }
        """
            % bucket.name
        )
        policy = policy.strip()

        pol = bucket.Policy()
        pol.put(Policy=policy)

    def configure_website(self, bucket):
        """Configure the bucket to run as a website"""
        bucket.Website().put(
            WebsiteConfiguration={
                "ErrorDocument": {"Key": "error.html"},
                "IndexDocument": {"Suffix": "index.html"},
            }
        )

    def load_manifest(self, bucket):
        """Load and fill a manifest with the Key/Etag for caching"""
        # allows us to compare the etag(hash) of uploaded files against local files and only upload the cahnged ones during sync
        paginator = self.s3.meta.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket.name):
            for obj in page.get("Contents", []):
                self.manifest[obj["Key"]] = obj["ETag"]

    @staticmethod
    def hash_data(data):
        """Generate md5 hash for the data"""
        hash = md5()
        hash.update(data)

        return hash

    def gen_etag(self, path):
        """Generate etag for file."""
        hashes = []

        with open(path, "rb") as f:
            while True:
                data = f.read(self.CHUNK_SIZE)

                if not data:
                    break

                hashes.append(self.hash_data(data))
        # file size is 0
        if not hashes:
            return
        # file size is < 1 chunk
        elif len(hashes) == 1:
            # format the hash as a hexadecimal, as etags are
            return '"{}"'.format(hashes[0].hexdigest())
        else:
            # esentially generates a hash of hashes, so lambda function wrapped in reduces concatenates the hashes, then we hash them.
            hash = self.hash_data(
                # reduce alternates between the two functions in the lambda. So it generates ((((0+h1)+h2)+h3)+h4) so on and so forth
                functools.reduce(lambda x, y: x + y, (h.digest() for h in hashes))
            )
            # returns hash-NoOfChunks which is the AWS convention
            return '"{}-{}"'.format(hash.hexdigest(), len(hashes))

    def upload_file(self, bucket, path, key):
        # guesses content type
        content_type = mimetypes.guess_type(key)[0] or "text/plain"
        # checks the local file etag against the AWS file etag
        etag = self.gen_etag(path)
        if self.manifest.get(key, "") == etag:
            # print("Skipping {}, ETags match".format(key))
            return

        return bucket.upload_file(
            path,
            key,
            ExtraArgs={"ContentType": content_type},
            Config=self.transfer_config,
        )

    def compare_files(self, bucket, local_files):
        for key in self.manifest:
            if key in local_files:
                continue
            else:
                print(key + " no longer in local directory, deleting")
                bucket.delete_objects(Delete={"Objects": [{"Key": key}]})

    def sync(self, pathname, bucket_name):
        """Sync files from PATHNAME to a specific BUCKET"""
        bucket = self.s3.Bucket(bucket_name)
        # loads manifest of ETags within the bucket
        self.load_manifest(bucket)

        root = Path(pathname).expanduser().resolve()
        localFiles = []
        # defining function here allows this function to have access the variables and root etc of the function its defined within
        def handle_directory(target):
            for p in target.iterdir():
                if p.is_dir():
                    handle_directory(p)
                if p.is_file():
                    # prints out the absolute and relative path
                    self.upload_file(
                        bucket, str(p), str((p.relative_to(root)).as_posix())
                    )
                    localFiles.append(str((p.relative_to(root)).as_posix()))

        handle_directory(root)
        self.compare_files(bucket, localFiles)
