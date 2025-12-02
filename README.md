# msdk-py

CLI tool for Maxim SDK project management.

Create projects and run build/utility tasks from the command line.

## Requirements

- Python >=3.12
- MaximSDK installed (see [here](https://github.com/analogdevicesinc/msdk?tab=readme-ov-file#installation) for installation guide)
- `MAXIM_PATH` environment variable set (ideally put in `~/.bashrc` or `~/.zshrc`; see [here](https://github.com/analogdevicesinc/msdk?tab=readme-ov-file#environment-setup-command-line))

## Installation

> [!WARNING]  
> Release v1.0.0 pending! See [CONTRIBUTING.md](./CONTRIBUTING.md) for dev installation

Install the `msdk` (not `msdk-py`) command globally.

With uv:

```bash
uv tool install msdk-py
```

OR with pipx (install with `python3 -m pip install --user pipx && python3 -m pipx ensurepath`):

```bash
pipx install msdk-py
```

## Usage

### Create Project

Basic example:

```bash
# Creates project `./my_proj` for MAX32655 target with default `Hello_World` template
# Note: you may use '32655' instead to implicitly specify MAX32655
msdk-py init my_proj -t MAX32655
```

Working with VSCode:

```bash
msdk-py init gpio_test -t 32655 --template GPIO --vscode
```

Specify alternative Board Support Package (BSP) (default is `EvKit_V1`):

```bash
msdk-py init sensor_project -t 32655 --bsp FTHR_Apps_P1 --template I2C
```

> [!NOTE]  
> Template names match SDK directory structure. Common examples include `Hello_World`, `GPIO`, `I2C`.
> Check `$MAXIM_PATH/Examples/{TARGET}/` for complete list.

### Supported Targets

Any target in your MaximSDK installation, e.g., `MAX32520`, `MAX32650`, `MAX32655`, ...

## License

[Apache 2.0](./LICENSE)

## Contributing

Feel free to contribute!

See [CONTRIBUTING.md](./CONTRIBUTING.md) for information.
