# Repository setup (maintainers)

These are one-time steps for `github.com/bigantal/cistercian`. For a fork or a renamed repository, replace the owner and repository name throughout.

## 1. Enable GitHub Pages through Actions

1. Go to **Settings → Pages → Build and deployment → Source** and choose **GitHub Actions**.
2. Open **Settings → Environments → `github-pages`**. GitHub creates this environment on the first deployment.
   - Under deployment branches, allow only **`main`**.
   - Leave the environment without secrets; none are needed.

From the command line:

```bash
gh api -X POST repos/bigantal/cistercian/pages -f build_type=workflow
```

## 2. Protect `main`

Go to **Settings → Rules → Rulesets** (or **Branches**) and add a rule for `main` that:

- requires a pull request before merging;
- requires these status checks to pass:
  - `Judge + Python 3.10`
  - `Judge + Python 3.13`
  - `TypeScript conformance (Node 20.19)`
  - `TypeScript conformance (Node 24)`
  - `Java conformance (JDK 25)`
  - `Website tests + build`
- blocks force pushes and deletion.

## 3. Restrict Actions for outside contributors

1. Under **Settings → Actions → General → Fork pull request workflows**, require approval for first-time contributors, or for all outside collaborators.
2. Under **Workflow permissions**, select **Read repository contents permission**. Each workflow already declares the minimum permissions it needs; this setting is a second safeguard.

## 4. First deployment

Push or merge to `main`. The **Deploy website** workflow then:

1. runs the complete test workflow on that commit;
2. builds `web/` and uploads `web/dist` as the Pages artifact;
3. deploys it.

If any test job fails, nothing is deployed. You can also start a run by hand from the Actions tab using **Run workflow**.

The site URL is **https://bigantal.github.io/cistercian/**.

## 5. Smoke check after each deployment

Open the site URL. Then:

1. Check that the page loads with no console errors and shows **1986** by default.
2. Compare the 1986 glyph with `docs/example-1986.svg`:
   - a detached stroke on the upper right;
   - a hook joined to the stem on the upper left;
   - a closed square on the lower right;
   - a bar on the lower left.
3. Click **7085**. The glyph should match King's printed example, which is also in `docs/digit-chart.svg`.
4. Type `0`, then `10000`, then `abc`. Each should show an error message and dim the result.
5. Open **JSON geometry**. It should show a single-line `{"segments":…}` object.
6. Narrow the window to phone width. The layout should become a single column, with no horizontal scrolling.

The deployed files use relative paths only, so they keep working if the repository is renamed.

## Updating pinned actions

The workflows pin every action to a full commit SHA, with the version as a comment. To update one:

```bash
gh api repos/actions/checkout/releases/latest --jq .tag_name
gh api repos/actions/checkout/commits/<tag> --jq .sha
```
