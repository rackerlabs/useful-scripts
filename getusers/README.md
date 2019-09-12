# GetUsers
A small python script for getting and displaying Linux users and login times

### Usage
```
  -h, --help          Show this help message and exit
  -v, --version       Shows script version
  -s, --system-users  Show system users on the device
  -u, --users         Show users on this device
  -a, --all-users     Show all users on this device.
  -F, --show-full     When displaying, show the full user information
                      including GECOS and Group ID
```

### Example Output

```
# ./getusers.py

   ______     __     __  __
  / ____/__  / /_   / / / /_______  __________
 / / __/ _ \/ __/  / / / / ___/ _ \/ ___/ ___/
/ /_/ /  __/ /_   / /_/ (__  )  __/ /  (__  )
\____/\___/\__/   \____/____/\___/_/  /____/


Default: Showing standard users

ID                  User                Home                Shell               Sudo                Last Login
1000                centos              /home/centos        /bin/bash           yes                 None found
1001                testuser            /home/testuser      /bin/bash           no                  Sat Jul 6 16:25
1002                luke                /home/luke          /bin/bash           yes                 Sat Jul 6 16:17
1003                testuser9999        /home/testuser9999  /bin/bash           no                  None found
```
