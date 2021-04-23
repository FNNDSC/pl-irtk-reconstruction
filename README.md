# IRTK Reconstruction

[![Version](https://img.shields.io/docker/v/fnndsc/pl-irtk-reconstruction?sort=semver)](https://hub.docker.com/r/fnndsc/pl-irtk-reconstruction)
[![MIT License](https://img.shields.io/github/license/fnndsc/pl-irtk-reconstruction)](https://github.com/FNNDSC/pl-irtk-reconstruction/blob/master/LICENSE)
[![Build](https://github.com/FNNDSC/pl-irtk-reconstruction/workflows/build/badge.svg)](https://github.com/FNNDSC/pl-irtk-reconstruction/actions?query=workflow%3Abuild)

Fetal brain MRI reconstruction using IRTK reconstruction in a _ChRIS ds_ plugin wrapper.

https://pubmed.ncbi.nlm.nih.gov/22939612/

# Usage

Quality assessment and inter-slice thickness should be defined by a .CSV file.

In the first column, the file name is specified. In the second column, the quality
score (a float between 0-1) is given. In the third column, the inter-slice thickness
in millimeters is given.

```shell
filename,quality,slice_thickness
a.nii,0.27163228,2.0
b.nii,0.7249744,2.0
c.nii,0.697088,2.0
d.nii,0.023986042,2.0
e.nii,0.849987,2.0
```

With this, the input to `pl-irtk-reconstruction` is tightly coupled to the output of
[`pl-fetal-brain-assessment`, v1.3.0](https://chrisstore.co/plugin/81).
The default input options to `pl-irtk-reconstruction` are tailored to meet the default
output names of `pl-fetal-brain-assessment`.

NOTE: the specific file path is not considered. Only the base name of the file names
listed in the .CSV are relevant. These names are matched to files discovered by the
option `--inputPathFilter`.

For an input tree like this:

```

in/
├── Best_Images_crop
│   ├── b.nii
│   ├── c.nii
│   └── e.nii
└── quality_assessment.csv
```

Command-line invocation:

```shell
singularity exec docker://fnndsc/pl-irtk-reconstruction:1.0.2 irtkrecon \
  --inputPathFilter 'Best_images_crop/*.nii' --csv 'quality_assessment.csv' \
  --output recon.nii --debug incoming/ outgoing/
```
