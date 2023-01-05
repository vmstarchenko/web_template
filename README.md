# Plan
- db container: mysql, sqlite, postgres
- ui init
- setup instruction in readme
- permissions (groups, per type, per object)
- file upload
- filtering
- tags (many-to-many example)
- objects versions
- admin pannel

# Setup
```bash
make server_bash
server_setup.sh  # same as: bash ~/etc/scripts/server_setup.sh
exit
```

# Run tests
```bash
make server_bash
test.sh  # same as: bash ~/etc/scripts/test.sh
```

# Run server
```bash
make server_up
# and open http://localhost:8080
```

# Setup ui
```bash
mkdir ui
make ui_build && make ui_bash
yarn global add @ionic/cli && ionic config set -g npmClient yarn
ionic start ui blank --type=react --no-deps --no-git
mv ~/ui/ui/* ~/ui/ && rm -r ~/ui/ui
yarn run start
```
