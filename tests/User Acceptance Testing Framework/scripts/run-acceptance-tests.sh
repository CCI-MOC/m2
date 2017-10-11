#!/bin/bash

  #behave --no-capture tests/
  
  chmod g-wx,o-wx ~/.python-eggs
  behave --no-capture tests/bdd/

  #python -W ignore -m behave --no-capture tests/bdd/

  #lettuce tests/bdd/
