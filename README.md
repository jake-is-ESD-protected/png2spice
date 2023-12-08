# PNG2SPICE

## About
Need a reference design in LTSPICE but only have screenshots available? Manually copying is **boring**, so just use **PNG2SPICE**!

**PNG2SPICE** uses image processing and the convolutional neural network [SPICEnet](https://github.com/jake-is-ESD-protected/SPICEnet) to detect, classify and localize electrical components from an image. It is then parsed into a `.asc` file which can be opened by LTSPICE. Check out [SPICEnet](https://github.com/jake-is-ESD-protected/SPICEnet) to see which components it supports.

## Setup
```
git clone https://github.com/jake-is-ESD-protected/schematic-line-tracing
python3 -m venv .env
source ./.env/bin/activate      # for Linux
./.env/Scripts/activate         # for Windows
pip install -r requirements.txt
pip install -e .
```

## Structure


## Examples

