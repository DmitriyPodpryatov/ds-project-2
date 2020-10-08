#!/bin/bash

touch ~/.custom_commands.sh
sudo echo "#!/bin/bash customFS() { python3 client $1 $2 }" >> ~/.custom_command.sh
chmod +x ~/.custom_command.sh
#in theory reboot is needed here
source ~/.custom_command.sh 