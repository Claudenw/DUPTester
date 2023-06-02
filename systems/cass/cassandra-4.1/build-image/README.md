How: Run `docker build -t test ./` under the current dir. 

This only needs to be run once in order to build a docker image with the target
version of Cassandra. 

There's one thing that needs to be changed in ../../cassandra_location:
cp -r /Users/yongle/research/projects/upgrade/src/cassandra ./
Here /Users/yongle/research/projects/upgrade/src/cassandra is the src code dir. 

- Dockerfile
- README.md
- compile-src.sh : compiles the source code of the target version
- general-setup.sh : general setup for this image
- supervisord.conf : configuration for supervisord, which controls the services
  we want to start
- cassandra-clusternode.sh : script used by supervisord to start cassandra, it
  also does some last-minute setup
- cass-setup.sh : setting up cassandra, changing configuration, etc. 
