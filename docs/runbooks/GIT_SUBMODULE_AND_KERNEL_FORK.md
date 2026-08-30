# Armbian Submodule and Orange Pi Kernel Fork

- Last verified: 2026-08-30 after migration
- Workstation: `/home/artm1904/Program/Robot`
- Organization: `robotics-lab-1904`
- Superproject: `robotics-lab-workspace`

## Purpose

This runbook documents the completed repository layout and its ongoing
submodule workflow. Migration-only commands are retained for historical
recovery and are explicitly marked as legacy.

The intended result is:

```text
robotics-lab-workspace/                 Git superproject
└── third_party/
    ├── armbian-build/                  Git submodule
    └── linux-orangepi-sun60iw2/        Git submodule pointing to our fork
```

A submodule does not copy another repository's files into the superproject
history. The superproject records the submodule URL and one exact commit ID.
The optional branch entry in `.gitmodules` only supplies the default branch for
`git submodule update --remote`; it does not replace the pinned commit.

## Verified initial state

> Historical migration state: the paths in this section refer to the legacy
> `/home/artm1904/Program/Robot/os` tree and must not be used as current
> workspace paths.

The following facts were observed locally before writing this runbook:

| Repository | Branch | Commit | Local changes |
|---|---|---|---|
| `robotics-lab-workspace` | `main` | `5f5ac26` | Clean |
| `os/build` | `main` | `de5fd0a` | Two modified tracked files |
| `os/linux-orangepi-sun60iw2` | `orange-pi-6.6-sun60iw2` | `8a9be72` | Three modified files and new `ov5647.c` |

The Armbian changes are in:

- `config/kernel/linux-sun60iw2-vendor.config`
- `patch/kernel/archive/sun60iw2-opi-vendor/0005-cubie-a7z-add-device-tree.patch`

The kernel changes are in:

- `arch/arm64/boot/dts/allwinner/sun60i-a733-orangepi-zero3w.dts`
- `bsp/drivers/vin/modules/sensor/Kconfig`
- `bsp/drivers/vin/modules/sensor/Makefile`
- `bsp/drivers/vin/modules/sensor/ov5647.c` (new)

Do not delete, replace, re-clone, or forcibly check out either existing working
tree before completing the preservation steps below.

## Terminology and remote policy

- **Superproject:** `robotics-lab-workspace`, which records submodule commits.
- **Fork:** a GitHub repository in `robotics-lab-1904` connected to its original.
- **origin:** a repository owned by `robotics-lab-1904`, where our branches are
  pushed.
- **upstream:** the original third-party repository, used to fetch vendor work.

For the kernel, the desired remotes are:

```text
origin    https://github.com/robotics-lab-1904/linux-orangepi.git
upstream  https://github.com/orangepi-xunlong/linux-orangepi.git
```

## Phase 1: Create recoverable backups

> Legacy recovery procedure only. The active repositories now live under the
> superproject paths documented in `docs/agent-context/PROJECT_MAP.md`.

Run on the workstation. These commands do not modify either repository.

```bash
mkdir -p /home/artm1904/Program/Robot/repository-migration-backup

git -C /home/artm1904/Program/Robot/os/build \
  diff --binary > /home/artm1904/Program/Robot/repository-migration-backup/armbian-build-working-tree.patch

git -C /home/artm1904/Program/Robot/os/build \
  status --porcelain=v1 > /home/artm1904/Program/Robot/repository-migration-backup/armbian-build-status.txt

git -C /home/artm1904/Program/Robot/os/linux-orangepi-sun60iw2 \
  diff --binary > /home/artm1904/Program/Robot/repository-migration-backup/linux-orangepi-working-tree.patch

cp --preserve=mode,timestamps \
  /home/artm1904/Program/Robot/os/linux-orangepi-sun60iw2/bsp/drivers/vin/modules/sensor/ov5647.c \
  /home/artm1904/Program/Robot/repository-migration-backup/ov5647.c

git -C /home/artm1904/Program/Robot/os/linux-orangepi-sun60iw2 \
  status --porcelain=v1 > /home/artm1904/Program/Robot/repository-migration-backup/linux-orangepi-status.txt
```

`git diff` does not include untracked files, which is why `ov5647.c` is copied
separately.

Verify the backup:

```bash
ls -lh /home/artm1904/Program/Robot/repository-migration-backup
sha256sum /home/artm1904/Program/Robot/repository-migration-backup/*
```

Keep this directory outside all repositories until the migration has been
cloned and validated independently.

## Phase 2: Create the kernel fork on GitHub

**Completed:** the fork is available at
`https://github.com/robotics-lab-1904/linux-orangepi`.

Open the upstream repository:

