#!/bin/sh -e
set -x

ruff check app scripts app/tests --fix
ruff format app scripts app/tests
