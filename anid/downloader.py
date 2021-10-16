import click
import requests

from pathlib import Path
from requests.models import ChunkedEncodingError
from tqdm import tqdm

DOWNLOAD_FOLDER = Path('.')
"""pathlib.Path: Points to the target directory of downloads."""


def downloader(url: str, resume_byte_pos: int = None, file_name: str = None):
    """Download url in ``URLS[position]`` to disk with possible resumption.

    Parameters
    ----------
    url: str
        url to be downloaded.
    resume_byte_pos: int
        Position of byte from where to resume the download

    """
    # Get size of file
    r = requests.head(url)
    file_size = int(r.headers.get('content-length', 0))

    # Append information to resume download at specific byte position
    # to header
    resume_header = ({'Range': f'bytes={resume_byte_pos}-'}
                     if resume_byte_pos else None)

    # Establish connection
    r = requests.get(url, stream=True, headers=resume_header)

    # Set configuration
    block_size = 1024
    initial_pos = resume_byte_pos if resume_byte_pos else 0
    mode = 'ab' if resume_byte_pos else 'wb'
    if file_name is None:
        file = DOWNLOAD_FOLDER / '-'.join(url.split('/')[-3:])
    else:
        file = DOWNLOAD_FOLDER / file_name

    with open(file, mode) as f:
        with tqdm(total=file_size, unit='B',
                  unit_scale=True, unit_divisor=1024,
                  desc=file.name, initial=initial_pos,
                  ascii=True, miniters=1) as pbar:
            try:
                for chunk in r.iter_content(32 * block_size):
                    f.write(chunk)
                    pbar.update(len(chunk))
            except ChunkedEncodingError:
                click.echo('Connection Broken! Chunked Encoding Error')


def download_file(url: str, file_name: str = None) -> None:
    """Execute the correct download operation.

    Depending on the size of the file online and offline, resume the
    download if the file offline is smaller than online.

    Parameters
    ----------
    url: str
        url to be downloaded.

    """
    # Establish connection to header of file
    r = requests.head(url)

    # Get filesize of online and offline file
    file_size_online = int(r.headers.get('content-length', 0))
    if file_name is None:
        file = DOWNLOAD_FOLDER / '-'.join(url.split('/')[-3:])
    else:
        file = DOWNLOAD_FOLDER / file_name

    if file.exists():
        file_size_offline = file.stat().st_size

        if file_size_online != file_size_offline:
            click.echo(f'File {file} is incomplete. Resume download.')
            downloader(url, file_size_offline, file)
        else:
            click.echo(f'File {file} is complete. Skip download.')
            pass
    else:
        click.echo(f'File {file} does not exist. Start download.')
        downloader(url, file_name=file)