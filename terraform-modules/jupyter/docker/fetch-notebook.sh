#!/bin/bash

if [ -z "${NOTEBOOK_NAME}" ] || [ -z "${NOTEBOOKS_S3_BUCKET}" ]; then
      echo "NOTEBOOK_NAME or NOTEBOOKS_S3_BUCKET not defined, exiting"
      exit 1
fi


aws s3api get-object --bucket "${NOTEBOOKS_S3_BUCKET}" --key "${NOTEBOOK_NAME}" notebook.ipynb
