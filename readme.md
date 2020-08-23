## linuxstore

package browser for arch linux. gui for discovering and installing packages.

### install

```
python -m pip install tkinter  # usually included with python
```

### usage

```
python store.py
```

browse packages by category: essential, popular, or all.
search by name or description. click install to install with pacman.

### files

- `store.py`       : gui application
- `packages.json`  : package database
- `packages.sh`    : original bash installer
