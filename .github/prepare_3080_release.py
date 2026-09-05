import runpy

# The complete 3.0.80 preparation now contains the final column-lock and
# automatic Internet-description implementation.
runpy.run_path('.github/prepare_3080.py', run_name='__main__')

print('Prepared iCE Onhand 3.0.80 release')
