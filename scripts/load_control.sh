#!/bin/bash

if [ -z "$1" ]
  then
    CPAR=10
  else
    CPAR=$1
fi

if [ -z "$2" ]
  then
    QPAR=20
  else
    QPAR=$2
fi

# limits for raise/keep the load in %, >=
LIMIT_RAISE=95
LIMIT_KEEP=85

#LATENCY limit
LIMIT_LAT=0.04

CVAL=$CPAR # conccurrent clients 
QVAL=$QPAR # rate for 1 client 
RF=10   #increase by factor in% 
CDIFF=10 #increase by value
INTERV="2s" #in sec 
ITER=50 
URL=http://node2:31909/hello 
echo "INPUT_QPS;OUTPUT_RPS;SUCC;AVG;P50;P95;P99;OPERATION" 
for i in $(eval echo "{1..$ITER}") ; do

  if [ ! -z "$3" ] # if param3 is present then keep fixed load
    then
      CVAL=$CPAR
      QVAL=$QPAR
  fi
#       CVAL=20
#       QVAL=20
        CVAL=$(printf  %.0f "$CVAL")
        QPS=$(($CVAL * $QVAL))
#        echo "Q: $QVAL, C: $CVAL, QPS: $QPS"
        hey -z $INTERV -c $CVAL -q $QVAL $URL > res.temp
#       cp res.temp res.temp.$i
        QPS_LINE=`grep "Req" res.temp`
        AVG=`grep "Ave" res.temp | cut -f2 | cut -d" " -f1`
        P50=`grep "50%" res.temp | cut -d" " -f 5`
        P95=`grep "95%" res.temp | cut -d" " -f 5`
        P99=`grep "99%" res.temp | cut -d" " -f 5`
#        echo $QPS_LINE
        RPSVAL=`echo $QPS_LINE | cut -d":" -f2 | tr -d '[:space:]'`
#        echo "RPS1: $RPSVAL"
        RPSVAL=${RPSVAL%.*}
#        echo "RPS2:xxx$RPSVAL"
        PRC=$((100 * $RPSVAL / $QPS))
#        echo "%= $PRC"


#latency based logic:
    if (( $(echo "$P95 > $LIMIT_LAT" |bc -l) ))
    then
#       echo "latency limit violation"
        OP="v"
        CVAL=$( echo "$CVAL * (100 - $RF ) / 100" |bc -l)
    else


#RPS based logic:
        if [ $PRC -ge $LIMIT_RAISE ]
        then
                CVAL=$( echo "$CVAL * (100 + $RF ) / 100" | bc -l)
#               CVAL=$(($CVAL + $CDIFF))
                OP="^"
        elif [ $PRC -ge $LIMIT_KEEP ]
        then
                OP="-"
#                echo "keep"
                #CVAL=$(($RPSVAL / $QVAL))
        else
                OP="_"
#               echo "backoff"
                CVAL=$( echo "$RPSVAL / $QVAL " | bc -l)
#                CVAL=$(($CVAL * (100 - $RF ) / 100))
        fi
#        echo "newC= $CVAL"
    fi



                echo "$QPS;$RPSVAL;$PRC;$AVG;$P50;$P95;$P99;$OP"
done