```text
https://github.com/orangepi-xunlong/linux-orangepi
```

Select **Fork**, choose `robotics-lab-1904` as the owner, and create the fork.
The conventional fork name is `linux-orangepi`. If GitHub permits and you prefer
the local platform-specific name, `linux-orangepi-sun60iw2` is also acceptable;
use the actual resulting URL in all commands below.

Do not select “copy the default branch only” if the UI offers that option. The
required source branch is `orange-pi-6.6-sun60iw2`, which may not be upstream's
default branch.

GitHub CLI is not currently installed on the workstation, so the web workflow
is the simplest option. Installing `gh` is not required for this migration.

## Phase 3: Preserve and publish the kernel changes

**Completed:** the published branch is `robotics/ov5647-sun60iw2`, and the
superproject currently pins commit `4590a2f8f1905931e6ca943d124d9f773df7cb52`.

The current checkout has the upstream repository named `origin`. Rename that
remote, then add the fork as the new `origin`:

```bash
cd /home/artm1904/Program/Robot/os/linux-orangepi-sun60iw2

git remote rename origin upstream
git remote add origin https://github.com/robotics-lab-1904/linux-orangepi.git
git remote -v
```

If the fork has a different name, replace the `origin` URL accordingly.

Create a dedicated branch without changing the current working files:

```bash
git switch -c robotics/ov5647-sun60iw2
git status --short
git diff --check
```

Review before staging:

```bash
git diff -- arch/arm64/boot/dts/allwinner/sun60i-a733-orangepi-zero3w.dts
git diff -- bsp/drivers/vin/modules/sensor/Kconfig
git diff -- bsp/drivers/vin/modules/sensor/Makefile
sed -n '1,240p' bsp/drivers/vin/modules/sensor/ov5647.c
```

Stage only the known OV5647 files:

```bash
git add \
  arch/arm64/boot/dts/allwinner/sun60i-a733-orangepi-zero3w.dts \
  bsp/drivers/vin/modules/sensor/Kconfig \
  bsp/drivers/vin/modules/sensor/Makefile \
  bsp/drivers/vin/modules/sensor/ov5647.c

git diff --cached --check
git diff --cached --stat
git status --short
```

Commit and publish the branch:

```bash
git commit -m "media: sunxi-vin: add OV5647 support for Orange Pi Zero 3W"
git push -u origin robotics/ov5647-sun60iw2
```

Verify that the commit exists remotely:

```bash
git ls-remote --heads origin robotics/ov5647-sun60iw2
git rev-parse HEAD
```

The hashes printed by these commands must match.

## Phase 4: Preserve the Armbian changes

**Selected model:** Model B. The active submodule points directly to upstream
`armbian/build`; the customization is versioned at
`patches/armbian/0001-enable-ov5647-sun60iw2.patch` and applied with
`bash patches/armbian/apply_patch.sh`. Use `--check` to validate without
modifying the submodule.

The Armbian checkout cannot be replaced by a clean submodule while its two local
changes are uncommitted. Choose one of the following models.

### Model A — recommended: fork Armbian and submodule the fork

Use this when the Armbian configuration and patch are part of the maintained
build workflow. Fork `https://github.com/armbian/build` into
`robotics-lab-1904`, then run:

```bash
cd /home/artm1904/Program/Robot/os/build

git remote rename origin upstream
git remote add origin https://github.com/robotics-lab-1904/build.git
git switch -c robotics/ov5647-sun60iw2

git add \
  config/kernel/linux-sun60iw2-vendor.config \
  patch/kernel/archive/sun60iw2-opi-vendor/0005-cubie-a7z-add-device-tree.patch

git diff --cached --check
git commit -m "build: enable OV5647 for sun60iw2 vendor kernel"
git push -u origin robotics/ov5647-sun60iw2
```

The main workspace will then submodule your fork and pin this exact commit.

### Model B — upstream submodule plus a versioned patch

Use this when you want `third_party/armbian-build` to point directly to
`armbian/build` and prefer to maintain only a small patch in the superproject.

First create a patch that includes the two tracked changes:

```bash
mkdir -p /home/artm1904/Program/Robot/robotics-lab-workspace/patches/armbian

git -C /home/artm1904/Program/Robot/os/build diff --binary \
  > /home/artm1904/Program/Robot/robotics-lab-workspace/patches/armbian/0001-enable-ov5647-sun60iw2.patch
```

After adding the clean upstream submodule, apply it with:

```bash
git -C third_party/armbian-build apply --check ../../patches/armbian/0001-enable-ov5647-sun60iw2.patch
git -C third_party/armbian-build apply ../../patches/armbian/0001-enable-ov5647-sun60iw2.patch
```

