# moboxer

# tips for pymol

Run pymol commands

```
pymol  -cqr load_w_pymol.py 
```

To install packages llike h5py with pymol, first, find pymol exececutable:

```
$ echo "import sys; print(sys.executable)" >> find_exec.py
$ pymol -cqr find_exec.py 
PyMOL>run find_exec.py,main
/opt/homebrew/Cellar/pymol/3.1.0_1/libexec/bin/python
```

then use pip

```
/opt/homebrew/Cellar/pymol/3.1.0_1/libexec/bin/python -m pip install h5py numpy
```

