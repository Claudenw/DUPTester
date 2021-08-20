How: Run `docker build -t test ./` under the current dir. 

This only needs to be run once in order to build a docker image with the target
version of ZooKeeper. 

There's one thing that needs to be changed in ../../zk_location:
/Users/yongle/research/projects/upgrade/src/zookeeper 
Here /Users/yongle/research/projects/upgrade/src/zookeeper is the src code dir. 

- Dockerfile
- README.md
- compile-src.sh : compiles the source code of the target version
- general-setup.sh : general setup for this image
- supervisord.conf : configuration for supervisord, which controls the services
  we want to start
- zk-clusternode.sh : script used by supervisord to start zookeeper, it
  also does some last-minute setup
- zk-setup.sh : setting up zookeeper, changing configuration, etc. 
