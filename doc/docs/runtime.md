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

### 1. Load the configuration

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

### 2. Load manifest variables

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

### 3. Load the extra variables

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

### 4. Interpete all the variables

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

### 5. Define the steps and capabilities to execute

After interpeting all the variables, the runtime define the steps and capabilities to execute based on the parameters.

> [!NOTE]
> To define the steps and capabilities to execute, you can use the `-s` or `--steps` parameter in the command line.

### 6. Read the manifest file (and templates)

After defining the steps and capabilities to execute, the runtime read the manifest file to get the definition of the product to intantiate.
The runtime load the capabilities, the solutions, interprete templates and load the tasks to execute.

### 7. Donwload (if needed) the plugins

After reading the manifest file, the runtime download the plugins needed to execute the tasks.
Plugins need to be defined in the `requirements` section of the manifest file.

### 8. Execute the workflow

After downloading the plugins, the runtime execute the workflow to activate the capabilities.

> [!NOTE]
> **Activation of the capabilities**
> To activate a capability you must define a variable named `<capability>.enable` and set to `true`.
>For example, to activate the code capability, you must define the following variable : `code.enable: true`.

> [!NOTE]
> **Define the solution to use**
> To define the solution to use to activate a capability, you must define a variable named `<capability>.solution` and set to the name of the solution to use.
> For example, to define Github as the solution to activate the code capability, you must define the following variable : `code.solution: Github`.

For each capability enabled, the runtime execute the solution defined in variables.

For each solution, the runtime execute the tasks defined.

### Workflow execution

The tasks are always executed in a specific order. The order is defined by the steps defined for each task.
If you execute the runtime with the `--steps ["all:code"]` parameter, the runtime will execute all the tasks (exept `clean` steps) with this order :

1. All tasks with the `pre` step
2. All tasks with the `run` step
3. All tasks with the `post` step

If you execute the runtime with the `--steps ["allclean:code"]` parameter, the runtime will execute all the tasks (exept `run` steps) with this order :

1. All tasks with the `pre` step
2. All tasks with the `clean` step
3. All tasks with the `post` step

> [!NOTE]
> If your task is tagged with multiple steps and the runtime is launched to execute this steps both, the task will be executed once.
> For example, if you execute the runtime with the `--steps ["all:code"]` parameter and you have a task with the steps `pre` and `run` (for exemple with Terraform init), the runtime will execute all the tasks with the `pre` step and ignore `run` step.

For each task, the runtime execute the plugin defined.
If the plugin generate output, the runtime collect the output and store it in the context (the bag of variables).

For example, if you define a task to create a repository with Github, the runtime will execute the Github plugin to create the repository. If the plugin generate the repository URL, the runtime will store the `repositoryURL` variables in the context.
So the runtime will have the following variables :

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
| repositoryURL | https://github.com/lemniscat-devops/lemniscat.runtime.git |

After executing the plugin, the runtime interpret all the variables. If some variables can't be interpeted, the runtime keep the variable as is and continue the execution.

### 9. Save the output context

If it's defined, the runtime save the context (all variables interpreted) in the output file.

> [!NOTE]
> To save the context, you can use the `-o` or `--outputContext` parameter in the command line.