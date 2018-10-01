# This will be by CI tool to build BMI image that will be used for testing.

# Basing on image stored in docker hub for faster build
FROM bmis/bmi-ci

ENV HIL_USERNAME=admin
ENV HIL_PASSWORD=admin

# Copy source code
USER bmi
COPY .git/ /home/bmi/.git
COPY ims/ /home/bmi/ims/
COPY tests/ /home/bmi/tests/
COPY scripts/ /home/bmi/scripts/
COPY setup.py /home/bmi/setup.py
COPY ci/bmiconfig.cfg.ci /etc/bmi/bmiconfig.cfg

# Install
USER root
WORKDIR /home/bmi
RUN pip install --upgrade setuptools
RUN python setup.py develop

# Create DB
USER bmi
RUN bmi db ls

# Start dependencies when container starts
CMD dumb-init /home/bmi/runbmi.sh
