#!/usr/bin/env bash
case "$1" in
  new-job)
    shift
    for job in "$@"; do
      PYTHONPATH=src python3 src/tools/job_generator.py "$job" job
    done
    ;;

  new-profession)
    shift
    for job in "$@"; do
      PYTHONPATH=src python3 src/tools/job_generator.py "$job" profession
    done
    ;;

  new-advanced)
    shift
    for job in "$@"; do
      PYTHONPATH=src python3 src/tools/job_generator.py "$job" advanced
    done
    ;;

  *)
    PYTHONPATH=src python3 src/main.py
    ;;
esac