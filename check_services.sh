#!/bin/bash
#Sebastian Porteiro
#Definimos algunas variables para saber en que maquina estamos
counter=0
user='administrador'
hostname=`hostname`
settings_path=/home/administrador/.openbroadcaster/mixter_settings.cfg
#settings_path=/home/administrador/mixter/mixter_settings.cfg

#Load settings from file, for now, we use regex to do it
enabled=`grep -Po 'cs_enabled =..*?[0-9]*' $settings_path | awk -F'= ' '{print $2}'`
cs_folder=`grep -Po 'cs_folder =..*?[\/aA-zZ0-9.]*' $settings_path | awk -F'= ' '{print $2}'`
cs_files_other_path=`grep -Po 'cs_files_other_path =..*?[\/aA-zZ0-9.]*' $settings_path | awk -F'= ' '{print $2}'`
cs_files_get_method=`grep -Po 'cs_files_get_method =..*?[aA-zZ0-9]*' $settings_path | awk -F'= ' '{print $2}'`

#define roles, we need to check this again every time the loop goes on
hostname_main=`grep -Po 'cs_hostname_main =..*?[aA-zZ0-9]*' $settings_path | awk -F'= ' '{print $2}'`
hostname_backup=`grep -Po 'cs_hostname_backup =..*?[aA-zZ0-9]*' $settings_path | awk -F'= ' '{print $2}'`
ip_main=`grep -Po 'cs_ip_main =..*?[0-9.]*' $settings_path | awk -F'= ' '{print $2}'`
ip_backup=`grep -Po 'cs_ip_backup =..*?[0-9.]*' $settings_path | awk -F'= ' '{print $2}'`
multicast_main=`grep -Po 'cs_multicast_main =..*?[0-9.]*' $settings_path | awk -F'= ' '{print $2}'`
multicast_backup=`grep -Po 'cs_multicast_backup =..*?[0-9.]*' $settings_path | awk -F'= ' '{print $2}'`
multicast_port='33333'

#define where to send telegram notifications
telegram_notifications=`grep -Po 'telegram_notifications =..*?[\/aA-zZ0-9.:0-9]*' $settings_path | awk -F'= ' '{print $2}'`

status=0
if [ $hostname = $hostname_main ] ; then
    role='1'
    role_other='2'
    ip_other=$ip_backup
    multicast_self=$multicast_main
    multicast_other=$multicast_backup
    ip_self=$ip_main
    elif [ $hostname = $hostname_backup ] ; then
    role='2'
    role_other='1'
    ip_other=$ip_main
    multicast_self=$multicast_backup
    multicast_other=$multicast_main
    ip_self=$ip_backup
    elif [ $hostname = $hostname_development ] ; then
    role='3'
    role_other='4'
    ip_other=$ip_development
    multicast_self=$multicast_development
    multicast_other=$multicast_development
    ip_self=$ip_development
    else	
    echo `date` "Esta maquina no se identifica como Main ni Backup ni Development, saliendo del script check_services.sh"
    exit 1
fi
log_path=$cs_folder/status_$role.log
log_host="/home/administrador/.openbroadcaster/logs/status.log"
rm -rf $log_path
echo `date` "[debug] $hostname Lanzando script" | tee -a $log_path >> $log_host
echo "El rol de esta maquina es: "$role
echo `date`  "[debug] $hostname El rol de la maquina es "$role | tee -a $log_path >> $log_host
counter_status=0
prev_uptime=0

