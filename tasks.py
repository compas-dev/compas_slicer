# -*- coding: utf-8 -*-
import contextlib
import glob
import os
import sys
from shutil import rmtree

from compas_invocations2.grasshopper import publish_yak, yakerize
from invoke import Collection, Exit, task

BASE_FOLDER = os.path.dirname(__file__)


class Log:
    def __init__(self, out=sys.stdout, err=sys.stderr):
        self.out = out
        self.err = err

    def flush(self):
        self.out.flush()
        self.err.flush()

    def write(self, message):
        self.flush()
        self.out.write(message + "\n")
        self.out.flush()

    def info(self, message):
        self.write(f"[INFO] {message}")

    def warn(self, message):
        self.write(f"[WARN] {message}")


log = Log()


def confirm(question):
    while True:
        response = input(question).lower().strip()

        if not response or response in ("n", "no"):
            return False

        if response in ("y", "yes"):
            return True

        print("Focus, kid! It is either (y)es or (n)o", file=sys.stderr)


@task(default=True)
def help(ctx):
    """Lists available tasks and usage."""
    ctx.run("invoke --list")
    log.write('Use "invoke -h <taskname>" to get detailed help for a task.')


@task(
    help={
        "docs": "True to clean up generated documentation, otherwise False",
        "bytecode": "True to clean up compiled python files, otherwise False.",
        "builds": "True to clean up build/packaging artifacts, otherwise False.",
    }
)
def clean(ctx, docs=True, bytecode=True, builds=True):
    """Cleans the local copy from compiled artifacts."""

    with chdir(BASE_FOLDER):
        if bytecode:
            for root, dirs, files in os.walk(BASE_FOLDER):
                for f in files:
                    if f.endswith(".pyc"):
                        os.remove(os.path.join(root, f))
                if ".git" in dirs:
                    dirs.remove(".git")

        folders = []

        if docs:
            folders.append("docs/api/generated")

        folders.append("dist/")

        if bytecode:
            for t in ("src", "tests"):
                folders.extend(glob.glob(f"{t}/**/__pycache__", recursive=True))

        if builds:
            folders.append("build/")
            folders.append("src/compas_slicer.egg-info/")

        for folder in folders:
            rmtree(os.path.join(BASE_FOLDER, folder), ignore_errors=True)


@task(
    help={
        "serve": "True to serve docs locally, otherwise just build.",
        "strict": "True to fail on warnings, otherwise False.",
    }
)
def docs(ctx, serve=False, strict=True):
    """Builds package's HTML documentation using MkDocs."""
    with chdir(BASE_FOLDER):
        if serve:
            ctx.run("mkdocs serve")
        else:
            cmd = "mkdocs build"
            if strict:
                cmd += " --strict"
            ctx.run(cmd)


@task()
def check(ctx):
    """Check the consistency of documentation, coding style and a few other things."""

    with chdir(BASE_FOLDER):
        log.write("Running ruff linter...")
        ctx.run("ruff check src tests")

        log.write("Running ruff formatter check...")
        ctx.run("ruff format --check src tests")


@task(help={"checks": "True to run all checks before testing, otherwise False."})
def test(ctx, checks=False, doctest=False):
    """Run all tests."""
    if checks:
        check(ctx)

    with chdir(BASE_FOLDER):
        cmd = ["pytest"]
        if doctest:
            cmd.append("--doctest-modules")

        ctx.run(" ".join(cmd))


@task()
def lint(ctx):
    """Check the consistency of coding style with ruff."""
    log.write("Running ruff linter...")
    ctx.run("ruff check src/")


@task()
def format(ctx):
    """Format code with ruff."""
    log.write("Running ruff formatter...")
    ctx.run("ruff format src/ tests/")
    ctx.run("ruff check --fix src/ tests/")


@task()
def typecheck(ctx):
    """Run type checking with mypy."""
    log.write("Running mypy type checker...")
    ctx.run("mypy src/compas_slicer --ignore-missing-imports")


@task
def prepare_changelog(ctx):
    """Prepare changelog for next release."""
    UNRELEASED_CHANGELOG_TEMPLATE = "\nUnreleased\n----------\n\n**Added**\n\n**Changed**\n\n**Fixed**\n\n**Deprecated**\n\n**Removed**\n"

    with chdir(BASE_FOLDER):
        # Preparing changelog for next release
        with open("CHANGELOG.rst", "r+") as changelog:
            content = changelog.read()
            start_index = content.index("----------")
            start_index = content.rindex("\n", 0, start_index - 1)
            last_version = content[start_index : start_index + 11].strip()

            if last_version == "Unreleased":
                log.write("Already up-to-date")
                return

            changelog.seek(0)
            changelog.write(
                content[0:start_index]
                + UNRELEASED_CHANGELOG_TEMPLATE
                + content[start_index:]
            )

        ctx.run('git add CHANGELOG.rst && git commit -m "Prepare changelog for next release"')


@task(
    help={
        "release_type": "Type of release follows semver rules. Must be one of: major, minor, patch."
    }
)
def release(ctx, release_type):
    """Releases the project in one swift command!"""
    if release_type not in ("patch", "minor", "major"):
        raise Exit("The release type parameter is invalid.\nMust be one of: major, minor, patch")

    # Run checks
    ctx.run("invoke check test")

    # Bump version and git tag it
    ctx.run(f"bump2version {release_type} --verbose")

    # Build project
    ctx.run("python -m build")

    # Prepare changelog for next release
    prepare_changelog(ctx)

    # Clean up local artifacts
    clean(ctx)

    # Upload to pypi
    if confirm(
        "Everything is ready. You are about to push to git which will trigger a release to pypi.org. Are you sure? [y/N]"
    ):
        ctx.run("git push --tags && git push")
    else:
        raise Exit("You need to manually revert the tag/commits created.")


@contextlib.contextmanager
def chdir(dirname=None):
    current_dir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(current_dir)


# Create collection and add compas_invocations2 tasks
ns = Collection()
ns.add_task(yakerize)
ns.add_task(publish_yak)
ns.add_task(help)
ns.add_task(clean)
ns.add_task(docs)
ns.add_task(check)
ns.add_task(test)
ns.add_task(lint)
ns.add_task(format)
ns.add_task(typecheck)
ns.add_task(prepare_changelog)
ns.add_task(release)
