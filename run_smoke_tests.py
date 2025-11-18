import subprocess, sys, os
print('Running pytest...')
rc = subprocess.call([sys.executable, '-m', 'pytest', '-q'])
print('pytest exit code', rc)
if rc != 0:
    raise SystemExit('Tests failed')
print('All tests passed')
