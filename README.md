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

## System model

The runtime is based on the following system model:

![system model](/doc/img/system-model.png)

### Capabilities

The capabilities are the DevOps steps that can be activated during the deployment of a product. It's designed to be sure that all the DevOps aspects are covered during the design of a product. 
For each capability, you can define the [solutions](#solutions) that need to be executed to activate the capability.
For example, for capability code you can define Github and Gitlab as [solutions](#solutions) to activate the capability when the product is deployed.

### Solutions

The solutions are the tools that can be used to execute the capabilities. For example, you can use Jenkins to execute the build capability, or you can use Ansible to execute the deployment capability.
For each solution, you can define a workflow with the [tasks](#tasks) that need to be executed to activate the capability.
For example, for Azure (in operate capability), you can define the [tasks](#tasks) that need to be executed to deploy infrastructure with Terraform.

### Tasks

The tasks are the actions that need to be executed to activate the capability. For example, you can define a task to execute a script, or a task to execute a terraform command.
For each task, you need to tag in witch [step](#step-concept) it needs to be executed, and the parameters that need to be used to execute the task.
You can define many tags for a task, and the task will be executed in the same step as the tag.
In the same step, the tasks are executed in the same order as defined in the manifest file.

### Step concept

The step is the concept that defines the big stages of the instantiation of the product. It's designed to be sure that all the tasks are executed in the right order during the instantiation of the product.
Their are 4 steps:
- **pre**: The step to prepare the instantiation of the product. For example, you can use this step to prepare the environment to deploy the product, prepare the configuration files, generate terraform plan, ...
- **run**: The step to execute the instantiation of the product. For example, you can use this step to deploy the infrastructure, define access rights, create git repository, ...
- **post**: The step to finalize the instantiation of the product. For example, you can use this step to execute the tests, generate the documentation, register the product in the CMDB, ...
- **clean**: The step to clean the instantiation of the product. For example, you can use this step to delete the infrastructure, delete the git repository, ...

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
lem -m <manifest_file> -c <config_files> -s <steps> -x <extraVariables> -o <outputContextFile> -v <verbosity>
```

## Parameters

`-m` or `--manifest`: **[Required]** The manifest file to use. This file contains the definition of the product to instantiate.

`-c` or `--configFiles`: [Optional] The configuration files to use. These files contain the variables needed to instantiate the product. 

`-s` or `--steps`: **[Required]** The steps to execute. These steps are defined in the manifest file.

`-x` or `--extraVariables`: [Optional] The override variables to use. These variables are used to override the variables defined in the configuration files.

`-o` or `--outputContext`: [Optional] The output file to use. This file contains all the variables computed during the execution.

`-v` or `--verbosity` : [Optional] The verbosity level to use. This level is used to control the verbosity of the logs.

## Definition

### Manifest

The parameters `-m` or `--manifest` is the path to the manifest file to use. This file contains the definition of the product to instantiate.

### Config files

The parameters `-c` or `--configFiles` is the path to the configuration files to use. These files contain the variables needed to instantiate the product.
The order of the files is important. The variables defined in the first file can be overridden by the variables defined in the second file, and so on.

### Steps

The parameters `-s` or `--steps` is the steps and capabilities to execute. These steps are defined in the manifest file.
You need to respect the naming convention to be sure that the runtime can execute the steps :
`<step>:<capability>`

For example :
- to execute only the pre step of the code capability, you must define : `-s ['pre:code']`
- to execute the pre and run steps of the code capability, you must define : `-s ['pre:code', 'run:code']`
- to execute the pre and run steps of the code capability and the pre step of the build capability, you must define : `-s ['pre:code', 'run:code', 'pre:build']`

If you want to execute all the capabilities, you can define `all` as the capability to execute.
For example :
- to execute all the pre steps for all capability, you must define : `-s ['pre:all']`
- to execute all the pre and run steps for all capability, you must define : `-s ['pre:all', 'run:all']`

If you want to execute all the instanciation steps for a capability (`pre`, `run` and `post`), you can define `all` as the step to execute.
For example :
- to execute all the steps for the code capability, you must define : `-s ['all:code']`
- to execute all the steps for all capability, you must define : `-s ['all:all']`

If you want to execute all the cleanup steps for a capability (`pre`, `clean` and `post`), you can define `allclean` as the step to execute.
For example :
- to execute all the cleanup steps for the code capability, you must define : `-s ['allclean:code']`
- to execute all the cleanup steps for all capability, you must define : `-s ['allclean:all']`

# Manifest file

The manifest file is a YAML file that contains the definition of the product to deploy. It contains the following sections:

- [**variables**](#variables): The variables needed to deploy the product.
- **capabilities**: The capabilities can be activated during the product deployment.
- **requirements**: The plugins needed to execute tasks describe in the manifest file.

## Variables

The variables are the static parameters needed to deploy the product. They are defined in the manifest file, and can be used in the tasks to execute.
For example, you can define a variable to define the name of the product, and use this variable in the tasks to create the product.

The variables are defined in the `variables` section of the manifest file, and are defined as a dictionary with the following structure:

```yaml
variables:
  - name: location
    value: West Europe
  ...
```

You can define in your variables a value based on another variablse. For example, you can define a variable `location` based on the environment variable `location`.
To do that, you can use the following syntax:

```yaml
variables:
  - name: location
    value: ${{ environment.location }}
  ...
```

You can also concatenate variables to define a new variable. For example, you can define a variable `resourceGroupId` based on the subscriptionId and the resource group name.
```yaml
variables:
  - name: resourceGroupId
    value: '/subscriptions/${{ env.subscriptionId }}/resourceGroups/${{ rgName }}'
  ...
```

## Capabilities

The capabilities are the DevOps steps that can be activated during the deployment of a product. It's designed to be sure that all the DevOps aspects are covered during the design of a product.
For each capability, you can define the [solutions](#solutions) that need to be executed to activate the capability.
For example, for capability code you can define Github and Gitlab as [solutions](#solutions) to activate the capability when the product is deployed.

The capabilities are defined in the `capabilities` section of the manifest file, and are defined as a dictionary with the following structure:

```yaml
capabilities:
  code:
    - solution: github
      ...
    - solution: gitlab
      ...
  build:
    - solution: jenkins
      ...
    - solution: azuredevops
      ...
  test:
    - solution: sonarqube
      ...
    - solution: jenkins
      ...
  release:
    - solution: artifactory
      ...
    - solution: azure-container-registry
      ...
  deploy:
    - solution: azuredevops
      ...
    - solution: argocd
      ...
  operate:
    - solution: azure
      ...
    - solution: aws
      ...
  monitor:
    - solution: grafana
      ...
    - solution: datadog
      ...
  plan:
    - solution: Jira
      ...
    - solution: PagerDuty
      ...
```

### Definition

Here, the list of capabilities that you can define in the manifest file:

- `code`: The capability to manage the code. For example, you can define the solutions to create a git repository, add collaborators, clone the repository, ...
- `build`: The capability to build. For example, you can define the solutions to build with Jenkins, Azure DevOps, ...
- `test`: The capability to test. For example, you can define the solutions to test with SonarQube, Jenkins, ...
- `release`: The capability to release. For example, you can define the solutions to release with Artifactory, Azure Container Registry, ...
- `deploy`: The capability to deploy. For example, you can define the solutions to deploy with Azure DevOps, ArgoCD, ...
- `operate`: The capability to operate. For example, you can define the solutions to operate with Azure, AWS, ...
- `monitor`: The capability to monitor. For example, you can define the solutions to monitor with Grafana, Datadog, ...
- `plan`: The capability to plan. For example, you can define the solutions to plan with Jira, PagerDuty, ...

Of course, you don't have to define all the capabilities in the manifest file. You can define only the capabilities that you need to or can activate during the deployment of the product.

You can't define the same capability twice in the manifest file. If you define the same capability twice, the runtime will raise an error.
You can't define a capability that is not in the list above. If you define a capability that is not in the list above, the runtime will raise an error.

## Solutions

The solutions are the tools that can be used to execute the capabilities. For example, you can use Jenkins to execute the build capability, or you can use Ansible to execute the deployment capability.
For each solution, you can define a workflow with the [tasks](#tasks) that need to be executed to activate the capability.
For example, for Azure (in operate capability), you can define the [tasks](#tasks) that need to be executed to deploy infrastructure with Terraform.

The solutions are defined in the capability section of the manifest file, and are defined as a dictionary with the following structure:

```yaml
capabilities:
  code :
    - solutions: github
      tasks:
        - name: github
          steps: 
            - run
          parameters:
            action: createRepository
            name: ${{ product.name }}
            description: ${{ product.description }}
            visibility: ${{ domain.visibility }}
            organization: ${{ domain.organization }}
            token: ${{ github.token }}
            ...
    - solution: gitlab
      tasks:
        - name: gitlab
          steps: 
            - run
          parameters:
            action: createRepository
            name: ${{ product.name }}
            description: ${{ product.description }}
            visibility: ${{ domain.visibility }}
            organization: ${{ domain.organization }}
            token: ${{ gitlab.token }}
            ...
  ...
```	

### Definition

You can define as many solutions as you want for a capability. For example, you can define Github and Gitlab as solutions for the code capability.
You can't define the same solution twice for a capability. If you define the same solution twice for a capability, the runtime will raise an error.

To define a solution, you need to define the following parameters:

- `solution: <solutionName>`, with `<solutionName>` the name of the solution to use to activate the capability.

For each solution, you can define the [tasks](#tasks) that need to be executed to activate the capability. The tasks are defined in the `tasks` section of the solution, and are defined as a dictionary with the following structure:

```yaml
- solutions: github
  tasks:
    ...
```

## Tasks

The tasks are the actions that need to be executed to activate the capability. For example, you can define a task to execute a script, or a task to execute a terraform command.
For each task, you need to tag in witch [step](#step-concept) it needs to be executed, and the parameters that need to be used to execute the task.
You can define many tags for a task, and the task will be executed in the same step as the tag.
In the same step, the tasks are executed in the same order as defined in the manifest file.

The tasks are defined in the solution section of the manifest file, and are defined as a dictionary with the following structure:

```yaml
capabilities:
  code :
    - solutions: github
      tasks:
        - name: github
          displayName: 'Create repository'
          steps: 
            - run
          parameters:
            action: createRepository
            name: ${{ product.name }}
            description: ${{ product.description }}
            visibility: ${{ domain.visibility }}
            organization: ${{ domain.organization }}
            token: ${{ github.token }}
            ...
        - name: github
          displayName: 'Add collaborators'
          steps: 
            - run
          parameters:
            action: addCollaborators
            name: ${{ product.name }}
            collaborators: ${{ product.collaborators }}
            token: ${{ github.token }}
        - name: github
          displayName: 'clone repository'
          steps: 
            - run
          parameters:
            action: clone
            name: ${{ product.name }}
            token: ${{ github.token }}
        - name: copy
          displayName: 'Copy sample code'
          steps: 
            - pre
          parameters:
            source: ${{ product.source }}
            destination: ${{ currentpath }}/${{ product.name }}
        - name: git
          displayName: 'Add files'
          steps: 
            - pre
          parameters:
            action: add
            path: ${{ currentpath }}/${{ product.name }}
        - name: git
          displayName: 'Commit files'
          steps: 
            - pre
          parameters:
            action: commit
            path: ${{ currentpath }}/${{ product.name }}
            message: 'Initial commit'
        - name: git
          displayName: 'Push files'
          steps: 
            - pre
          parameters:
            action: push
            path: ${{ currentpath }}/${{ product.name }}
            token: ${{ github.token }}
      ...
```

In order to factorize tasks in your solution, you can define templates for your tasks. For example, you can define a template to create and initialze a repository.
To do that, you can use the following syntax in your manifest file:

```yaml
capabilities:
  code :
    - solutions: github
      tasks:
        - template: ${{ templates.path }}/createRepository.yaml
          displayName: 'Create and initialize repository'
```

And in the `createRepository.yaml` file, you can define the following tasks:

```yaml
tasks:
  - name: github
    displayName: 'Create repository'
    steps: 
    - run
    parameters:
    action: createRepository
    name: ${{ product.name }}
    description: ${{ product.description }}
    visibility: ${{ domain.visibility }}
    organization: ${{ domain.organization }}
    token: ${{ github.token }}
    ...
  - name: github
    displayName: 'Add collaborators'
    steps: 
    - run
    parameters:
    action: addCollaborators
    name: ${{ product.name }}
    collaborators: ${{ product.collaborators }}
    token: ${{ github.token }}
  - name: github
    displayName: 'clone repository'
    steps: 
    - run
    parameters:
    action: clone
    name: ${{ product.name }}
    token: ${{ github.token }}
  - name: copy
    displayName: 'Copy sample code'
    steps: 
    - pre
    parameters:
    source: ${{ product.source }}
    destination: ${{ currentpath }}/${{ product.name }}
  - name: git
    displayName: 'Add files'
    steps: 
    - pre
    parameters:
    action: add
    path: ${{ currentpath }}/${{ product.name }}
  - name: git
    displayName: 'Commit files'
    steps: 
    - pre
    parameters:
    action: commit
    path: ${{ currentpath }}/${{ product.name }}
    message: 'Initial commit'
  - name: git
    displayName: 'Push files'
    steps: 
    - pre
    parameters:
    action: push
    path: ${{ currentpath }}/${{ product.name }}
    token: ${{ github.token }}
```

### Definition

You can define as many tasks as you want for a solution. For example, you can define a task to create a repository, a task to add collaborators, a task to deploy the infrastructure, ...
During the execution of the runtime, the tasks are executed in the same order as defined in the manifest file.

To define a task, you need to define the following parameters:

- `name: <pluginName>`, with `<pluginName>` the name of the plugin to execute. This parameter is mandatory.
- `displayName: <displayName>`, with `<displayName>` the name of the task to display in the logs. This parameter is optional.
- `steps: <steps>`, with `<steps>` the list of steps where the task needs to be executed. This parameter is mandatory.
  For example, you can define `steps: ['pre', 'run']` to execute the task in the pre and run steps.
- `parameters: <parameters>`, with `<parameters>` the parameters needed to execute the task. This parameter is mandatory.
- `condition: <condition>`, with `<condition>` the condition to execute the task. This parameter is optional. The condition is a boolean expression that needs to be true to execute the task. The condition can be based on the variables defined in the manifest file.
  For example, you can define `condition: "${{ productName }}" != ""` to execute the task only if the product name is not empty.

You can also define a template for your tasks. For example, you can define a template to create and initialze a repository.

To define a template, you need to define the following parameters:

- `template: <templatePath>`, with `<templatePath>` the path to the template file to use. This parameter is mandatory.
- `displayName: <displayName>`, with `<displayName>` the name of the task to display in the logs. This parameter is optional.

## Requirements

The requirements are the plugins needed to execute tasks describe in the manifest file. They are defined in the `requirements` section of the manifest file, and are defined as a dictionary with the following structure:

```yaml
requirements:
  - name: lemniscat.plugin.azurecli
    version: 1.0.0
  - name: lemniscat.plugin.github
    version: 1.0.0
    ...
  ...
```

# Runtime : How it works

The runtime work in 9 steps:

1. **Load the configuration**: The runtime load the configuration files.
2. **Load manifest variables**: The runtime load the variables defined in the manifest file.
3. **Load the extra variables**: The runtime load the extra variables.
4. **Interpete all the variables**: The runtime interpete all the variables. If some variables can't be interpeted, the runtime keep the variable as is and continue the execution.
5. **Define the steps and capabilities to execute**: The runtime define the steps and capabilities to execute based on the parameters.
6. **Read the manifest file (and templates)**: The runtime read the manifest file to get the definition of the product to intantiate.
7. **Donwload (if needed) the plugins**: The runtime download the plugins needed to execute the tasks.
8. **Execute the workflow**: The runtime execute the workflow to activate the capabilities.
9. **Save the output context**: If it's defined, the runtime save the context (all variables) in the output file.

## 1. Load the configuration

The runtime load the configuration files. The configuration files are the files that contain the variables needed to instantiate the product. The order of the files is important. The variables defined in the first file can be overridden by the variables defined in the second file, and so on.

> [!NOTE]
> To load configuration files, you can use the `-c` or `--configFiles` parameter in the command line.

For example, you can define a configuration file to define the variables decribed at project level like this :

```json
{
    "projectName": "myProject",
    "description": "This is my project",
    "visibility": "private",
    "organization": "myOrganization",
    "collaborators": ["user1", "user2"],
    "permissions": ["reader"]
}
```

And you can define a configuration file to define the variables decribed at environment level like this :
```json
{
    "envName": "developement",
    "location": "West Europe",
    "subscriptionId": "12345678-1234-1234-1234-123456789012",
    "rgName": "${{ projectName }}-${{ appName }}-${{ envName }}-rg",
    "permissions": ["contributor"]
}
```

After loading previous files the runtime will have the following variables :

| Variable | Value |
|----------|-------|
| projectName | myProject |
| description | This is my project |
| visibility | private |
| organization | myOrganization |
| collaborators | ["user1", "user2"] |
| permissions | ["contributor"] |
| envName | developement |
| location | West Europe |
| subscriptionId | 12345678-1234-1234-1234-123456789012 |
| rgName | ${{ projectName }}-${{ appName }}-${{ envName }}-rg |

## 2. Load manifest variables

After loading the configuration files, the runtime load the variables defined in the manifest file. The variables defined in the manifest file can override the variables defined in the configuration files.

For example, you can define a variable to define the name of the product, like this :

```yaml
variables:
  - name: productName
    value: ${{ projectName }}-${{ appName }}-${{ envName }}-app
  ...
```

After loading the manifest file, the runtime will have the following variables :

| Variable | Value |
|----------|-------|
| projectName | myProject |
| description | This is my project |
| visibility | private |
| organization | myOrganization |
| collaborators | ["user1", "user2"] |
| permissions | ["contributor"] |
| envName | developement |
| location | West Europe |
| subscriptionId | 12345678-1234-1234-1234-123456789012 |
| rgName | ${{ projectName }}-${{ appName }}-${{ envName }}-rg |
| productName | ${{ projectName }}-${{ appName }}-${{ envName }}-app |


## 3. Load the extra variables

After loading the configuration files, the runtime load the extra variables. The extra variables are the override variables to use. These variables are used to override the variables defined in the configuration files.

> [!NOTE]
> To load extra variables, you can use the `-x` or `--extraVariables` parameter in the command line.

For example, you can define a extra variable to define the name of the product, like this :

```json
{
    "appName": "myApp"
}
```

After loading the extra variables, the runtime will have the following variables :

| Variable | Value |
|----------|-------|
| projectName | myProject |
| description | This is my project |
| visibility | private |
| organization | myOrganization |
| collaborators | ["user1", "user2"] |
| permissions | ["contributor"] |
| envName | developement |
| location | West Europe |
| subscriptionId | 12345678-1234-1234-1234-123456789012 |
| rgName | ${{ projectName }}-${{ appName }}-${{ envName }}-rg |
| productName | ${{ projectName }}-${{ appName }}-${{ envName }}-app |
| appName | myApp |

## 4. Interpete all the variables

After loading the extra variables, the runtime interpete all the variables. If some variables can't be interpeted, the runtime keep the variable as is and continue the execution.

For example, the runtime will interpete the `rgName` variable to have the following value : `myProject-myApp-developement-rg`.
After interpeting all the variables, the runtime will have the following variables :

| Variable | Value |
|----------|-------|
| projectName | myProject |
| description | This is my project |
| visibility | private |
| organization | myOrganization |
| collaborators | ["user1", "user2"] |
| permissions | ["contributor"] |
| envName | developement |
| location | West Europe |
| subscriptionId | 12345678-1234-1234-1234-123456789012 |
| rgName | myProject-myApp-developement-rg |
| productName | myProject-myApp-developement-app |
| appName | myApp |

The interpreter can interprete `string` values, `int` values, `float` values, `boolean` values, `list` values and `dictionary` values.
For example, if a variable contains a complex value like this :

| Variable | Value |
|----------|-------|
| complexValue | { "productName": "${{ productName }}", "envName": "${{ envName }}" } |

The interpreter will interpete the `complexValue` variable to have the following value : `{ "productName": "myProject-myApp-developement-app", "envName": "developement" }`.

## 5. Define the steps and capabilities to execute

After interpeting all the variables, the runtime define the steps and capabilities to execute based on the parameters.

> [!NOTE]
> To define the steps and capabilities to execute, you can use the `-s` or `--steps` parameter in the command line.

## 6. Read the manifest file (and templates)

After defining the steps and capabilities to execute, the runtime read the manifest file to get the definition of the product to intantiate.
The runtime load the capabilities, the solutions, interprete templates and load the tasks to execute.

## 7. Donwload (if needed) the plugins

After reading the manifest file, the runtime download the plugins needed to execute the tasks.
Plugins need to be defined in the `requirements` section of the manifest file.

## 8. Execute the workflow

After downloading the plugins, the runtime execute the workflow to activate the capabilities.

> TODO

## 9. Save the output context

If it's defined, the runtime save the context (all variables interpreted) in the output file.

> [!NOTE]
> To save the context, you can use the `-o` or `--outputContext` parameter in the command line.