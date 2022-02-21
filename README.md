### Install pipenv 
```
pip3 install pipenv
```

### Install psycopg2-binary
```
pipenv install psycopg2-binary
```

### Activate virtual environment
```
pipenv shell
```

### Install dependencies
```
pipenv install
```

### Run biweb container
```
docker-compose run biweb /bin/bash
```

### Get in biweb container
```
docker exec -it biweb /bin/bash
```

### Run commands into biweb container
```
docker-compose run biweb <command>
```

# Debug with pdb

Up the container with 
```
docker-compose up -d bidb biweb
```

and attach the container
```
docker attach <containe_id>
```

You can find the id with `docker ps`


In order to debug, use pdb
```
from pdb import set_trace as bp
...
bp()
...
```
Import the function set trace from pdb `from pdb import set_trace as bp` and use `bp()` in the line you want the break point