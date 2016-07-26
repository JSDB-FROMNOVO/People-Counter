#!/bin/bash
unset ERR
if [[ -n "$1" ]]; then
   SERVICE_UUID=$1
else
   echo "Must specify first parameter (Service UUID)"
   ERR=1
fi

if [[ -z "$ERR" ]]; then
    POTENTIAL_STACKS=`heat stack-list | grep firewall | grep -e "| [0-9a-f]" | awk '{print $2}'`
    TARGET_STACK=""
    for STACK in $POTENTIAL_STACKS; do
        UUID=`heat output-show $STACK service_uuid | sed 's/\"//g'`
        if [[ -n $SERVICE_UUID ]]; then
            if [[ $SERVICE_UUID == $UUID ]]; then
                TARGET_STACK=$STACK
            fi
        fi
    done

    if [[ -n $TARGET_STACK ]]; then
        heat stack-delete $TARGET_STACK
    fi
fi

