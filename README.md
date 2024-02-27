# lemniscat.runtime
A runtime to provide product oriented in DevOps approach

# Description

This runtime is a set of tools to provide a DevOps approach to the development of products. It is based on the following principles:
- **Product oriented**: The runtime is designed to be used in the development of products, not in the development of software. This means that the runtime is designed to be used in the development of products that are composed of software, hardware, and other components.
- **Modular**: The runtime is designed to be modular, so that it can be used in different contexts and with different tools.
- **Extensible**: The runtime is designed to be extensible, so that it can be used with different tools and in different contexts.
- **Open source**: The runtime is open source, so that it can be used and modified by anyone.
- **Community driven**: The runtime is designed to be community driven, so that it can be used and improved by a community of users and developers.
- **DevOps oriented**: The runtime is designed to be used in a DevOps approach, so that it can be used to activate all the capabilities of a DevOps Approach (code, build, test, ...).
- **CI/CD solution software agnostic**: The runtime is designed to be used with any CI/CD solution, so that it can be used with any CI/CD solution.
- **Cloud agnostic**: The runtime is designed to be used with any cloud provider, so that it can be used with any cloud provider.
- **locally executable**: The runtime is designed to be executed locally, so that it can be used in a local environment to help the development of products (for example).

## Key concepts

The runtime is based on the following key concepts:

### Capabilities

The capabilities are the DevOps steps that can be activated during the deployment of a product. It's designed to be sure that all the DevOps aspects are covered during the design of a product. For example, you need 

### Solutions

The solutions are the tools that can be used to execute the capabilities. For example, you can use Jenkins to execute the build capability, or you can use Ansible to execute the deployment capability.

### Plugins

The plugins are the tools that can be used to execute the tasks describe in the manifest file. For example, you can use the Ansible plugin to execute the deployment tasks describe in the manifest file.

### Manifest file

The manifest file is a YAML file that contains the definition of the product to deploy. It contains the variables needed to deploy the product, the capabilities that can be activated during the deployment, and the plugins needed to execute the tasks describe in the manifest file.

### Configuration files

The configuration files are the files that contain the variables needed to deploy the product. These files are used to define the variables needed to deploy the product, and to define the variables needed to execute the capabilities.
The order of the configuration files is important. The variables defined in the first configuration file can be overridden by the variables defined in the second configuration file, and so on.



# Installation

## Requirements
The runtime requires Python 3.10 or later and the following packages:
`setup-tools`

## Install the runtime
To install the runtime, you can use the following command:

```bash
pip install lemniscat-runtime
```

# Usage

To use the runtime, you can use the following command:

```bash
lem -m <manifest_file> -c <config_files> -s <steps> -o <override_variables> -x <output_file> -l <verbosity>
```

## Parameters

`-m` or `--manifest`: **[Required]** The manifest file to use. This file contains the definition of the product to deploy.

`-c` or `--config`: [Optional] The configuration files to use. These files contain the variables needed to deploy the product. 

`-s` or `--steps`: **[Required]** The steps to execute. These steps are defined in the manifest file.

`-o` or `--override`: [Optional] The override variables to use. These variables are used to override the variables defined in the configuration files.

`-x` or `--output`: [Optional] The output file to use. This file contains all the variables computed during the execution.

`-l` or `--log` : [Optional] The verbosity level to use. This level is used to control the verbosity of the logs.

# Manifest file

The manifest file is a YAML file that contains the definition of the product to deploy. It contains the following sections:

- **variables**: The variables needed to deploy the product.
- **capabilities**: The capabilities can be activated during the product deployment.
- **requirements**: The plugins needed to execute tasks describe in the manifest file.