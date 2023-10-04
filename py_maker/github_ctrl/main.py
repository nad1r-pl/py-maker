"""Define the GitHub class.

This is a class to encapsulate the GitHub API and is responsible for
authenticating with GitHub and performing the necessary operations.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from github import Auth, Github
from github.GithubException import GithubException

if TYPE_CHECKING:
    from github.AuthenticatedUser import AuthenticatedUser
    from github.NamedUser import NamedUser
    from github.Repository import Repository


def git_error(exc: GithubException) -> None:
    """Display any errors cleanly during a git operation."""
    message = exc.data.get("message")
    error = exc.data.get("errors", None)
    error_message = ""
    if error:
        error_message = f"({error[0].get('message')})".capitalize()
    print(f"Error creating repository: {message} {error_message}")


class GitHub:
    """Define the main GitHub class."""

    def __init__(
        self,
        github_token: str,
        repo_name: str,
    ):
        """Initialize the GitHub class."""
        self.github_token = github_token
        if self.github_token is None:
            raise ValueError("GitHub token must be provided.")  # noqa: TRY003

        self._auth = Auth.Token(self.github_token)
        self._github = Github(auth=self._auth)
        self._user = self._github.get_user()

        self.repo_name = repo_name

    def __del__(self) -> None:
        """Close the underlying Github object when we are done."""
        self._github.close()

    @property
    def user(self) -> Union[AuthenticatedUser, NamedUser]:
        """Return the GitHub user object."""
        return self._user

    @property
    def repo(self) -> Union[Repository, None]:
        """Return the GitHub repository object."""
        try:
            return self._user.get_repo(self.repo_name)
        except AssertionError:
            print(f"Repository '{self.repo_name}' does not exist.")
            return None

    def create_repo(
        self, repo_name: Optional[str] = None, private: bool = False
    ) -> Union[Repository, None]:
        """Create a new repository.

        Args:
            repo_name: The name of the repository to create.
            private: Whether the repository should be private or not.
        """
        if repo_name is None:
            raise ValueError(  # noqa: TRY003
                "Repository name must be provided."
            )

        self.repo_name = repo_name

        try:
            repo = self._user.create_repo(  # type: ignore
                repo_name, private=private
            )
        except GithubException as exc:
            git_error(exc)
            return None
        else:
            return repo
