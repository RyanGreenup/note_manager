#!/usr/bin/env python3
import click
import os
from pathlib import Path
from enum import Enum

"""A Notetaking CLI tool."""


def add_directory_option(func):
    func = click.option(
        "--directory",
        default=os.path.join(os.path.expanduser("~"), "Notes/slipbox"),
        type=click.Path(exists=True),
        help="The directory to operate on",
    )(func)
    return func


@click.command()
@add_directory_option
@click.argument("source", type=click.Path(exists=True))
@click.argument("destination")
def Move(source: Path, destination: Path, directory: Path):
    """Hello. If the destination is a directory, preserves the basename."""
    print(f"Source: {source}, Destination: {destination}")


def get_notes():
    notes_dir = "/home/ryan/Notes/slipbox/"
    files = [
        [os.path.join(root, file) for file in files if file.endswith(".md")]
        for root, _, files in os.walk(notes_dir)
    ]
    # Flatten the list
    files = [file for sublist in files for file in sublist]
    print(files)


if __name__ == "__main__":
    Move()
