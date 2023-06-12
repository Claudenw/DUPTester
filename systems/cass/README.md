# Cassandra Docker Image Builder

This code creates images for various versions of Cassandra.

To create a version execute `create_version <tag>` e.g. (`create_version cassandra-4.0.9`)

If this is the first time running the script a `git` directory will be created and the
code checked out to it.  Branch checkouts are performed from the `git` directory.

The script will create a directory called `<tag>/build_image` and populate it with scripts to 
build and manage the docker image after which it will execute `<tag>compile-src` and `<tag>/build-docker-image`. 
See below for information about these scripts.


## Rebuilding a version

The next time `create_version <tag>` is run the code is updated from git and rebuilt.  Running `create_version` when
there is not update does not cause any changes to build scripts to be lost.

# Compiling source (compile-src)

Running `<tag>/compile-src` will update the local git repository and then 
checkout the code to `<tag>/build_image/cassandra` and build it. 
The result is tarred into `<tag>/build_image/cassandra.tar.gz`

When building the source if the `JAVA_HOME` environment variable is not set it is set to a default.

# Rebuilding the Docker image (build-docker-image)

Running `<tag>/build-docker-image` will execute the build`<tag>/build_image/Dockerfile` and update the
docker image using the latest `<tag>/build_image/cassandra.tar.gz`.  

The resulting image is called `cass-image-<tag>`
