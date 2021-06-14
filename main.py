#!/usr/bin/python3

import os

pkg_list = os.popen("apt list --upgradable")
outputs = pkg_list.readlines()

imp_pkg = ["firefox", "sudo", "chromium","linux-image"]

sim_pkg = ["youtube-dl","wine","virtualbox","vscodium","wget","curl"]

pkgs = imp_pkg + sim_pkg

for pkg in pkgs:
	if pkg in str(outputs):
		print(f"{pkg} found on")
		for i in outputs:
			if pkg in i:
				print("->",i)
	else:
		print(f"{pkg} not found")	