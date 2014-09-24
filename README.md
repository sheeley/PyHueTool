# PyHueTool
Tool used to quickly identify hue lights by id in the command line.

## Install
```
pip install -r requirements.txt
```

## Usage
Automatically use first hue bridge in list:
```
python hue.py 1 --user user
```

Use specific bridge:
```
python hue.py 1 --user user --ip 10.0.0.1
```

