# Distributed Systems &ndash; Project 2

Students: **Lev Svalov**, **Dmitry Podpryatov**

Group: **DS-02**

## Distributed File System

### How to Launch

Clone repository to machines with private closed network

```
git clone https://github.com/DmitriyPodpryatov/ds-project-2.git
```

Install [docker](https://docs.docker.com/engine/install/ubuntu/) and [docker-compose](https://docs.docker.com/compose/install/) on machines 

#### Storage Servers aka Datanodes

On server machines open folder with datanodes' files

```
cd ds-project-2/dfs/datanode
```

Run this to start datanodes

```
sudo docker-compose up -d
```

To access DFS on container, run

```
sudo docker exec -it <container name> bash
cd /dfs
```

#### Naming Server aka Namenode

On namenode machine open folder with namenode files

```
cd ds-project-2/dfs/namenode
```

Run this to start namenode

```
sudo docker-compose up -d
```

#### Client

On client machine open folder with client python script

```
cd ds-project-2/client
```

### How to Use

Set up an alias for python script

```
alias dfs='python3 client.py'
OR
alias dfs='/home/<user>/ds-project-2/client/python3 client.py'
```

Run commands by

```
dfs <args>
```

List of available commands:

```
dfs hello - get hello from namenode and active datanodes
dfs help - list of all commands
dfs init - initialize DFS and retun available space
dfs touch FILE - create empty FILE
dfs read FILE - download FILE
dfs write FILE DEST_DIR - upload FILE into DEST_DIR
dfs rm FILE - remove FILE
dfs info FILE - show info about FILE
copy SOURCE DEST - copy SOURCE into DEST
dfs move FILE DEST_DIR - move FILE into DEST_DIR
dfs cd DIR - open DIR
dfs ls DIR - list of files in DIR
dfs mkdir DIR - create DIR
dfs rmdir DIR - remove DIR
```

**Note:**

* Use `/` for the root folder
* No `.` or `..` are allowed
* No trailing `/` are allowed
