[![Nyaa Watcher Banner](https://raw.githubusercontent.com/resort-io/assets/main/nyaa-watcher/img/banner.png)](https://github.com/resort-io/nyaa-watcher)

# Contributing

* [Reporting Bugs](#reporting-bugs)
* [Suggesting Features](#suggesting-features)
* [Creating Pull Requests](#creating-pull-requests)

## Reporting Bugs

> ### Before Reporting a Bug
> 
> * Make sure that you are using the latest version and have read the [setup documentation](https://github.com/resort-io/nyaa-watcher/blob/main/SETUP.md) and [Wiki pages](https://github.com/resort-io/nyaa-watcher/wiki) to ensure the bug is not a configuration error.
> * Search through the [GitHub issues](https://github.com/resort-io/nyaa-watcher/issues) to see if the bug has already been reported. If it has, add a comment to the existing issue instead of opening a new one.

### How to Report a Bug

Bug reports are tracked as [GitHub issues](https://github.com/resort-io/nyaa-watcher/issues) with the ***[BUG]*** prefix in the title.

* Navigate to the [new issue page](https://github.com/resort-io/nyaa-watcher/issues/new/choose) and select the **Bug Report** template.
* Use a **clear and descriptive title** with the ***[BUG]*** prefix and the ***bug*** label.
* Copy the **debug log message** from the watcher and paste into the issue textarea.
  * The debug log message can be obtained by setting the `LOG_LEVEL` environment variable to `DEBUG` and restarting the watcher.
* Provide **any information** about the bug, such as steps that can possibly reproduce the bug.
* Provide **code changes** if you have any suggestions on how to fix the bug.

## Suggesting Features

> ### Before Suggesting a Feature
> 
> * Make sure that you are using the latest version and have read the [setup documentation](https://github.com/resort-io/nyaa-watcher/blob/main/SETUP.md) and [Wiki pages](https://github.com/resort-io/nyaa-watcher/wiki) to ensure the feature has not been implemented yet.
> * Search through the [GitHub issues](https://github.com/resort-io/nyaa-watcher/issues) to see if the feature has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.

### How to Suggest a Feature

Feature suggestions are tracked as [GitHub issues](https://github.com/resort-io/nyaa-watcher/issues) with the ***[FEAT]*** prefix in the title.

* Navigate to the [new issue page](https://github.com/resort-io/nyaa-watcher/issues/new/choose) and select the **Feature Suggestion** template.
* Use a **clear and descriptive title** with the ***[FEAT]*** prefix and the ***enhancement*** label.
* Provide a **description of the suggested enhancement** in as many details as possible.
* Describe **how the suggested feature will change the current behavior**.
* Explain **why the feature would be beneficial to most**, if not all, nyaa-watcher users.
* You can **include screenshots** to help you demonstrate how the feature should work or to point out the part at which the suggestion is related to.
* Provide **code changes** if you have any suggestions on how to implement the feature.

## Creating Pull Requests

> ### Before Creating a Pull Request
> 
> I ask to please only submit pull requests that are meaningful and relevant to the project, and are not just syntax/grammar changes.
> If you are unsure about your pull request, you can make a [discussion post](https://github.com/resort-io/nyaa-watcher/discussions) to get feedback from the maintainers and the community.

### How to Create a Pull Request

* Fork the repository and clone it to your local machine.
* Create a new branch for your feature or bug fix.
* Make a copy of the `.env.example` file and rename it to `.env`.
* Make your changes and push your changes to your fork.
* Create a pull request to the `develop` branch of the main repository.

Since this project adds features with each release, pull requests will be merged into the `develop` branch, and then the `main` as a stable release.

> All versions are numbered using the `v1.X.Y` format.
> 
> * `X` is for **new features or additions**.
> * `Y` is for **bug fixes or minor changes**.

### Environment Variables

| Key               | Description                                                                                  | Values                                                                                |
|-------------------|----------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| `ENV`             | Determines which JSON files to use. JSON files will be generated when running `__init__.py`. | `DEVELOPMENT` (uses the `dev.*.json` files) or `PRODUCTION` (uses the `*.json` files) |
| `LOG_LEVEL`       | Logging level for the watcher.                                                               | `INFO` or `DEBUG`                                                                     |
| `LOG_RSS_ENTRIES` | Determines whether to log each RSS entry and corresponding matches when searching.           | `true` (`DEBUG` logging only) or `false`                                              |
| `LOG_TIPS`        | Determines whether to log the watcher tips.                                                  | `true` or `false`                                                                     |
| `WATCHER_DIR`     | Directory for watcher python files, relative to `__init__.py`.                               | `./`                                                                                  |
| `DOWNLOADS_DIR`   | Directory for the downloaded torrent files.                                                  | `./downloads` (Directory is not tracked)                                              |
| `INTERVAL_SEC`    | Interval between each subscriptions search.                                                  | Any integer                                                                           |

### Improving The Documentation

If your pull request **adds or changes a functionality that will affect the user experience** or the setup process of the watcher, please update the corresponding `README.md` and/or `SETUP.md` sections.