Model B deliberately leaves the submodule dirty after applying the patch. A
small wrapper script should perform the apply step before every clean build.
Model A is easier for agents and continuous integration because the submodule
itself is clean and points to a buildable commit.

## Phase 5: Add clean submodules to the main workspace

**Completed:** all four submodules are registered in `.gitmodules`.

Only perform this phase after the relevant commits are available on GitHub.
Do not move the existing 3.1 GiB and 2.3 GiB working trees into the main
repository. Add fresh submodule checkouts instead.

```bash
cd /home/artm1904/Program/Robot/robotics-lab-workspace
mkdir -p third_party
```

For recommended Model A:

```bash
git submodule add \
  -b robotics/ov5647-sun60iw2 \
  https://github.com/robotics-lab-1904/build.git \
  third_party/armbian-build

git submodule add \
  -b robotics/ov5647-sun60iw2 \
  https://github.com/robotics-lab-1904/linux-orangepi.git \
  third_party/linux-orangepi-sun60iw2
```

For Model B, replace the first command with:

```bash
git submodule add \
  -b main \
  https://github.com/armbian/build.git \
  third_party/armbian-build
```

Inspect exactly what the superproject will record:

```bash
cat .gitmodules
git submodule status
git diff --submodule=log --cached
git status --short
```

Then commit the submodule metadata and pinned commits:

```bash
git add .gitmodules third_party/armbian-build third_party/linux-orangepi-sun60iw2
git commit -m "build: add pinned Armbian and Orange Pi kernel submodules"
git push origin main
```

## Phase 6: Validate with a clean clone

This remains the required final validation after repository documentation and
submodule pins are updated.

Do not consider the migration complete until a second clone works without using
either old checkout:

```bash
cd /tmp
git clone --recurse-submodules \
  https://github.com/robotics-lab-1904/robotics-lab-workspace.git \
  robotics-lab-workspace-validation

git -C /tmp/robotics-lab-workspace-validation submodule status --recursive
git -C /tmp/robotics-lab-workspace-validation status --short
```

For Model A, both commands should show initialized submodules and a clean
working tree. Verify the expected source files and configuration:

```bash
test -f /tmp/robotics-lab-workspace-validation/third_party/linux-orangepi-sun60iw2/bsp/drivers/vin/modules/sensor/ov5647.c

rg -n 'CONFIG_SENSOR_OV5647' \
  /tmp/robotics-lab-workspace-validation/third_party/armbian-build/config/kernel/linux-sun60iw2-vendor.config
```

For Model B, apply the tracked Armbian patch after cloning, then validate it with
`git diff --check` inside the submodule.

## Daily submodule workflow

Clone everything:

```bash
git clone --recurse-submodules \
  https://github.com/robotics-lab-1904/robotics-lab-workspace.git
```

Initialize submodules in an existing clone:

```bash
git submodule update --init --recursive
```

After pulling the superproject, check out its recorded commits:

```bash
git pull --ff-only
git submodule update --init --recursive
```

Work on the kernel fork from a submodule checkout:

```bash
cd third_party/linux-orangepi-sun60iw2
git switch robotics/ov5647-sun60iw2
git pull --ff-only origin robotics/ov5647-sun60iw2
```

After committing and pushing a new kernel commit, update the superproject pin:

```bash
cd /home/artm1904/Program/Robot/robotics-lab-workspace
git add third_party/linux-orangepi-sun60iw2
git commit -m "build: update Orange Pi kernel submodule"
git push origin main
```

Avoid blindly running `git submodule update --remote`. Review the incoming
commit first, test it, and then commit the updated submodule pointer.

## Synchronizing forks with upstream

Fetch upstream without changing the working branch:

```bash
git fetch upstream --prune
```

Inspect divergence before integrating anything:

```bash
git log --oneline --graph --decorate --left-right \
  upstream/orange-pi-6.6-sun60iw2...robotics/ov5647-sun60iw2
```

Rebasing or merging vendor updates can conflict with the OV5647 driver, Kconfig,
Makefile, or DTS. Perform that integration as a separate documented task, build
the module and DTB, run staged camera validation, and only then update the
superproject pin.

## Rollback

Remote configuration changes can be reversed without touching commits:

```bash
git remote remove origin
git remote rename upstream origin
```

If a commit has not yet been made, the original working files remain unchanged.
If recovery is needed, use the patch and copied `ov5647.c` from
`/home/artm1904/Program/Robot/repository-migration-backup`; do not use a hard
reset while unverified work exists.

## References

- [Git submodule documentation](https://git-scm.com/docs/git-submodule)
- [GitHub: Fork a repository](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/fork-a-repo)
- [GitHub: Configure a remote for a fork](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/configuring-a-remote-repository-for-a-fork)
