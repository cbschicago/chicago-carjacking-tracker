import argparse
from base64 import decodebytes
from io import StringIO
import os
import paramiko
import pysftp

cnopts = pysftp.CnOpts()
cnopts.hostkeys.add(
    "ftp.cbslocal.com",
    "ssh-rsa",
    paramiko.RSAKey(
        data=decodebytes(
            bytes(os.getenv("wbbm_sftp_server_public_key").encode("UTF-8"))
        )
    ),
)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--create-directory",
    help="whether to create the path to the remote file if it doesn't already exist",
    action="store_true",
)
parser.add_argument("localpath", type=str, help="the local path and filename")
parser.add_argument("remotepath", type=str, help="the remote path and filename")
args = parser.parse_args()

with pysftp.Connection(
    "ftp.cbslocal.com",
    username="interactiveWBBM",
    private_key=paramiko.RSAKey.from_private_key(
        StringIO(os.getenv("wbbm_sftp_private_key"))
    ),
    cnopts=cnopts,
) as sftp:
    remote_directory = os.path.dirname(args.remotepath)

    def create_file():
        sftp.put(localpath=args.localpath, remotepath=args.remotepath, confirm=True)
        print(f"uploaded file to '{args.remotepath}'")

    if sftp.exists(remote_directory):
        create_file()
    else:
        if args.create_directory:
            create_file()
        else:
            print(
                f"The remote directory '{remote_directory}' does not exist on the server. "
                "Create the folder first or use option --create-directory"
            )
            exit()
