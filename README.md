# Distributed Systems &ndash; Project 2

Students: **Lev Svalov**, **Dmitry Podpryatov**

Group: **DS-02**

## Distributed File System

### Storage Servers aka Datanodes

Copy `dfs/datanode` folder to the machine

```
scp -r dfs/datanode user@IP:
```

Or

```
git clone https://github.com/DmitriyPodpryatov/ds-project-2.git
cd ds-project-2/datanode
```

Run

```
docker-compose up --build
```

### Naming Server aka Namenode

Copy `dfs/namenode` folder to the machine

```
scp -r dfs/namenode user@IP:
```

Or

```
git clone https://github.com/DmitriyPodpryatov/ds-project-2.git
cd ds-project-2/namenode
```

Run

```
docker-compose up --build
```

### Client

Copy `client` folder on the machine(s)

```
scp -r client user@IP:
```

Or

```
git clone https://github.com/DmitriyPodpryatov/ds-project-2.git
cd client
```

Run

```
python3 client.py <args>
```
