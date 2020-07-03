# Dockerfile Debian latest

Build command:

	$ docker build .

Run command:

	$ docker run --cap-add SYS_PTRACE <image-id>

Notes:

This pulls from staging by default, as thats where I do all my testing of new features / bug fixes.

If you want to pull from master instead, change staging to master on the ENTRYPOINT line.

IMPORTANT: in order for apache2buddy to run properly, docker images need a capability adding at run time:

	--cap-add SYS_PTRACE

Without this, apache2buddy will crash out when it runs pmap, see https://github.com/richardforth/apache2buddy/issues/329.
