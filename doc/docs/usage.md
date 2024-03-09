To use the runtime, you can use the following command:

```bash
lem -m <manifest_file> -c <config_files> -s <steps> -x <extraVariables> -o <outputContextFile> -v <verbosity>
```

### Parameters

`-m` or `--manifest`: **[Required]** The manifest file to use. This file contains the definition of the product to instantiate.

`-c` or `--configFiles`: [Optional] The configuration files to use. These files contain the variables needed to instantiate the product. 

`-s` or `--steps`: **[Required]** The steps to execute. These steps are defined in the manifest file.

`-x` or `--extraVariables`: [Optional] The override variables to use. These variables are used to override the variables defined in the configuration files.

`-o` or `--outputContext`: [Optional] The output file to use. This file contains all the variables computed during the execution.

`-v` or `--verbosity` : [Optional] The verbosity level to use. This level is used to control the verbosity of the logs.

### Definition

#### Manifest

The parameters `-m` or `--manifest` is the path to the manifest file to use. This file contains the definition of the product to instantiate.

#### Config files

The parameters `-c` or `--configFiles` is the path to the configuration files to use. These files contain the variables needed to instantiate the product.
The order of the files is important. The variables defined in the first file can be overridden by the variables defined in the second file, and so on.

#### Steps

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
