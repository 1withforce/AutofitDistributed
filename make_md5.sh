#!/bin/bash
md5sum $1 |cut -c1-32 > $2