while true; do
    if [ $enabled = 1 ];then
        ip_main=`grep -Po 'cs_ip_main =..*?[0-9.]*' $settings_path | awk -F'= ' '{print $2}'`
        ip_backup=`grep -Po 'cs_ip_backup =..*?[0-9.]*' $settings_path | awk -F'= ' '{print $2}'`
        hostname_main=`grep -Po 'cs_hostname_main =..*?[aA-zZ0-9]*' $settings_path | awk -F'= ' '{print $2}'`
        hostname_backup=`grep -Po 'cs_hostname_backup =..*?[aA-zZ0-9]*' $settings_path | awk -F'= ' '{print $2}'`
        multicast_main=`grep -Po 'cs_multicast_main =..*?[0-9.]*' $settings_path | awk -F'= ' '{print $2}'`
        multicast_backup=`grep -Po 'cs_multicast_backup =..*?[0-9.]*' $settings_path | awk -F'= ' '{print $2}'`
        cs_send_emergency=`grep -Po 'cs_send_emergency =..*?[0-9.]*' $settings_path | awk -F'= ' '{print $2}'`

        if [ $hostname = $hostname_main ] ; then
            role='1'
            role_other='2'
            ip_other=$ip_backup
            multicast_self=$multicast_main
            multicast_other=$multicast_backup
            ip_self=$ip_main
            elif [ $hostname = $hostname_backup ] ; then
            role='2'
            role_other='1'
            ip_other=$ip_main
            multicast_self=$multicast_backup
            multicast_other=$multicast_main
            ip_self=$ip_backup
            else	
            echo `date` "Esta maquina no se identifica como Main ni Backup, saliendo del script check_services.sh"
            exit 1
        fi

    log_lines_counter=$(wc -l < $log_path)
    cpu_usage=`uptime | grep -ohe 'load average[s:][: ].*' | awk '{ print $3}' | sed -s 's/,$//gi'`
    cpu_total=`nproc`
    #shm_usage=`df -k /dev/shm/ | awk 'NR==2 {print $5}'`
    shm_usage=`df -h /dev/shm | awk 'NR==2 {print $3"/"$2"/"$4}'`
    ram_usage=`free -h | awk 'NR==2 {print $3"/"$2"/"$4}'`

    obplayer_pid=`ps -U $user | grep 'obplayer_loop' |  awk 'NR==1{ print $1}'`
    snowmix_pid=`ps -U $user | grep 'snowmix' |  awk 'NR==1{ print $1}'`
    #comprobar ffmpeg en lugar de multicast? por el FIXME de abajo y el IGMPv3
    ffmpeg_pid=`ps -U $user | grep 'ffmpeg' |  awk 'NR==1{ print $1}'`
    #comprobar mixter
    mixter_pid=`ps -auU $user | grep 'http_server' |  awk 'NR==1{ print $2}'`

    #OJO! si hay mas de una transmision, el grep debe ser de la ip principal, multicast_self FIXME si tambien se escucha, da falso positivo
    multicast_ip=`ip maddress | grep $multicast_self | awk 'NR==1{ print $2}'`

    if [ $log_lines_counter -gt 30 ] ; then
	    #cat $log_path >> /home/administrador/.openbroadcaster/logs/status.log
	    echo `date`  "[debug] $hostname Log vaciado" > $log_path
    fi
    emergency=0
    if [ X$obplayer_pid = X ] ; then
        obplayer_pid='0'
    fi
    if [ X$snowmix_pid = X ] ; then
        snowmix_pid='0'
    fi
    if [ X$multicast_ip = X ] ; then
        multicast_ip='0'
    fi
    if [ X$mixter_pid = X ] ; then
        mixter_pid='0'
    fi

    if [ X$ffmpeg_pid = X ] ; then
        ffmpeg_pid='0'
    fi
    counter=$(($counter + 1))
    info_to_log="[error] $hostname suicidandose. Playouter PID: $mixter_pid, Obplayer PID: $obplayer_pid, ffmpeg PID: $ffmpeg_pid, RAM $ram_usage, CPU $cpu_usage, SHM $shm_usage" 
    if  [ $counter -gt 30 ] ; then
        if  [ $status = 0 ] ; then
       	 echo "Tiempo de respuesta limite, el sistema se suicidara si algo no funciona a partir de ahora"
       	 echo `date` "[debug] $hostname Tiempo de respuesta limite, el sistema se suicidara si algo no funciona a partir de ahora" | tee -a $log_path >> $log_host
        fi
        status=1
	    #Comentado porque la deteccion de la ip por la que se emite el multicast no es correcta, verifico si hay proceso de ffmpeg
	    #if [ $obplayer_pid = 0 ] || [ $snowmix_pid = 0 ] || [ $multicast_ip = 0 ] ; then
        #ya no dependemos de snowmix
        #if [ $obplayer_pid = 0 ] || [ $snowmix_pid = 0 ] || [ $ffmpeg_pid = 0 ] ; then
	    if [ $obplayer_pid = 0 ] || [ $ffmpeg_pid = 0 ] || [ $mixter_pid = 0 ]; then
		    echo $info_to_log
		    echo `date` $info_to_log | tee -a $log_path >> $log_host
            python3 /home/administrador/obplayer/mixter/sendemail.py "$info_to_log"
            curl -X POST -d '{"user":"admin","pass":"admin","msg":"'"$info_to_log"'"}'  $telegram_notifications
            curl -X POST -d '{"user":"admin","pass":"admin"}'  http://$ip_self:1666/suicide
            rm -rf $cs_folder/status_$role.json
		    killall -9 tail
	    fi
    fi
    #if everything is already working, we can set status to 1
    #if [ $counter -gt 10 ] && [ $counter -lt 30 ] && [ $obplayer_pid != 0 ] && [ $ffmpeg_pid != 0 ] && [ $mixter_pid != 0 ]; then
    if [ $obplayer_pid != 0 ] && [ $ffmpeg_pid != 0 ] && [ $mixter_pid != 0 ]; then
        status=1
    fi
    if [ X$secondary_pid != X ];then
	    emergency=1
    fi
    #Cuidado en como se forma el json!, tiene que ajustarse bien al grep que se hace para sacar los valores
    json='{'
    json+='"hostname": "'$hostname'",'
    json+='"role": "'$role'",'
    json+='"ip_main": "'$ip_main'",'
    json+='"uptime": '$counter','
    json+='"cpu_usage": "'$cpu_usage'/'$cpu_total'",'
    json+='"shm_usage": "'$shm_usage'",'
    json+='"ram_usage": "'$ram_usage'",'
    json+='"obplayer_pid": '$obplayer_pid','
    #json+='"snowmix_pid": '$snowmix_pid','
    json+='"mixter_pid": '$mixter_pid','
    #json+='"multicast_ip": "'$multicast_ip'",'
    json+='"ip_self": "'$ip_self'",'
    json+='"status": '$status','
    json+='"emergency": '$emergency
    json+='}'

    #overwrite our copy of other json in case values does not change
    json_other='{'
    json_other+='"hostname": "-",'
    json_other+='"role": "'$role_other'",'
    json_other+='"ip_main": "'$ip_main'",'
    json_other+='"uptime":  0,'
    json_other+='"cpu_usage":  "-/-",'
    json_other+='"shm_usage":  "-/-",'
    json_other+='"ram_usage": "-/-",'
    json_other+='"obplayer_pid":  "-",'
    json_other+='"mixter_pid":  "-",'
    json_other+='"ip_self": "'$ip_other'",'
    json_other+='"status":  0,'
    json_other+='"emergency":  0'
    json_other+='}'

    echo $json
    echo $json > $cs_folder/status_$role.json
	
	#save also a frame of each stream to the cs_folder
	if [ $((counter%10)) -eq 0 ];then
		ffmpeg -y -timeout 1 -i udp://$multicast_self:$multicast_port -vframes 1 -vf scale=640:360 $cs_folder/thumb_$role.jpg &
		ffmpeg -y -timeout 1 -i udp://$multicast_other:$multicast_port -vframes 1 -vf scale=640:360 $cs_folder/thumb_$role_other.jpg &
	fi

    if [ $cs_files_get_method = "wget" ];then
	    wget -O $cs_folder/status_$role_other.log http://$ip_other:4567/status/status_$role_other.log
	    wget -O $cs_folder/status_$role_other.json http://$ip_other:4567/status/status_$role_other.json && remote_json=1 || remote_json=0
	    else 
		    cp $cs_files_other_path/status_$role_other.log $cs_folder/status_$role_other.log
		    cp $cs_files_other_path/status_$role_other.json $cs_folder/status_$role_other.json && remote_json=1 || remote_json=0
    fi
    #status_other=`grep -o "..$" /home/administrador/obplayer/scripts/noVNC/status_2.json`
    status_other=`grep -Po '"status":..*?[0-9]*' $cs_folder/status_$role_other.json | awk -F': ' '{print $2}'`
    uptime_other=`grep -Po '"uptime":..*?[0-9]*' $cs_folder/status_$role_other.json | awk -F': ' '{print $2}'`

    #save status and compare, if its the same 3 times, can mean the other machine is not really working ok
    #echo " uptime_other es $uptime_other"
    #echo " prev_uptime es $prev_uptime"
    if [ $prev_uptime = 0 ];then
    	prev_uptime=$uptime_other
    fi
    if [ $prev_uptime = $uptime_other ];then
    	counter_status=$(($counter_status + 1))
    	else
        	prev_uptime=$uptime_other
        	counter_status=0
    fi
    #if value is the same x times, can mean the node is not working or this script is not working in that node, we set status_other to 0
    if [ $counter_status -gt 5 ];then
    	echo "Same value for more than $counter_status seconds"
		echo $json_other
		echo `date` "[warning] $hostname Datos no actualizados del otro nodo, cs inactivo en $ip_other" | tee -a $log_path >> $log_host
	        status_other=0
		echo $json_other > $cs_folder/status_$role_other.json

    fi



    #Si no hay status de la otra maquina, entendemos que no esta corriendo y lanzamos la señal de emergencia, solo si nuestro status es 1
    if [ $remote_json = 0 ] || [ $status_other = 0 ]; then
	    echo "No hay datos del otro nodo"
	    echo `date` "[warning] $hostname No hay datos del otro nodo" | tee -a $log_path >> $log_host
	    if [ X$secondary_pid = X ] && [ $status = 1 ] && [ $cs_send_emergency = 1 ]; then
		    echo "No hay datos del otro nodo, lanzando emision secundaria" 
		    echo `date` "[warning] $hostname No hay datos del otro nodo, lanzando emision secundaria" | tee -a $log_path >> $log_host
		    multicat -p 68 -u -U @$multicast_self:$multicast_port $multicast_other:$multicast_port & secondary_pid=$! 
	    fi
    fi	
    echo "secondary_pid " $secondary_pid "status_other " $status_other "cs_send_emergency " $cs_send_emergency
    if [ X$secondary_pid != X ] && ( ( [ $remote_json = 1 ] && [ $status_other = 1 ]) || [ $cs_send_emergency = 0 ] ) ; then
			    echo "Parando la emision de emergencia"
			    echo `date` "[warning] $hostname Parando la emision de emergencia" | tee -a $log_path >> $log_host
			    kill -9 $secondary_pid
			    secondary_pid=''
    fi
    else
        echo `date`  "[warning] $hostname check_services.sh disabled"
        
    fi
    sleep 1
    enabled=`grep -Po 'cs_enabled =..*?[0-9]*' $settings_path | awk -F'= ' '{print $2}'`
done

