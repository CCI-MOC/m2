
ORIG_DIR=`pwd`
source config/bmi-config.sh
cd ${BMI_INSTANCE_DIR}/ims

# Setup the previous environment
source ./config-interactive-session
source ./bmi-config.sh
./shutdown-bmi-servers.sh

if [ "$1" == "--pr" ]; then

  # The initial PR-60 will initiate the servers as scripts/...  
  PICASSO_ID=`pgrep -f scripts/picasso_server | cut -f1 -d' '`
  EINSTEIN_IDS=`pgrep -f scripts/einstein_server | cut -f1 -d' '`

  # If the IDs variables are not empty, then kill those processes
  if [ ! -z "$PICASSO_ID" ]; then
    kill -9 $PICASSO_ID
    #wait $PICASSO_ID 2>/dev/null
  fi

  if [ ! -z "$EINSTEIN_IDS" ]; then
    kill -9 $EINSTEIN_IDS
    #wait $EINSTEIN_IDS 2>/dev/null
  fi


  .bmi_venv/bin/picasso_server &
  .bmi_venv/bin/einstein_server &
  source .bmi_venv/bin/activate
else
  bin/picasso_server &
  bin/einstein_server &
  source ./bin/activate
fi
