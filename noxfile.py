# noxfile.py
import tempfile

import nox


@nox.session(python=["3.8", "3.7", "3.9", "3.10"])
def tests(session):
    session.run("poetry", "install", external=True)
    session.run("pytest")


@nox.session(python="3.8")
def safety(session):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install("safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")


# end
