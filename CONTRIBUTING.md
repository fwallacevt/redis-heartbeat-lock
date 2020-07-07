# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs [here](https://github.com/fwallacevt/simple_redis_lock/issues).

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

### Write Documentation

Simple Python Redis locking could always use more documentation, whether as part of the official docs, in docstrings, or even on the web in blog posts, articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue [here](https://github.com/fwallacevt/simple_redis_lock/issues).

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Getting Started

Ready to contribute? Here's how to set up `simple_redis_lock` for local development.

* Fork the `simple_redis_lock` repo on GitHub.
* Clone your fork locally:

    ```sh
    git clone git@github.com:your_name_here/simple_redis_lock.git
    ```

* Ensure [poetry](https://python-poetry.org/docs/) is installed.
* Install dependencies and start your virtualenv:

    ```sh
    poetry install
    ```

* Create a branch for local development:

    ```sh
    git checkout -b name-of-your-bugfix-or-feature
    ```

* When you're done making changes, check that your changes pass the tests, including testing other Python versions, with tox:

    ```sh
    tox
    ```

* Commit your changes and push your branch to GitHub:

    ```sh
    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature
    ```

* Submit a pull request through the GitHub website.

### Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a docstring, and add the feature to the list in README.md.
3. The pull request should work for Python 3.7 and 3.8, and for PyPy. Check [Travis](https://travis-ci.com/fwallacevt/simple_redis_lock/pull_requests) and make sure that the tests pass for all supported Python versions.

### Tips

To run a subset of tests::

```sh
pytest tests.test_simple_redis_lock
```

## Deploying

A reminder for the maintainers on how to deploy. Make sure all your changes are committed (including an entry in `HISTORY.md`). Then run:

```sh
bump2version patch # possible: major / minor / patch
git push
git push --tags
```

Travis will then deploy to PyPI if tests pass.
