#!/bin/bash
unset ERR
if [[ -n "$1" ]]; then
   SERVICE_UUID=$1
else
   echo "Must specify first parameter (Service UUID)"
   ERR=1
fi

if [[ -z "$ERR" ]]; then
    #SERVICE_UUID=`heat output-show $STACK_UUID service_uuid | sed 's/\"//g'`
    SCALE_UP_URL=http://localhost:4040/api/scaleservice/${SERVICE_UUID}/1
    SCALE_DOWN_URL=http://localhost:4040/api/scaleservice/${SERVICE_UUID}/-1

    VMS=`curl http://localhost:4040/api/services/$SERVICE_UUID/vm_list | sed 's/\"//g'`

    ALARMS=`ceilometer alarm-list | grep -e '| [a-f0-9]' | awk '{print $4}'`

    # Use the first segment of the service's UUID as an identifier of alarms belonging to a service
    # Use the first segment of a VM's UUID as an identifier of alarms belonging to a VM
    SERV_SUB_ID=`echo $SERVICE_UUID | cut -d '-' -f 1`

    for VM in $VMS; do
        # Only create alarms for VMs with no alarms. Need to identify those VMs
        VM_SUB_ID=`echo $VM | cut -d '-' -f 1`
        if [[ $ALARMS =~ $VM_SUB_ID ]]; then
            # Do nothing
            :
        else
            # Create alarms
            # Format of alarm name: serviceSubID-cpu_high-instanceSubID
            ceilometer alarm-threshold-create --name $SERV_SUB_ID-cpu_high-$VM_SUB_ID --description 'vSRX running hot' --meter-name cpu_util --threshold 50.0 --comparison-operator gt --statistic avg --period 30 --evaluation-periods 2 --alarm-action "$SCALE_UP_URL" --query resource_id=$VM
            ceilometer alarm-threshold-create --name $SERV_SUB_ID-cpu_low-$VM_SUB_ID --description 'vSRX almost idle' --meter-name cpu_util --threshold 10.0 --comparison-operator lt --statistic avg --period 30 --evaluation-periods 2 --alarm-action "$SCALE_DOWN_URL" --query resource_id=$VM

            #echo "creating alarm for $SERV_SUB_ID-cpu_high-$VM_SUB_ID"
        fi
    done
fi


