# cads

Parametric CAD parts. Each part is a [build123d](https://github.com/gumyr/build123d) script, and the matching STEP file is generated from that script.

Open a `.step` file in a CAD program, or regenerate it from the script. To add a part, describe it in this repository. The agent follows `AGENTS.md` and writes the script and the STEP file.

Units are millimeters. The Python file is the source. Regenerate the STEP file from the script.

## Get the repository

```sh
git clone https://github.com/teyd/cads.git
cd cads
```

## Install mise

[mise](https://mise.jdx.dev/) installs the Python and uv versions in `mise.toml`.

macOS or Linux:

```sh
curl -fsSL https://mise.run | sh
```

Homebrew:

```sh
brew install mise
```

Windows: `winget install jdx.mise`.

The installer puts mise at `~/.local/bin/mise`. If your shell cannot find it, use that path, or activate mise once:

```sh
echo 'eval "$(~/.local/bin/mise activate zsh)"' >> "${ZDOTDIR:-$HOME}/.zshrc"
```

Open a new terminal after that. Homebrew users write `mise` instead of `~/.local/bin/mise`. Other shells are in the [mise shell setup](https://mise.jdx.dev/shell-setup.html).

## Install this project's tools

From the repository root, after reading `mise.toml`:

```sh
mise install
mise exec -- uv sync
```

`mise install` installs Python 3.13 and uv. `uv sync` installs build123d into `.venv`. If mise asks you to trust this project, run `mise trust`.

Activation is optional. Without it, run project commands through `mise exec --`.

## Use a part

STEP files are in `parts/`. Open one directly, or regenerate it:

```sh
mise exec -- uv run python parts/flat-ring/flat-ring.py
```

A valid STEP file is text and starts with `ISO-10303-21`.

| Part | Description |
| --- | --- |
| [flat-ring](parts/flat-ring/) | Annulus, 150 mm outer diameter, 60 mm inner diameter, 10 mm thick |

```text
parts/<name>/<name>.py
parts/<name>/<name>.step
```

The folder name says what the part is. Dimensions stay in the script, so a size change does not force a rename. `flat-ring` is a name. `ring-150x60x10` is not.

## License

This repository does not have a license yet. Until you add one, others cannot tell whether they may reuse the models.
