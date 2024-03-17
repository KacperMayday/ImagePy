# ImagePy

## About

ImagePy is a GUI utility tool for performing basic image analysis. It was developed as part of Image processing algorithms
(pl: Algorytmy przetwarzania obrazów) subject during the third year of Computer Science
studies. The tool is implemented in Python 3.12 with minimal external dependencies.

## Installation

For now, application is not published on https://pypi.org/, so it has to be installed manually from this repository.

Inside your virtual environment:

1. Clone the repository: `git clone https://github.com/KacperMayday/ImagePy.git`
2. Install Python package: `pip install imagepy`
3. Run: `imagepy`

Check [Usage](#usage) section to see how to compile and execute application as `.exe` file.

## Documentation

Documentation was uploaded as PDF file in `docs/` in this repository. Documentation is written in Polish, but has
lots of screenshots which may be helpful. If you encounter any problems, check [FAQ](#faq) section or report an Issue.

## Usage

It is recommended to use [make](https://www.gnu.org/software/make/) to get started. If you do not have make or do not
want to use it, you may invoke all commands manually in your local Python environment.

### Compile to EXE file

Compilation to executable file is done with [PyInstaller](https://pypi.org/project/pyinstaller/). Compilation
configuration is in `imagepy/app.spec` file.

#### Using make (recommended)

1. Run: `make build`
2. Compiled EXE file will be saved in newly created `dist/` directory.

#### Manual setup

1. Install build dependencies: `pip install imagepy[pyinstaller]`
2. Compile EXE file: `pyinstaller imagepy/app.spec`
3. Compiled EXE will be saved in newly created `dist/` directory.

### Development setup

Development setup consists of installing external dependencies, linters, pre-commit setup.

#### Using make (recommended)

1. Create development virtual environment: `make install-dev`
2. Just before committing your changes run: `make lint`

## FAQ

#### 1. I open an image, select one of the options and nothing happens. Is this a correct behaviour?

Yes, some options aren't applicable for every image format. Currently, all options are available for users to select,
regardless image attributes, but clicking them has no effect (i.e. binary operations will not work when selected image
is in RGB colorscale). Refer to the documentation which options are available for your image format.

#### 2. When invoking `pyinstaller` on Windows I get an alert about a virus:

Sometimes PyInstaller conflicts with Windows antivirus software. To solve this issue, add your project directory as an
exception in Windows Security component.
Reference:
https://stackoverflow.com/questions/77266764/i-get-a-virus-alert-when-i-convert-my-py-file-into-an-exe-file-how-do-i-fix-i

#### 3. EXE file created on one machine does not work on another one:

Executable file created with PyInstaller is platform dependent. This means that if you create an `.exe` file on Windows
machine, it won't work on Linux. For each platform you need to create separate EXE file.
