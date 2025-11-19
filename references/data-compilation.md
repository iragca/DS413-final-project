This document discusses how the compilation of MegaPlant was done


# Datasets


## DiaMOS 

Sourced from here https://zenodo.org/records/5557313. DOI: 10.3390/agronomy11112107

We only take the images found under leaves/.


```bash
.
├── annotations
├── leaves
│   ├── curl        # unhealthy
│   ├── healthy     # healthy
│   ├── slug        # unhealthy
│   └── spot        # unhealthy
├── fruits
└── data
```

## PlantDoc

Sourced from here https://www.kaggle.com/datasets/nirmalsankalana/plantdoc-dataset. DOI: 10.1145/3371158.3371196

We classify folders and their files as unhealthy, when their name contains these keywords (case-insensitive):

- rust
- scab
- spot
- blight
- rot
- mold
- mildew

```bash
.
├── test
│   └── ...             # Desired data
├── train
│   └── ...             # Desired data
├── file_renamer.py
└── folder_renamer.py
```

## PlantVillage

Sourced from here https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset. DOI: 10.3389/fpls.2016.01419

- rust
- scab
- spot
- blight
- rot
- mold
- mildew
- measles
- mites

```bash
.
├── color
│   └── ...             # Desired data
├── grayscale
└── segmented
```