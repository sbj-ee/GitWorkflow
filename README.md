# Git Workflow Best Practices

A practical guide to a clean, collaborative Git workflow: how to branch, how to
use pull requests, and how to keep history readable — including the difference
between a **rebase** and a **fast-forward**.

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [Branching](#branching)
3. [Pull Requests](#pull-requests)
4. [Rebase vs. Fast-Forward](#rebase-vs-fast-forward)
5. [Quick Reference](#quick-reference)

---

## Core Principles

- **`main` is always releasable.** Never commit directly to `main`; every change
  arrives through a reviewed pull request.
- **Branches are short-lived.** Open a branch, ship it, delete it. Long-running
  branches drift and cause painful merges.
- **Commits are small and atomic.** Each commit should do one thing and have a
  message that explains *why*, not just *what*.
- **Keep history readable.** A linear, intentional history is far easier to
  bisect, revert, and review than a tangle of merge commits.

---

## Branching

### Naming convention

Use a `type/short-description` pattern so branches sort and read well:

```
feature/user-login
fix/null-pointer-on-checkout
chore/bump-dependencies
docs/api-readme
```

### Everyday branching commands

```bash
# Start from an up-to-date main
git checkout main
git pull origin main

# Create and switch to a new branch
git checkout -b feature/user-login

# ... make changes ...
git add .
git commit -m "Add email/password login form"

# Push the branch and set its upstream
git push -u origin feature/user-login
```

### Keeping your branch current

While you work, `main` keeps moving. Refresh your branch regularly so the final
merge is boring (which is what you want):

```bash
git checkout feature/user-login
git fetch origin
git rebase origin/main      # replay your work on top of the latest main
```

> **Rule of thumb:** rebase your *own* unpushed/feature work to keep it tidy;
> never rebase commits that other people have already pulled.

---

## Pull Requests

Pull requests (PRs) are where code gets reviewed, discussed, and verified by CI
before it touches `main`.

### A good PR workflow

1. **Push your branch** and open a PR against `main`.
2. **Write a clear description** — what changed, why, and how to test it.
3. **Keep it small.** A PR under ~400 lines gets reviewed faster and better.
4. **Let CI run.** Tests and linters must be green before review.
5. **Address feedback** with additional commits (easy to review), then squash on
   merge if you want a single clean commit.
6. **Merge, then delete the branch.**

### Opening a PR from the command line

Using the GitHub CLI ([`gh`](https://cli.github.com/)):

```bash
gh pr create \
  --base main \
  --head feature/user-login \
  --title "Add email/password login" \
  --body "Adds a login form and session handling. Closes #42."
```

### Example PR description template

```markdown
## What
Adds email/password login with server-side session handling.

## Why
Users currently have no way to authenticate. Closes #42.

## How to test
1. Run `npm start`
2. Visit /login and sign in with a seeded account
3. Confirm you're redirected to /dashboard

## Notes
- Passwords are hashed with bcrypt (cost 12).
```

### Merge strategies at a glance

| Strategy           | Result                                  | Best for |
| ------------------ | --------------------------------------- | -------- |
| **Squash & merge** | All PR commits collapse into one        | Most feature work — keeps `main` clean |
| **Rebase & merge** | Commits replayed onto `main`, no merge commit | Preserving a curated commit-by-commit history |
| **Merge commit**   | Explicit merge commit ties the branch in | Long-lived branches where you want the merge recorded |

---

## Rebase vs. Fast-Forward

These two often get confused because both can produce a **linear history** — but
they answer different questions.

- **Fast-forward** is a kind of *merge*: "can I move the branch pointer forward
  without creating a merge commit?"
- **Rebase** *rewrites* commits: "replay my commits as if I had started from a
  different base."

### Fast-Forward

A fast-forward happens when the target branch has **no new commits** since you
branched off it. There's nothing to reconcile, so Git just slides the branch
pointer forward. **No merge commit is created.**

![Fast-forward merge diagram](./ff-merge.png)

```bash
# main is still at B; feature added C, D, E on top of B
git checkout main
git merge feature        # fast-forward: 'main' label simply moves to E
```

History stays a single straight line — as if the feature commits had been made
on `main` all along.

To *force* a merge commit even when a fast-forward is possible (some teams prefer
this so every merge is recorded):

```bash
git merge --no-ff feature
```

### Rebase

Rebase is for when `main` **has** moved on while you were working. Instead of
creating a merge commit, rebase takes your commits, sets them aside, fast-forwards
your branch to the latest `main`, and then **replays your commits on top** —
giving each a *new hash* (so `C` becomes `C'`).

![Rebase diagram](./rebase.png)

```bash
# main advanced to G (commits F, G) while you built C, D on feature
git checkout feature
git rebase main          # replays C, D as C', D' on top of G
```

The result is a clean, linear history with no merge bubble — as though you had
branched from `G` in the first place.

> ⚠️ **The golden rule of rebasing:** never rebase commits that have been pushed
> and that others may have based work on. Rebasing rewrites history, and shared
> rewritten history forces everyone else into painful conflicts. Rebase local /
> feature-only work; merge shared work.

### Side-by-side summary

| | Fast-forward | Rebase |
| --- | --- | --- |
| **What it does** | Moves the branch pointer forward | Replays commits onto a new base |
| **Creates a merge commit?** | No | No |
| **Rewrites history (new hashes)?** | No | **Yes** |
| **Possible when…** | Target branch has no new commits | Always (resolves divergence) |
| **Use it to…** | Integrate a branch that's strictly ahead | Update a branch whose base moved on |
| **Safe on shared branches?** | Yes | **No** — only on local/unshared commits |

---

## Quick Reference

```bash
# Branch
git checkout -b feature/x          # create + switch
git push -u origin feature/x       # publish

# Stay current
git fetch origin
git rebase origin/main             # replay your work on latest main

# Integrate
git merge feature                  # fast-forward when possible
git merge --no-ff feature          # always make a merge commit
git rebase main                    # linearize before merging

# Open a PR
gh pr create --base main --fill

# Clean up after merge
git branch -d feature/x            # delete local
git push origin --delete feature/x # delete remote
```

---

*Diagrams (`ff-merge.png`, `rebase.png`) are generated by `make_diagrams.py`.*
