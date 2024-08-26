---
layout: post
title: "Rendering MongoDB Driver Specifications as a Book"
date: 2024-08-26 07:36:01 -0400
comments: true
categories: MongoDB
tags: [mongodb, drivers]
image: /images/mongodb-logo.png
---

MongoDB's [Drivers Specifications](https://github.com/mongodb/specifications) have always been available on GitHub. Since the content [license is extremely permissive](https://creativecommons.org/licenses/by-nc-sa/3.0/us/) there are a number of things we could do to transform that work as long as we provide proper attribution.

Until recently, this content has always been maintained as [restructuredText](https://docutils.sourceforge.io/rst.html) documents, however with [DRIVERS-2789](https://jira.mongodb.org/browse/DRIVERS-2789) this content has all been converted to [Markdown](https://daringfireball.net/projects/markdown/). MongoDB decided to use this opportunity (via [DRIVERS-2881](https://jira.mongodb.org/browse/DRIVERS-2881)) to [publish the specifications to ReadTheDocs](https://specifications.readthedocs.io/en/latest/) using [MkDocs](https://docs.readthedocs.io/en/stable/intro/getting-started-with-mkdocs.html), however I wanted to try taking an alternate approach to see how difficult it would be to automate publication of Markdown content in book format.

## Configuration

Since the specifications are hosted on GitHub, I began by [forking the repository to `alexbevi/specifications`](https://github.com/alexbevi/specifications). Instead of `MkDocs` I chose [`mdBook`](https://rust-lang.github.io/mdBook/) as the tool for rendering Markdown to HTML as creating a book was as simple as:

1. [Defining a `book.toml`](https://rust-lang.github.io/mdBook/guide/creating.html#booktoml) with basic configuration options
2. [Outlining the book structure in a `SUMMARY.md`](https://rust-lang.github.io/mdBook/guide/creating.html#summarymd) file

I [defined my `book.toml`](https://raw.githubusercontent.com/alexbevi/specifications/mkbook/book.toml) to indicate all my Markdown files would be in the `source/` directory, [created a `source/SUMMARY.md`](https://raw.githubusercontent.com/alexbevi/specifications/mkbook/source/SUMMARY.md) file with links to all the Markdown files I wanted in my book and was basically done.

Testing this out was as easy as running `mdbook serve --open`:

```
mdbook serve --open
2024-08-26 07:56:39 [INFO] (mdbook::book): Book building has started
2024-08-26 07:56:39 [WARN] (mdbook::preprocess::index): It seems that there are both "README.md" and index.md under "/Users/alex/Workspace/specifications/source".
2024-08-26 07:56:39 [WARN] (mdbook::preprocess::index): mdbook converts "README.md" into index.html by default. It may cause
2024-08-26 07:56:39 [WARN] (mdbook::preprocess::index): unexpected behavior if putting both files under the same directory.
2024-08-26 07:56:39 [WARN] (mdbook::preprocess::index): To solve the warning, try to rearrange the book structure or disable
2024-08-26 07:56:39 [WARN] (mdbook::preprocess::index): "index" preprocessor to stop the conversion.
2024-08-26 07:56:39 [INFO] (mdbook::book): Running the html backend
2024-08-26 07:56:43 [INFO] (mdbook::cmd::serve): Serving on: http://localhost:3000
2024-08-26 07:56:43 [INFO] (mdbook): Opening web browser
2024-08-26 07:56:43 [INFO] (warp::server): Server::run; addr=[::1]:3000
2024-08-26 07:56:43 [INFO] (warp::server): listening on http://[::1]:3000
2024-08-26 07:56:43 [INFO] (mdbook::cmd::watch::poller): Watching for changes...
```

`mdBook` will process the `SUMMARY.md` file, generate HTML content based on the indexed Markdown files and open a preview in your default browser.

## Automation

Laying out the book and rendering it from Markdown to HTML turned out to be pretty easy, but MongoDB's engineers continuously refine the specifications so anything we generate would go stale fairly quickly. What if we could leverage [GitHub Actions](https://docs.github.com/en/actions) to refresh our fork of the `specifications` repository, rebuild our book and continuously publish as [GitHub Pages](https://pages.github.com/)?

We'll be publishing our repository to a GitHub Pages instance (see the [Quickstart for GitHub Pages](https://docs.github.com/en/pages/quickstart) if needed), so the first step is to ensure this has been configured. Next we'll setup workflow that GitHub Actions can use to:

1. Checkout the upstream repository
2. Sync the upstream repository's `master` branch with our fork's default branch (`mkbook` in this case)
3. Install `mdbook` and build our book based on the latest Markdown files
4. Deploy the HTML contents from our build target (`book/`) to the branch GitHub pages is configured to use (`gh-pages` in this case)

If you want to check out the latest version of this it's at [`.github/workflows/sync.yml`](https://raw.githubusercontent.com/alexbevi/specifications/mkbook/.github/workflows/sync.yml), but at the time of writing it looks like this:

```yaml
name: 'Scheduled Upstream Sync'
on:
  schedule:
    - cron:  '0 8 * * *'

  workflow_dispatch:  # click the button on Github repo!
    inputs:
      sync_test_mode: # Adds a boolean option that appears during manual workflow run for easy test mode config
        description: 'Fork Sync Test Mode'
        type: boolean
        default: false

jobs:
  sync_latest_from_upstream:
    runs-on: ubuntu-latest
    name: Sync latest commits from upstream repo

    steps:
    # REQUIRED step
    # Step 1: run a standard checkout action, provided by github
    - name: Checkout target repo
      uses: actions/checkout@v3
      with:
        # optional: set the branch to checkout,
        # sync action checks out your 'target_sync_branch' anyway
        ref:  mkbook
        # REQUIRED if your upstream repo is private (see wiki)
        # persist-credentials: false

    # REQUIRED step
    # Step 2: run the sync action
    - name: Sync upstream changes
      id: sync
      uses: aormsby/Fork-Sync-With-Upstream-action@v3.4.1
      with:
        target_sync_branch: mkbook
        # REQUIRED 'target_repo_token' exactly like this!
        target_repo_token: ${{ secrets.GITHUB_TOKEN }}
        upstream_sync_branch: master
        upstream_sync_repo: mongodb/specifications
        # upstream_repo_access_token: ${{ secrets.UPSTREAM_REPO_SECRET }}

        # Set test_mode true during manual dispatch to run tests instead of the true action!!
        test_mode: ${{ inputs.sync_test_mode }}

    # Step 3: Display a sample message based on the sync output var 'has_new_commits'
    - name: New commits found
      if: steps.sync.outputs.has_new_commits == 'true'
      run: echo "New commits were found to sync."

    - name: No new commits
      if: steps.sync.outputs.has_new_commits == 'false'
      run: echo "There were no new commits."

    - name: Show value of 'has_new_commits'
      run: echo ${{ steps.sync.outputs.has_new_commits }}

    - name: Install latest mdbook
      run: |
        tag=$(curl 'https://api.github.com/repos/rust-lang/mdbook/releases/latest' | jq -r '.tag_name')
        url="https://github.com/rust-lang/mdbook/releases/download/${tag}/mdbook-${tag}-x86_64-unknown-linux-gnu.tar.gz"
        mkdir mdbook
        curl -sSL $url | tar -xz --directory=./mdbook
        echo `pwd`/mdbook >> $GITHUB_PATH
    - name: Build Book
      run: |
        # This assumes your book is in the root of your repository.
        # Just add a `cd` here if you need to change to another directory.
        mdbook build
    - uses: JamesIves/github-pages-deploy-action@4.1.7
      with:
        branch: gh-pages # The branch the action should deploy to.
        folder: book # The folder the action should deploy.
```

Note that the above is configured to run on a [`schedule`](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#schedule), so GitHub Actions will fire once a day to check if there were any updates in the upstream repository that we may want to sync.

## Results

Since I wrote about ["Peeling the MongoDB Drivers Onion"]({% post_url 2024-05-17-peeling-the-mongodb-drivers-onion %}) I wanted this to be included in the book as well, so this was included as the [`source/README.md`](https://github.com/alexbevi/specifications/blob/mkbook/source/README.md) file. The rest of the contents of the specification repository were untouched and are just being rendered by `mdBook`.

If you want to explore MongoDB's Driver Specifications, you can now just click on through to [alexbevi.com/specifications](https://alexbevi.com/specifications/) (or select "Specifications" from the menu) and explore these to your heart's content :)

