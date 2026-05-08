# TokenDash Scripts

Helpers for running a local TokenDash fork without replacing the globally installed `tokendash` command.

## setup-tokendash-dev-aliases.sh

Installs two aliases into `~/.zshrc`:

```bash
build-tokendash-dev
tokendash-dev
```

`build-tokendash-dev` builds the local TokenDash repo. `tokendash-dev` runs the built local server from `dist/server/index.js`.

The global `tokendash` command is not changed.

## Usage

From inside a local `tokendash` repo:

```bash
/path/to/Scripts/tokendash/setup-tokendash-dev-aliases.sh
```

Or pass the repo path explicitly:

```bash
/path/to/Scripts/tokendash/setup-tokendash-dev-aliases.sh /path/to/tokendash
```

Then reload zsh:

```bash
source ~/.zshrc
```

Build and run the local fork:

```bash
build-tokendash-dev
tokendash-dev
```

Open:

```text
http://localhost:3456/
```

## Notes

The script is safe to run multiple times. It replaces only the block between:

```bash
# >>> tokendash-dev aliases >>>
# <<< tokendash-dev aliases <<<
```

If `Scripts` and `tokendash` are sibling folders under the same parent, the script can also infer the repo path from its own location.
