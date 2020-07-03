# About Dockerfiles

I should just point out to anyone that doesnt understand the purpose of dockerizing apache2buddy - its for testing only. You will still need to run the apache2buddy script on your actual servers, because apache2buddy will only see what it sees in the containers - so I'm only using them for testing and hopefully getting changes out faster.

It's also useful to have a known good running script to compare against if you are having issues, that's what Docker is for here, it containerizes it in its own little bubble so it should run all the time, every time - in that container.

So, say you are running Debian 10 and apache2buddy is not working for you, you can build and run the Debian 10 Dockerfile and check to see why yours is different.

Thats the main idea. You wont be able to tune any existing server using a dockerised version of apache2buddy, it just doesnt work like that, it can only see whats running inside the container.

If you notice any Dockerfiles are missing, feel free to create your own and submit a PR. I will be working on producing supported Dockerfiles for the OSes listed in the code at line 382 to 394:

```perl
	my @supported_os_list = ('Ubuntu',
				'ubuntu',
				'Debian',
				'debian',
				'Red Hat Enterprise Linux',
				'Red Hat Enterprise Linux Server',
				'redhat',
				'CentOS Linux',
				'CentOS',
				'centos',
				'Scientific Linux',
				'SUSE Linux Enterprise Server',
				'SuSE');
```

Obviously Red Hat is proprietary so for testing purposes we wiill stick to CentOS and Scientific  (where base images are available).

Don't forget when testing on Docker, apache2buddy requires that the image has a capability added at runtime:

	--cap-add SYS_PTRACE

So for example after building your docker image from these docker files, you should run the image like so:

	$ docker run --cap-add SYS_PTRACE <image-id>

If you do not add this capability, apache2buddy will crash out when it comes to running pmap.

# Docker Hub Images

I have uploaded a few images to docker hub:

	forric/centos_6_apache2buddy_mas
	forric/centos_6_apache2buddy_stag
	forric/centos_7_apache2buddy_mas
	forric/centos_7_apache2buddy_stag
	forric/centos_8_apache2buddy_mas
	forric/centos_8_apache2buddy_stag
	forric/debian_10_apache2buddy_mas
	forric/debian_10_apache2buddy_stag
	forric/scientific_6_apache2buddy_mas
	forric/scientific_6_apache2buddy_stag

You can pull these with 'docker pull'. More to follow.

	mas => pulls from master branch
	stag => pulls from staging branch

# Notes

 - Scientific Linux has no docker image yet for Scientific Linux 8
 - I couldnt find any Suse linux docker images
 - same with RHEL, but then CentOS is a rebuild so we are all good.
 - Most of the time if it works on CentOS,  it will also work on RHEL and Scientific.
