#!/bin/bash
rm ../data/cust_db.sqlite
python2 db_gen.py
python2 build_transition_table.py
