# Systems Directory

This directory contains all the projects that have been built for DUPTester

## Adding a new project

For a project to be included it must be stored in a git repository and there must
be tags or branches that identify the versions to be built.

To add a project execute:
```commandline
cd systems
./scripts/create_system <directory> <name>
```

Where 
* `directory` is the name for the project directory under the systems directory, this is also the prefix for the docker build.
* `name` is the name of the directory that will be created inside the docker image.  This is also the name of the directory that will contain the source code.

Edit the `system/<directory>/config_lib` file to contain proper values for:

* `GIT_URL` The url to of the git repository to clone from. 
* `trunk` The name of the trunk in the git repository.  Usually "main" or "master".
* `name` The name of the directory to contain the source.  This is normally set properly during the `create_system` command.
* `build_cmd` The command to build the project.  Often something like "mvn clean package" or "ant clean;ant build".  Multiple commands may be specified by separating them with a semi-colon ";"

Edit the `system/<directory>/template/build-image/Dockerfile` to construct the proper environment to run the compiled code in.

## Add a project branch/tag

To add a project branch or tag execute:
```commandline
cd systems/<directory>
create_version <branch/tag>
```

This will check out the specified branch or tag of the project in `<directory>` and attempt to 
compile it. 

If the build fails check the `systems/<directory>/config.lib` to ensure that the proper `build_cmd` is set.

Once the build succeeds edit the `system/<directory>/<branch/tag>/build-image/Dockerfile` for any special needs for this particular branch/tag.
Then execute `<branch/tag>/build-docker-image`.

Once the docker image is created the version can be used in testing.
