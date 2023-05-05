# pylint: disable=import-outside-toplevel,broad-except

import json
import sys
from collections import namedtuple
from importlib import reload
from typing import Dict, List, Optional

import click
import pkg_resources
import requests
import spacy
from packaging.version import parse
from rich.console import Console
from spacy.util import run_command
from tabulate import tabulate

console = Console()

# Spacy trained model names
SPACY_MODEL_NAMES = [
    "ca_core_news_lg",
    "ca_core_news_md",
    "ca_core_news_sm",
    "ca_core_news_trf",
    "da_core_news_lg",
    "da_core_news_md",
    "da_core_news_sm",
    "da_core_news_trf",
    "de_core_news_lg",
    "de_core_news_md",
    "de_core_news_sm",
    "de_dep_news_trf",
    "de_pytt_bertbasecased_lg",
    "de_trf_bertbasecased_lg",
    "el_core_news_lg",
    "el_core_news_md",
    "el_core_news_sm",
    "en_core_web_lg",
    "en_core_web_md",
    "en_core_web_sm",
    "en_core_web_trf",
    "en_depent_web_md",
    "en_pytt_bertbaseuncased_lg",
    "en_pytt_distilbertbaseuncased_lg",
    "en_pytt_robertabase_lg",
    "en_pytt_xlnetbasecased_lg",
    "en_trf_bertbaseuncased_lg",
    "en_trf_distilbertbaseuncased_lg",
    "en_trf_robertabase_lg",
    "en_trf_xlnetbasecased_lg",
    "en_vectors_glove_md",
    "en_vectors_web_lg",
    "es_core_news_lg",
    "es_core_news_md",
    "es_core_news_sm",
    "es_core_web_md",
    "es_dep_news_trf",
    "fr_core_news_lg",
    "fr_core_news_md",
    "fr_core_news_sm",
    "fr_dep_news_trf",
    "fr_depvec_web_lg",
    "it_core_news_lg",
    "it_core_news_md",
    "it_core_news_sm",
    "ja_core_news_lg",
    "ja_core_news_md",
    "ja_core_news_sm",
    "ja_core_news_trf",
    "lt_core_news_lg",
    "lt_core_news_md",
    "lt_core_news_sm",
    "mk_core_news_lg",
    "mk_core_news_md",
    "mk_core_news_sm",
    "nb_core_news_lg",
    "nb_core_news_md",
    "nb_core_news_sm",
    "nl_core_news_lg",
    "nl_core_news_md",
    "nl_core_news_sm",
    "pl_core_news_lg",
    "pl_core_news_md",
    "pl_core_news_sm",
    "pt_core_news_lg",
    "pt_core_news_md",
    "pt_core_news_sm",
    "ro_core_news_lg",
    "ro_core_news_md",
    "ro_core_news_sm",
    "ru_core_news_lg",
    "ru_core_news_md",
    "ru_core_news_sm",
    "xx_ent_wiki_sm",
    "xx_sent_ud_sm",
    "zh_core_web_lg",
    "zh_core_web_md",
    "zh_core_web_sm",
    "zh_core_web_trf",
]

SPACY_MODELS = namedtuple("SpacyModels", SPACY_MODEL_NAMES)(*SPACY_MODEL_NAMES)


def get_installed_model_version(name: str) -> Optional[str]:
    """
    Return the version of an installed package
    """

    try:
        return pkg_resources.get_distribution(name).version
    except pkg_resources.DistributionNotFound:
        return None


def get_spacy_models() -> Dict[str, List[str]]:
    """
    Get all versions of spaCy models from github
    """

    releases = {}

    paginated_url = "https://api.github.com/repos/explosion/spacy-models/releases?page=1&per_page=100"

    try:
        while paginated_url:
            response = requests.get(url=paginated_url)

            if not response.ok:
                response.raise_for_status()

            # Get name-version pairs
            for release in json.loads(response.content):
                name, version = release["tag_name"].split("-", maxsplit=1)

                # Skip alpha/beta versions
                if "a" in version or "b" in version:  # pragma: nocover
                    # https://github.com/nedbat/coveragepy/issues/198
                    continue

                releases[name] = [*releases.get(name, []), version]

            # Get the next page of results
            try:
                paginated_url = response.links["next"]["url"]
            except (AttributeError, KeyError):
                break

    except requests.HTTPError:
        releases = {name: [] for name in SPACY_MODEL_NAMES}

    return releases


def list_spacy_models() -> int:
    """
    Print installed spaCy models
    """

    with console.status(
        "[bold green]Fetching available model versions...", spinner="dots"
    ):
        releases = get_spacy_models()

    # Sort the results by version name
    releases = list(releases.items())
    releases.sort(key=lambda x: x[0])

    table = [["spaCy model", "installed version", "available versions"]]

    for name, versions in releases:
        table.append([name, get_installed_model_version(name), ", ".join(versions)])

    print(tabulate(table, headers="firstrow"))

    return 0


def install_spacy_model(
    model: str, version: Optional[str] = None, upgrade: bool = False
) -> int:
    """
    Install a given spaCy model
    """
    from spacy.cli.download import msg as spacy_msg

    # Check for existing version
    installed_version = get_installed_model_version(model)

    if not version and not upgrade and installed_version:
        click.echo(
            click.style(
                f"Model {model} already installed, version {installed_version}",
                fg="blue",
            )
        )
        click.echo(
            click.style(
                f"Please specify a version or run `spacy-model upgrade {model}` to upgrade to the latest version",
                fg="blue",
            )
        )
        return 0

    # Download quietly
    spacy_msg.no_print = True

    version_suffix, direct_download = (f"-{version}", True) if version else ("", False)

    try:
        with console.status(
            f"[bold green]Installing {model}{version_suffix}...", spinner="dots"
        ):
            spacy.cli.download(
                f"{model}{version_suffix}", direct_download, False, "--quiet"
            )
    except SystemExit:
        click.echo(
            click.style(
                f"❌ Unable to install spacy model {model}{version_suffix}", fg="red"
            ),
            err=True,
        )
        return -1

    # Confirm installation
    try:
        reload(pkg_resources)
        installed_version = pkg_resources.get_distribution(model).version

    except Exception as exc:
        click.echo(
            click.style(
                f"❌ Unable to confirm model installation, error: {exc}", fg="red"
            ),
            err=True,
        )
        return -1

    if version and parse(version) != parse(installed_version):
        click.echo(
            click.style(
                f"❌ Installed model version {installed_version} and specified version {version} differ",
                fg="red",
            ),
            err=True,
        )
        return -1

    click.echo(
        click.style(f"✔ Installed {model}, version {installed_version}", fg="green")
    )
    return 0


def uninstall_spacy_model(model: str) -> int:
    """
    Uninstall a given spaCy model
    """

    try:
        run_command([sys.executable, "-m", "pip", "uninstall", "--yes", model])
    except SystemExit:
        click.echo(
            click.style(f"❌ Unable to remove spacy model {model}", fg="red"),
            err=True,
        )
        return -1

    return 0
