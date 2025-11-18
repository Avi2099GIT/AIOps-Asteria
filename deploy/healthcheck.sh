#!/bin/bash
curl -sSf http://localhost:8000/health || exit 1
echo OK
