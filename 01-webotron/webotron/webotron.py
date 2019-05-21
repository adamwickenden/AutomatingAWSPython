## Run pipenv shell to generate the virtual environment to run the script in
import boto3

import click

from webotron.bucket import BucketManager
from webotron import util

# define empty global variables so they are accessible to all but can be set in the click group
session = None
bucket_manager = None

# creates a group called cli, which we are delegating control of commands to, as opposed to click
@click.group()
# ability to pass in a profile,defaults to none
@click.option("--profile", default=None, help="Use a given AWS profile")
def cli(profile):
    "Webotron deploys website to AWS"
    # use the global key word to return the assignments out of this fn
    global session, bucket_manager
    # define a dictionary (key/value) which we can assign the passed profile to
    session_cfg = {}
    if profile:
        session_cfg["profile_name"] = profile

    # ** is a "glob" operator, it takes a dictionary as the inputs to a function eg: key=value
    session = boto3.Session(**session_cfg)
    # bucket_manager will hold all the resources we need instead of calling them one by one
    bucket_manager = BucketManager(session)
    pass


# top part is a decorator that tells click about the function and allows it to control how it works
@cli.command("list-buckets")
def list_buckets():
    """List all s3 Buckets"""
    for bucket in bucket_manager.all_buckets():
        print(bucket)


@cli.command("list-bucket-objects")
@click.argument("bucket")
def list_bucket_objects(bucket):
    """List objects within a Bucket"""
    for obj in bucket_manager.all_objects(bucket):
        print(obj)


@cli.command("setup-bucket")
@click.argument("bucket")
def setup_bucket(bucket):
    """"Create and configure bucket to host static site"""
    s3_bucket = bucket_manager.init_bucket(bucket)
    bucket_manager.set_policy(s3_bucket)
    bucket_manager.configure_website(s3_bucket)

    return


@cli.command("sync")
@click.argument("pathname", type=click.Path(exists=True))
@click.argument("bucket")
def sync(pathname, bucket):
    """Sync contants of PATHNAME to BUCKET"""
    bucket_manager.sync(pathname, bucket)
    print(bucket_manager.get_bucket_url(bucket_manager.s3.Bucket(bucket)))


# if statement means that when file is run as a script it will execute (script is main), when its imported as a module (script not main) it wont run
if __name__ == "__main__":
    cli()
