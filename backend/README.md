# Usage: dev-playground.py

## Grab a competition and save dump to a JSON file

**Usage**

```
$ python dev-playground.py grabc --help
usage: dev-playground.py grabc [-h] [-i UUID] [-o OUT]

options:
  -h, --help            show this help message and exit
  -i UUID, --uuid UUID  Scrape competition and save as JSON
  -o OUT, --out OUT     Specify path for output
```

**Example:**

```sh
python dev-playground.py grabc --uuid 718b3256-e778-4003-88e9-832c4aad0cc2 --out dump.json
```


## Run remaining test code

```sh
python dev-playground.py
```