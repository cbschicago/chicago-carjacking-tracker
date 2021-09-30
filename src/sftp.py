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
    sftp.put(localpath=args.localpath, remotepath=args.remotepath, confirm=True)
