SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

export ROBIN_IS_DEVICE=1
python $SCRIPTPATH/../robin/config.py
python $SCRIPTPATH/../robin/main.py


