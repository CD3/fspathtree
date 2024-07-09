"""Nox sessions."""

import nox

package = "fspathtree/"
python_versions = ["3.10"]
nox.needs_version = ">= 2021.6.6"
nox.options.sessions = ("tests",)


@nox.session(python=python_versions)
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    session.install(".")
    session.install("pytest")
    session.run("pytest", *session.posargs)


@nox.session
def lint(session: nox.Session) -> None:
    """Run th elinter"""
    session.install("pre-commit")
    session.run(
        "pre-commit", "run", "--all-file", "--show-diff-on-failure", *session.posargs
    )
