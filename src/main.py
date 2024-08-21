#!/usr/bin/env python3
import click
import os
import re
from os import path
from pathlib import Path
import logging
from pprint import pprint

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
    """Move a note and update links. If the destination is a directory, preserves the basename."""
    if os.path.isdir(destination):
        dest_d = destination
        destination = os.path.join(destination, os.path.basename(source))
    else:
        dest_d = os.path.dirname(destination)

    source_p: Path = Path(source)
    dest_p: Path = Path(destination)
    dir_p: Path = Path(directory)
    print(f"Source: {source}, Destination: {destination}")

    # TODO is the notes directory even needed?
    # Check if destination is under directory
    if not target_under_directory(source_p, dir_p):
        logging.warning("Destination is not under directory")

    # DONE update links inside that file
    remap = {
        file: {
            "from": path.relpath(file, path.dirname(source)),
            "to": path.relpath(file, dest_d),
            # TODO refactor and handle, e.g. ./knn.md and knn.md
            # "candidates": [
            #     ": " + path.relpath(file, source),
            #     f"[[{path.relpath(file, source)}]]",
            #     f"[[{path.splitext(path.relpath(file, source))[0]}]]",
            #     f"({path.relpath(file, source)})",
            #     f'="{path.relpath(file, source)}"',  # for images and HTML
            #     f'= "{path.relpath(file, source)}"',  # for images and HTML
            # ],
        }
        for file in directory.glob("**/*.md")
    }

    # pprint(remap)

    # TODO deal with link formats
    # TODO strip leading ./
    with open(source, "r") as f:
        content = f.read()

    for file, info in remap.items():
        content = replace_links(info["from"], info["to"], content)

    with open(source, "w") as f:
        f.write(content)

    # TODO assess if quicker to read the file and check if the string is in there
    # or just find/replace
    remap = {
        file: {
            # TODO define destination var if it's a dir not a file
            "from": path.relpath(source, path.dirname(file)),
            "to": path.relpath(destination, path.dirname(file)),
        }
        for file in directory.glob("**/*.md")
    }

    pprint(remap)

    for file, info in remap.items():
        # TODO deal with link formats
        # TODO strip leading ./
        with open(file, "r") as f:
            content = f.read()

        if any([ly in content for ly in make_links(info["from"])]):
            content = replace_links(info["from"], info["to"], content)

            with open(file, "w") as f:
                f.write(content)


def replace_links(before: str, after: str, content: str) -> str:
    before_markdown_links = make_links(before)
    after_markdown_links = make_links(after)

    if any([ly in content for ly in before_markdown_links]):
        for before, after in zip(before_markdown_links, after_markdown_links):
            content = content.replace(before, after)

    return content


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


def file_contains_link(source: str, file: str) -> bool:
    # rel_source = os.path.relpath(source, os.path.dirname(file))
    # rel_source_no_ext = os.path.splitext(rel_source)[0]
    rel_source = str(file.relative_to(source, walk_up=True))
    rel_source_no_ext = str(os.path.splitext(rel_source)[0])
    candidates = [
        f": {rel_source}",
        f"[[{rel_source}]]",
        f"[[{rel_source_no_ext}]]",
        f"({rel_source})",
        f'"{rel_source}"',  # for images and HTML
    ]

    with open(file) as f:
        for line in f:
            if any(c in line for c in candidates):
                return True
    return False


def make_md_links(path: str) -> list[str]:
    path_no_ext = os.path.splitext(path)[0]
    return [
        f": {path}",
        f"[[{path}]]",
        f"[[{path_no_ext}]]",
        f"({path})",
        # For HTML etc.
        f'="{path}"',
        f'= "{path}"',
        f"='{path}'",
        f"= '{path}'",
    ]


def file_is_note_and_contains_string(filepath: Path, string: str) -> bool:
    print(filepath)
    if not file_is_note(filepath):
        return False
    return file_contains_string(filepath, string)


def file_is_note(filepath: Path) -> bool:
    return filepath.suffix in [".md"]


def file_contains_string(file: Path, string: str) -> bool:
    return string in file.read_text()


def target_under_directory(source: Path, dest_dir: Path) -> bool:
    return source.absolute().is_relative_to(dest_dir.absolute())


def get_notes() -> list[Path]:
    notes_dir = "/home/ryan/Notes/slipbox/"
    files = [
        [os.path.join(root, file) for file in files if file.endswith(".md")]
        for root, _, files in os.walk(notes_dir)
    ]
    # Flatten the list
    files = [file for sublist in files for file in sublist]
    # Make them paths
    files = [Path(file) for file in files]

    return files


if __name__ == "__main__":
    Move()
