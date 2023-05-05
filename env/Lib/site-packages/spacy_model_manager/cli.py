# pylint: disable=unused-argument

import re
import sys
from typing import Optional

import click

from spacy_model_manager.lib import (
    SPACY_MODEL_NAMES,
    install_spacy_model,
    list_spacy_models,
    uninstall_spacy_model,
)

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

PATH_METAVAR = "<path>"
INT_METAVAR = "<n>"
VERSION_METAVAR = "<version>"
MODEL_METAVAR = "<model>"


def validate_version_string(ctx, param, value: Optional[str]) -> Optional[str]:
    """
    Callback for click commands that checks that version string is valid
    """

    if value is None:
        return None

    version_pattern = re.compile(r"\d+(?:\.\d+)+")

    if not version_pattern.match(value):
        raise click.BadParameter(value)

    return value


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def spacy_model():
    """
    Command line utility to view, install, and upgrade spaCy models
    """


@spacy_model.command("list", context_settings=CONTEXT_SETTINGS)
def _list():
    """
    List installed and available models.
    """

    status = list_spacy_models()
    sys.exit(status)


@spacy_model.command(context_settings=CONTEXT_SETTINGS)
@click.argument("model", metavar=MODEL_METAVAR, type=click.Choice(SPACY_MODEL_NAMES))
@click.option(
    "--model-version",
    required=False,
    metavar=VERSION_METAVAR,
    callback=validate_version_string,
    help="Install a given version.",
)
def install(model, model_version):
    """
    Install <model>.
    """

    status = install_spacy_model(model, version=model_version, upgrade=False)
    sys.exit(status)


@spacy_model.command(context_settings=CONTEXT_SETTINGS)
@click.argument("model", metavar=MODEL_METAVAR, type=click.Choice(SPACY_MODEL_NAMES))
def upgrade(model):
    """
    Upgrade <model>.
    """

    status = install_spacy_model(model, version=None, upgrade=True)
    sys.exit(status)


@spacy_model.command(context_settings=CONTEXT_SETTINGS)
@click.argument("model", metavar=MODEL_METAVAR, type=click.Choice(SPACY_MODEL_NAMES))
def remove(model):
    """
    Uninstall <model>.
    """

    status = uninstall_spacy_model(model)
    sys.exit(status)
