#!/bin/sh
set -x -e

mkdir -p $PREFIX/share/man/man1

cp share/man/man1/* $PREFIX/share/man/man1
