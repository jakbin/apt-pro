# jkb
A python package for better update and manage your debian packages.

[![PyPI version](https://badge.fury.io/py/jkb.svg)](https://badge.fury.io/py/jkb)

![GitHub Contributors](https://img.shields.io/github/contributors/jakbin/jkb)

![GitHub commit activity](https://img.shields.io/github/commit-activity/m/jakbin/jkb)

![GitHub last commit](https://img.shields.io/github/last-commit/jakbin/jkb)

## Introduction

When you run "apt list --upgradable" in your terminal, you find around 2000 upgradable packages (if you are using parrot os or kali linux like distibution). It hard to find your important package or security releases.  

For this solution, here is "jkb".

## Compatability
Python 3.6+ is required.

## Installation

```bash
pip install jkb
```
or 

```bash
pip3 install jkb
```

## Then run it with:

```bash
jkb -h
```

## Todo-List 

- [x] Pretty Output 
- [x] Update and upgrade packages from Here
- [x] Add or Remove packages form list
- [ ] Use sqlite 
