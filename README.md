# Distributed Systems &ndash; Project 2

Students: **Lev Svalov**, **Dmitry Podpryatov**

Group: **DS-02**

## Docker Swarm

Create docker-machines

```
docker-machine create --driver virtualbox Namenode
docker-machine create --driver virtualbox Datanode-1
docker-machine create --driver virtualbox Datanode-2
docker-machine ls
```

Initialize docker swarm and add servers

```
docker-machine ssh Namenode
docker swarm init --advertise-addr <IP>

docker-machine ssh Datanode-1
docker swarm join --token <token> <IP>

docker-machine ssh Datanode-2
docker swarm join --token <token> <IP>

docker node ls
```
