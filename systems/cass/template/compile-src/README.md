This image is used to compile Cassandra 1.1.0 
because compiling it with jdk 8 runs into an antlr error 
caused by incompatibility between jdk 7 & jdk 8. 

- Run `sh build-docker-image.sh` to build the docker image. 
- Run `sh prepare-src.sh` to prepare Cassandra source code. 
- Run `docker-compose up` to start the container. 

However, compiling with jdk 7 runs into missing jar problems reported by maven. 
Weirdly compiling with jdk 8 could retrieve all the jars from maven repo. 
There are 2 methods to resolve it. 
1) Either you can manually downloaded required jars, 
or 2) you can use jdk 8 to compile it first and it'll download and cache required jars, 
then switch to jdk 7 to compile it again. 

