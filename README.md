**[shmd](https://github.com/examesh/shmd)** creates markdown API documentations from shell script annotations.


## Usage

```shell
$ shmd

shmd <src_dir> <dst_file> [<black_files>]

  src_dir     = Source directory with shell files
  dst_file    = Destination (markdown) file
  black_files = Skip these comma separated src files

  export $SHMD_PAT to match other source files than *.sh

  Examples:
    ./shmd ~/foo ~/api.md
    ./shmd ~/foo ~/api.md cfg.sh,main.sh
    SHMD_PAT='*_*.sh' ./shmd ~/foo ~/api.md
```


## Installation

#### Linux x86-64 Binary

The `dist/` folder contains a ready to use Linux x86-64 binary created with [pyinstaller](http://www.pyinstaller.org/). BUT: Cause of (glibc) library incompatibilities it doesn't work with all distributions. If you get execution errors, you can compile the binary by yourself with the included `dist/build.sh` (see the next section).

```shell
# try shmd binary
cd /usr/local/bin
sudo curl --fail -L -o shmd https://raw.githubusercontent.com/examesh/shmd/master/dist/shmd.linux_x86-64
sudo chmod 755 shmd
./shmd -h
```


#### Python

[shmd](https://github.com/examesh/shmd) is a [Python 3](https://www.python.org) application without external package dependencies.

```shell
mkdir -p ${HOME}/tmp
cd ${HOME}/tmp
git clone https://github.com/examesh/shmd.git
cd shmd
python shmd.py # successfully tested with Python 3.7.6
```

To create the Linux x86-64 binary you need to install [pyinstaller](http://www.pyinstaller.org/).

```shell
pip install pyinstaller   # successfully tested with pyinstaller 3.5 and Python 3.7.6
cd ${HOME}/tmp/shmd/dist
./build.sh                # needs pyinstaller
./shmd.linux_x86-64 -h
```



## Annotations

`shmd` supports the following annotation tags:

| Tag | Description | Optional | Multiple allowed? |
|---- |------------ |--------- |------------------ |
| `##C` | Command Usage | Yes | No |
| `##D` | Description | Yes | Yes |
| `##A` | Argument | Yes | Yes |
| `##E` | Example | Yes | Yes |


## Example

```shell
cd /tmp
mkdir shmd_demo

# create annotated shell functions
cat << 'EOF' > shmd_demo/foobar.sh
# function names MUST be at beginning of line
foo() {  
  ##C <arg1> [<arg2>]
  ##D This is the description of the `foo()` function.
  ##D Description supports multiple lines and markdown tags.
  ##A arg1 = Description of the first (mandatory) parameter
  ##A arg2 = Description of the second (optional) parameter
  ##E foo bar
  ##E foo bar1 bar2
  local arg1="${1}"
  local arg2="${2:-}"
  echo "First paramter: ${arg1}"
  [ -z "${arg2}" ] || echo "Second parameter: ${arg2}"
}
bar() {
  echo "All annotations are optional"
}
EOF

# create API documentation
./shmd ./shmd_demo ./api.md
```

**Result**, saved in `api.md`:

<p align="center">
<img src="https://raw.githubusercontent.com/examesh/shmd/master/shmd.png" width=600px>
</p>

<br><br>
<sub>[Powered by ExaMesh](https://examesh.de)</sub>
