#!/usr/bin/env python3
import click
import os
from os import path
from pathlib import Path
import logging

# TODO need to also move .ipynb, .Rmd etc.


# Set up basic configuration for the logger
logging.basicConfig(level=logging.INFO)

"""A Notetaking CLI tool."""

NOTES_DIR = Path("~/Notes/slipbox").expanduser().absolute()
dest = Path("/home/ryan/Notes/20210802123456.md")
dest.absolute().is_relative_to(NOTES_DIR)


def add_directory_option(func):
    func = click.option(
        "--directory",
        default=NOTES_DIR,
        type=click.Path(exists=True),
        help="The directory to operate on",
    )(func)
    return func


@click.command()
@add_directory_option
@click.argument("source", type=click.Path(exists=True))
@click.argument("destination")
def Move(source: str, destination: str, directory: Path):
    source_p = Path(source)
    destination_p = Path(destination)
    directory_p = Path(directory)

    # Check if destination is under directory
    if not target_under_directory(source_p, Path(directory_p)):
        logging.warning("Destination is not under directory")
        if "y" != input("Continue? [y/n]"):
            return

    # Handle moving directories
    if os.path.isdir(source_p):
        if os.path.isdir(destination_p):
            for file in Path(source_p).glob("**/*.md"):
                move_file_to_file(file, destination_p, directory)
        else:
            # Make the user create a directory, don't assume
            logging.error(
                "Source is a directory but destination is not, create a directory first"
            )
    else:
        move_file_to_file(source_p, destination_p, directory)


def move_file_to_file(
    source: Path, destination: Path, directory: Path, move_file: bool = True
):
    """Move a note and update links. If the destination is a directory, preserves the basename."""
    # Handle the target being a directory
    if os.path.isdir(destination):
        dest_d = destination
        destination = Path.joinpath(destination, os.path.basename(source))
    else:
        dest_d = os.path.dirname(destination)

    print(f"Source: {source}, Destination: {destination}")

    # 1. Change links within the file being moved
    remap = {
        file: {
            "from": path.relpath(file, path.dirname(source)),
            "to": path.relpath(file, dest_d),
        }
        for file in directory.glob("**/*.md")
    }
    for file, info in remap.items():
        replace_links(info["from"], info["to"], source)

    # 2. Change links in other files
    remap = {
        file: {
            # TODO define destination var if it's a dir not a file
            "from": path.relpath(source, path.dirname(file)),
            "to": path.relpath(destination, path.dirname(file)),
        }
        for file in directory.glob("**/*.md")
    }

    for file, info in remap.items():
        replace_links(info["from"], info["to"], file)

    # 3. Move the file
    if move_file:
        source.rename(destination)


def replace_links(before: str, after: str, file: Path):
    # TODO deal with link formats
    # TODO strip leading ./
    with open(file, "r") as f:
        content = f.read()

    before_markdown_links = make_links(before)
    after_markdown_links = make_links(after)
    if any([ly in content for ly in before_markdown_links]):
        for before, after in zip(before_markdown_links, after_markdown_links):
            content = content.replace(before, after)

        with open(file, "w") as f:
            f.write(content)


def make_links(filepath: str) -> list[str]:
    filepath_no_ext = os.path.splitext(filepath)[0]
    return [
        # Markdown Links
        f"]({filepath})",
        # Wiki Links
        f"[[{filepath}]]",
        f"[[{filepath_no_ext}]]",
        # Definition LInks
        f": {filepath}",
        # HTML
        f'="{filepath}"',
        f'= "{filepath}"',
        f"='{filepath}'",
        f"= '{filepath}'",
    ]


def target_under_directory(source: Path, dest_dir: Path) -> bool:
    return str(dest_dir) in str(source)


if __name__ == "__main__":
    Move()
