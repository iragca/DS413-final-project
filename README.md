<h1 align="center">MegaPlant</h1>

<p align="center">
<a href="https://iragca.github.io/DS413-final-project/">
<img src="https://img.shields.io/badge/Research-Paper-darkgreen?logo=paperswithcode"/>
<a href="https://huggingface.co/datasets/chrisandrei/MegaPlant">
<img src="https://img.shields.io/badge/HuggingFace-Dataset-blue?logo=huggingface"/>
</p>

---

A consolidated leaf-image dataset designed to support plant disease classification models that generalize across diverse environmental conditions, from controlled laboratory settings to highly variable in-field scenarios. MegaPlant integrates multiple publicly available datasets and standardizes them into a unified taxonomy of healthy and diseased leaf categories, enabling robust training across modalities.

## Datasets integrated

| Dataset      | Authors                                   | Description                                                 | Retrieved from                                                   |
| ------------ | ----------------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------- |
| PlantVillage | https://doi.org/10.48550/arXiv.1511.08060 | Laboratory conditions, small images                         | https://www.kaggle.com/datasets/nirmalsankalana/plantdoc-dataset |
| PlantDoc     | https://doi.org/10.1145/3371158.3371196   | Field and laboratory conditions, stock-photos, small images | https://www.kaggle.com/datasets/nirmalsankalana/plantdoc-dataset |
| DiaMOS       | https://doi.org/10.3390/agronomy11112107  | Field conditions, large high quality images                 | https://zenodo.org/records/5557313                               |

## Citation

If you use this dataset, please cite it as below.

```cff
@misc{Irag_MegaPlant_An_integrated,
author = {Irag, Chris Andrei and Pramio, Ashley and Mendoza, Monique Antoinette and Dela Vega, Rod Vincent},
title = {{MegaPlant: An integrated image classification dataset of laboratory and field images}},
url = {https://iragca.github.io/DS413-final-project/}
}
```

## Setup

We recommend working inside an [IDE](https://en.wikipedia.org/wiki/Integrated_development_environment) like [Visual Studio Code](https://code.visualstudio.com/) or [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/) as you need to clone the [github repository](https://github.com/iragca/DS413-final-project) for this project.

We work with uv. You can install it [here](https://docs.astral.sh/uv/guides/install-python/)

```bash
make requirements   #  Install dependencies
```

## Dataset Manager

```bash
make data           #  Run the CLI dataset manager
```

Functionalities

- Download datasets
- Deduplicated files
- Splitting the MegaPlantDataset

### How to Navigate

| Keybind      | Functionality                |
| ------------ | ---------------------------- |
| `Ctrl+C`     | Quit the app or current menu |
| `Arrow Keys` | Navigate choices             |
