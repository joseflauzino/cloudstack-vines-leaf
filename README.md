# CloudStack/Vines Leaf [![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=joseflauzino_cloudstack-vines-leaf&metric=ncloc)](https://sonarcloud.io/dashboard?id=joseflauzino_cloudstack-vines-leaf) ![GitHub language count](https://img.shields.io/github/languages/count/joseflauzino/cloudstack-vines-leaf.svg) ![GitHub top language](https://img.shields.io/github/languages/top/joseflauzino/cloudstack-vines-leaf.svg)

Leaf is a VNF-ExP (Virtualized Network Function - Execution Platform). Basically, it is a specialized host (virtual machine) to execute Network Functions (network softwares) in order to compose full VNF instances.

This repository is part of an unofficial CloudStack project called Vines. You can read more about Leaf and Vines by visiting the project's [website](https://www.inf.ufpr.br/jwvflauzino/vines).  

## Installation

Step 1 - Clone this repository.

	# git clone https://github.com/joseflauzino/cloudstack-vines-leaf.git

Step 2 - Go to the directory.

	# cd cloudstack-vines-leaf

Step 3 - Run the installation script as root.

For Ubuntu run the `install.sh` script:

	# chmod +x install.sh
	# sh install.sh

For Alpine - run the `install-for-alpine.sh` script

	# chmod +x install-for-alpine.sh
	# sh install-for-alpine.sh

## Administration

For learn about how to manage the Vines Leaf, see:

[ADMIN-GUIDE-FOR-UBUNTU.md](ADMIN-GUIDE-FOR-UBUNTU.md)

[ADMIN-GUIDE-FOR-ALPINE.md](ADMIN-GUIDE-FOR-ALPINE.md)