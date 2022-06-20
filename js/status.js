/* Sebastian Porteiro para ITER
codigo para mostrar los datos del script check_status.sh
se cargan los datos desde los .json que genera cada nodo de TDT y los archivos de logs
*/

MX.Status = function() {

}

var cs_folder;
var gointer;
var snap;

var role;
var emergency_config={1:0,2:0};
var node_real_status={1:0,2:0};

var cpu_1_percent = 0;
var cpu_2_percent = 0;
var ram_1_percent = 0;
var ram_2_percent = 0;
var shm_1_percent = 0;
var shm_2_percent = 0;

var lines_data = {};

var lines_increase = {
    'data_1': {x:0,y:0},
    'data_2': {x:0,y:0},
    'data_3': {x:0,y:0},
    'data_4': {x:0,y:0},
};

var lines_increase_e = {
    'data_1': {x:0,y:0},
    'data_2': {x:0,y:0},
    'data_3': {x:0,y:0},
    'data_4': {x:0,y:0},
};

MX.Status.main = function() {
    MX.Status.getCsfolder();
	MX.Status.updateData();
   	MX.Status.updateThumb();
	clearInterval(MX.Status.gointer, snap);
	MX.Status.gointer = setInterval(MX.Status.updateData, 1000);
	MX.Status.snap = setInterval(MX.Status.updateThumb, 10000);
	// Fecha y version en footer
	MX.currentDate();
	MX.currentVersion();
}
//path to .log and .json of self and the other node
MX.Status.getCsfolder = function() {
    $.getJSON("/settings", function(data) {
        urlSplitted = data['cs_folder'].split("/"),
        path = urlSplitted[urlSplitted.length-1];
        cs_folder = "status/"+path;
    });
}

MX.Status.updateData = function() {
    MX.Status.updateStatus();
    MX.Status.updateLog();
    MX.Status.animateMarker();
}

MX.Status.updateStatus = function() {
    MX.Status.getStatus(1);
    MX.Status.getStatus(2);
}

MX.Status.updateThumb = function() {
    MX.Status.getThumb(1);
    MX.Status.getThumb(2);
}

MX.Status.updateLog = function() {
    MX.Status.getLog(1);
    MX.Status.getLog(2);
}

//pasar los segundos a dd hh:mm:ss
MX.Status.friendlytime = function(seconds) {
	var seconds = parseInt(seconds);
	var days = Math.floor(seconds / (3600*24));
	seconds -= days*3600*24;
	var hrs = Math.floor(seconds / 3600);
	seconds -= hrs*3600;
	var mnts = Math.floor(seconds / 60);
	seconds -= mnts*60;
	return (days+" Días, "+(hrs<10?'0':'')+hrs+":"+(mnts<10?'0':'')+mnts+":"+(seconds<10?'0':'')+seconds);
}

//if user is not logged in, he can get scheme from status, but only that
MX.Status.showSchemeifNotLogin = function() {
    if (MX.checkLogin() == false ) {
        $('#modeA').addClass('hidden');
        $('#modeB').removeClass('hidden');
        $("#mode_button").addClass('hidden');
        $("#footer_box_left").children().addClass('hidden');
        $("#footer_box_right").addClass('hidden');
        MX.Status.svgSize();
    } else {
        if (window.location.pathname=='/scheme') MX.Status.statusViewMode();
    }
}

//cambiar el id del body para ajustar el estilo segun el rol de la maquina
MX.Status.changeBodyId = function() {
	$('body').attr('id', role);
	$('#header_role').html(role);
}

MX.Status.getThumb = function(index) {
    var snap_path = cs_folder+'/thumb_'+index+'.jpg';
    var snap_url = 'url("'+snap_path+'")';
    console.log(snap_url);
    var w = $('.box_back').css('width');
    var h = $('.box_back').css('height');
    $('#box_'+index+'_r image').css({ 'width':w, 'height':h, 'object-fit': 'cover' }).attr('xlink:href', snap_path);
    // $('#box_'+index+'_r image').css({ 'width':w, 'height':h, 'background-image':snap_url, 'background-size': 'cover' });
}

//Mostrar los datos de cada uno de los MX.Status.json que se generan en las maquinas de TDT
MX.Status.getStatus = function(index)    {
	//Para cada uno de los status que haya, hay que crear un div y poner los valores solo si son diferentes a los que habia
	//var json_uri = 'status_'+index+'.json?t=' + (new Date());

    var json_uri = cs_folder+'/status_'+index+'.json';
	$.getJSON(json_uri, function(data) {
		$.each(data,function(key,val) {
			//comprobar si soy la maquina principal
			if (key=="ip_main") {
				if (val==window.location.hostname)	{ role='main'; }
				else	{ role='backup'; }
				MX.Status.changeBodyId();
			}
			//si el estatus es 1 cambiar la clase, si no, es que algo va mal o no termino de cargar
			if (key=="status") {
				if (val==0)	{
					$("#hostname_"+index+"_title").removeClass('statusOK').addClass('statusKO');
					$("#lines_"+index+"_active").css("stroke","#a4721d");
					node_real_status[index] = 0;
					// $("#box_"+index+"_s rect").css('fill','#a4721d');
                    $("#box_"+index+"_s").css('fill','#a4721d');
				}
				else if (val==1)	{
					node_real_status[index] = 1;
					$("#hostname_"+index+"_title").removeClass('statusKO').addClass('statusOK');
					// $("#box_"+index+"_s rect").css('fill','#1b945b');
                    $("#box_"+index+"_s").css('fill','#1b945b');
					$("#lines_"+index+"_active").css("stroke","#61f1ad");

					if ($("#role_"+index+"_title").text()==1)	{
						$("#hostname_"+index+"_title").addClass('main_live');
					}
					else {
						$("#hostname_"+index+"_title").removeClass('main_live');
					}
				}
			}
			//si es hostname, colocarlo en un h2
			if (key=="hostname") {
				if ($("#"+key+"_"+index+"_title").length==0)	{
	   			$("#status_container_"+index).prepend("<div id='"+key+"_"+index+"_title'><h2>"+val+"</h2></div>");
					// $("#status_container_"+index).append("<div id='buttons_'" + index + " class='container_buttons'><button class='icon_button suicide' onclick=suicide('"+val+"')></button></div>");
					$("#box_"+index+"_s .box_title_s").text(val);
				}
				else {
					if ($("#"+key+"_"+index+"_title").text()!=val)	{
						$("#"+key+"_"+index+"_title").html("<h2>"+val+"</h2>");
					}
				}
    		}

			if (key=="uptime") {
				if ($("#"+key+"_"+index).length==0)	{
	       			$("#status_container_data_"+index).append("<div id='"+key+"_"+index+"'><span class='element_title'>"+key+"</span><span class='element_value' id='"+key+"_"+index+"_value'>"+MX.Status.friendlytime(val)+"</span></div>");

				}
                else if (val==0) {
                    for (n in lines_data['lines_'+index])   {
                        lines_data['lines_'+index][n]['x'] = 0;
                    }

                }
				else {
					if ($("#"+key+"_"+index+"_value").text()!=MX.Status.friendlytime(val))	{
						$("#"+key+"_"+index+"_value").html(MX.Status.friendlytime(val));

                        //show some movement to see if its working
                        for (n in lines_data['lines_'+index])   {
                            lines_data['lines_'+index][n]['x'] += lines_increase[n]['x'];
                        }

                        $("#box_"+index+"_s .box_uptime").text(MX.Status.friendlytime(val)); // Zeus
					}
                // else {
                // lines_data['lines_'+index] = 0 - lines_increase;
                // }
				}
            }
			//Si la emision de emergencia esta activada, tenemos que mostrar algo
			else if (key=="emergency") {
				index_other = index;
				index_other = index_other == 1 ? index_other=2 : index_other = 1;

				if (val==1) {
					val='Emision suplementaria activada';
					$("#"+key+"_"+index+"_value").parent('div').removeClass('emergency_off').addClass('emergency_on');
					$("#lines_"+index+"_e_active").css("stroke","#61f1ad");

                    for (n in lines_data['lines_'+index+'_e'])   {

                        // lines_data['lines_'+index+ '_e'][n]['x'] += lines_increase[n]['x'];
                        lines_data['lines_'+index+ '_e'][n]['x'] += lines_increase_e[n]['x'];

                        // Zeus Provisional
                        // if (index==1)  lines_data['lines_'+index+ '_e'][n]['y'] += lines_increase[n]['y'];
                        // else lines_data['lines_'+index+ '_e'][n]['y'] -= lines_increase[n]['y'];

                    }

					//show real status of node in scheme mode
					if (node_real_status[index_other] == 1)	{
						// $("#box_"+index_other+"_r rect").css('fill','#c11616');
                        $("#box_"+index_other+"_r .box_back, #box_"+index_other+"_r .box_stand").css('fill','#1b945b'); // Zeus
                        $("#box_"+index_other+"_r .box_overlay").addClass('checkers'); // Zeus
        			} else {
                        // $("#box_"+index_other+"_r rect").css('fill','#1b945b');
                        $("#box_"+index_other+"_r .box_back, #box_"+index_other+"_r .box_stand").css('fill','#1b945b'); // Zeus
                        $("#box_"+index_other+"_r .box_overlay").removeClass('checkers'); // Zeus
                    }

				} else	{

                    for (n in lines_data['lines_'+index+'_e'])   {
                        lines_data['lines_'+index+'_e'][n]['x'] = 0;
                        if (index==1)  lines_data['lines_'+index+ '_e'][n]['y'] = 0;
                        else lines_data['lines_'+index+ '_e'][n]['y'] = linesHeight;
                    }

					//show real status of node in scheme mode
					if (node_real_status[index_other] == 0)	{
						$("#box_"+index_other+"_r .box_back, #box_"+index_other+"_r .box_stand").css('fill','#222');
					} else {
                        $("#box_"+index_other+"_r .box_back, #box_"+index_other+"_r .box_stand").css("fill","#1b945b");
                    }

					val='';
					$("#"+key+"_"+index+"_value").parent('div').removeClass('emergency_on').addClass('emergency_off');
					$("#lines_"+index+"_e_active").css("stroke","None");
				}

				if ($("#"+key+"_"+index+"_value").length==0)	{
		   		    $("#status_container_"+index).append("<div class='emergency_status'><span id='"+key+"_"+index+"_value'>"+val+"</span></div>");
				} else {
					if ($("#"+key+"_"+index+"_value").text()!=val)	{
						$("#"+key+"_"+index+"_value").html(val);
					}
				}
    		}
					//si el campo es la ip propia, mostrar el boton de suicidar el sistema
			else if (key=="ip_self") {

				if ($("#"+key+"_"+index+"_value").length==0)	{

					MX.Status.getStatusSettings(val,index);
					$("#status_container_data_"+index).append("<div id='"+key+"_"+index+"'><span class='element_title'>"+key+"</span><span class='element_value' id='"+key+"_"+index+"_value'>"+val+"</span></div>");
					$("#hostname_"+index+"_title").append("<div id='buttons_"+index+"' class='container_buttons'><button class='icon_button suicide cs_toggle' onclick=MX.Status.suicide('"+val+"') title='"+msg[lang]['suicide']+' '+val+"' ></button>");

                    $("#box_"+index+"_s .box_ipself").text(val); // Zeus

				} else {

					if ($("#"+key+"_"+index+"_value").text()!=val)	{
						$("#"+key+"_"+index+"_value").html(val);
                        $("#box_"+index+"_s .box_ipself").text(val); // Zeus
					}
				}
			}

			else if (key=="cpu_usage") {

				var cpu_usage = val.split("/");
				var cpu_used = cpu_usage[0];
                var cpu_total = cpu_usage.pop();

				if ($("#"+key+"_"+index).length==0)	{
	   			    $("#status_container_data_"+index).append("<div id='"+key+"_"+index+"'><span class='element_title'>"+key+"</span><span class='element_value' id='"+key+"_"+index+"_value'>"+val+"</span></div>");
                    $("#box_"+index+"_s .box_cpu_usage").text('CPU: ' + val); // Zeus
					MX.Status.sizeAndPaintBar('cpu',index,cpu_used,cpu_total);

				} else {
					if ($("#"+key+"_"+index+"_value").text()!=val)	{
						$("#"+key+"_"+index+"_value").html(val);
                        $("#box_"+index+"_s .box_cpu_usage").text('CPU: ' + val);
						MX.Status.sizeAndPaintBar('cpu',index,cpu_used,cpu_total);
					}
				}
			}

			else if (key=="ram_usage") {

				var ram_usage = val.split("/");
				var ram_used = MX.Status.humanToBytes(ram_usage[0]);
                var ram_total = MX.Status.humanToBytes(ram_usage[1]);

				if ($("#"+key+"_"+index).length==0)	{
	   			    $("#status_container_data_"+index).append("<div id='"+key+"_"+index+"'><span class='element_title'>"+key+"</span><span class='element_value' id='"+key+"_"+index+"_value'>"+val+"</span></div>");
                    $("#box_"+index+"_s .box_ram_usage").text('RAM: ' + ram_usage[0] + '/' + ram_usage[1]); // Zeus
					MX.Status.sizeAndPaintBar('ram',index,ram_used,ram_total);

				} else {
					if ($("#"+key+"_"+index+"_value").text()!=val) {
						$("#"+key+"_"+index+"_value").html(val);
                        $("#box_"+index+"_s .box_ram_usage").text('RAM: ' + ram_usage[0] + '/' + ram_usage[1]); // Zeus
						MX.Status.sizeAndPaintBar('ram',index,ram_used,ram_total);
					}
				}
			}

			else if (key=="shm_usage") {

				var shm_usage = val.split("/");
				var shm_used = MX.Status.humanToBytes(shm_usage[0]);
                var shm_total = MX.Status.humanToBytes(shm_usage[1]);

				if ($("#"+key+"_"+index).length==0)	{
	   			    $("#status_container_data_"+index).append("<div id='"+key+"_"+index+"'><span class='element_title'>"+key+"</span><span class='element_value' id='"+key+"_"+index+"_value'>"+val+"</span></div>");
                    $("#box_"+index+"_s .box_shm_usage").text('SHM: ' + shm_usage[0] + '/' + shm_usage[1]);
					MX.Status.sizeAndPaintBar('shm',index,shm_used,shm_total);
				} else {
					if ($("#"+key+"_"+index+"_value").text()!=val)	{
						$("#"+key+"_"+index+"_value").html(val);
                    	$("#box_"+index+"_s .box_shm_usage").text('SHM: ' + shm_usage[0] + '/' + shm_usage[1]);
						MX.Status.sizeAndPaintBar('shm',index,shm_used,shm_total);
					}
				}
			}

  			//el resto de los campos, recargar solo si el valor cambia
	   		else {
				if ($("#"+key+"_"+index).length==0)	{
		 			$("#status_container_data_"+index).append("<div id='"+key+"_"+index+"'><span class='element_title'>"+key+"</span><span class='element_value' id='"+key+"_"+index+"_value'>"+val+"</span></div>");
				} else {
					if ($("#"+key+"_"+index+"_value").text()!=val)	{
						$("#"+key+"_"+index+"_value").html(val);
					}
				}
	  		}
		});
	});
}
//Mostrar el archivo de logs que corresponda a cada status
MX.Status.getLog = function(index) {
	//$.get('status_'+ index +'.log', function(datados) {
    $.get(cs_folder+'/status_'+index+'.log', function(datados) {
		$("#layout_logger_console_content_"+index).html('');
		var lines = datados.split("\n");
		for (nm in lines)	{
			//console.log('lineas' + nm);
			$("#layout_logger_console_content_"+index).append('<p>'+lines[nm]+'</p>');
		}
	});
}
//Mostrar una descripcion de cada programa y una captura
MX.Status.showInfo = function(application)	{
	var warning;
	if (role=='backup')	{
		warning='<span id="warning">¡Advertencia!</span><span id="warning_message">Está usted en modo backup, los cambios pueden perder efecto al volver al modo main</span>';
	}
	else	{ warning=''; }
	$("#app_info_text").html(warning+msg[lang][application]);
	$("#app_snapshot").css('background-image','url(img/'+application+'.png)');
}


//llamar al Killall tail de brave y al killall tail propio. Se encarga playiter
MX.Status.suicide = function(hostname) {
    console.log('Intentando suicidar el sistema '+ hostname);
    if (MX.checkLogin()!=false) {
        var token =  MX.checkLogin();
        var url = "http://"+hostname+":4567/suicide";
        $.post(url, '{"token":"'+token+'"}',function(response) {
            console.log('Suiciding ',response);
        });
    }
}

//FIXME en desuso
// MX.Status.saveStatusSettings = function(settings)    {
//     $.post("/savesettings", JSON.stringify(settings),function(response) { alertify.notify(response, "success", 5);  }  );
// }


MX.Status.toggleSettings = function(key,val,ip,role_id)    {
    //intercambiar el valor, si es 1 poner o y viceversa
    val = val == 1 ? val=0 : val = 1;
    setting = '{"'+key+'":"'+val+'"}';
    $.post("http://"+ip+":4567/savesettings",setting,function(response) { alertify.notify(response, "success", 5);  }  );
    MX.Status.getStatusSettings(ip,role_id);
}

MX.Status.bothEmergency = function (on_off,ip_main,ip_backup,ip,role_id)  {
    $.post("http://"+ip_main+":4567/savesettings",'{"cs_send_emergency":'+on_off+'}',function(response) { alertify.notify(response, "success", 5);  }  );
    $.post("http://"+ip_backup+":4567/savesettings",'{"cs_send_emergency":'+on_off+'}',function(response) { alertify.notify(response, "success", 5);  }  );
    // setTimeout(function() { location.reload() }, 1000);
    emergency_config={1:0,2:0};
    if (role_id==1) {        setTimeout(function() { MX.Status.getStatusSettings(ip,role_id);MX.Status.getStatusSettings(ip_backup,2)}, 1000); }
    else { setTimeout(function() { MX.Status.getStatusSettings(ip_main,1);MX.Status.getStatusSettings(ip,role_id);}, 1000); }
}

MX.Status.toggleEmergency = function (ip,role_id,ip_main,ip_backup)  {
    $.post("http://"+ip+":4567/savesettings",'{"cs_send_emergency":1}',function(response) { alertify.notify(response, "success", 5);  }  );
    emergency_config={1:0,2:0};
    if (role_id==1) {
        $.post("http://"+ip_backup+":4567/savesettings",'{"cs_send_emergency":0}',function(response) { alertify.notify(response, "success", 5);  }  );
        setTimeout(function() { MX.Status.getStatusSettings(ip,role_id);MX.Status.getStatusSettings(ip_backup,2)}, 1000);
    } else {
        $.post("http://"+ip_main+":4567/savesettings",'{"cs_send_emergency":0}',function(response) { alertify.notify(response, "success", 5);  }  );
        setTimeout(function() { MX.Status.getStatusSettings(ip_main,1);MX.Status.getStatusSettings(ip,role_id);}, 1000);
    }
}

MX.Status.toggleRoles = function(ip,role_id)    {

	//console.log("toggleRoles");
	var settings = {};
	$.getJSON("http://"+ip+":4567/settings", function(data) {
		//we switch the settings
		settings['cs_ip_main'] = data['cs_ip_backup'];
		settings['cs_ip_backup'] = data['cs_ip_main'];
		settings['cs_hostname_main'] = data['cs_hostname_backup'];
		settings['cs_hostname_backup'] = data['cs_hostname_main'];
		//To avoid a check_services reboot, we put cs_enabled to 0
		settings['cs_enabled'] = 0;
		//and make a copy for other server, so far settings are same for both
		var settings_2 = $.extend({}, settings);

		//then we toggle the udp_ip in both
		if (data['udp_ip']==data['cs_multicast_backup'])	{
			settings['udp_ip'] = data['cs_multicast_backup'];
			settings_2['udp_ip'] = data['cs_multicast_main'];
			$.post("http://"+data['cs_ip_main']+":4567/savesettings", JSON.stringify(settings),function(response) { alertify.notify(response, "success", 5);  }  );
			$.post("http://"+data['cs_ip_backup']+":4567/savesettings", JSON.stringify(settings_2),function(response) { alertify.notify(response, "success", 5);  }  );
		}
		else {
			settings['udp_ip'] = data['cs_multicast_backup'];
			settings_2['udp_ip'] = data['cs_multicast_main'];
			$.post("http://"+data['cs_ip_main']+":4567/savesettings", JSON.stringify(settings),function(response) { alertify.notify(response, "success", 5);  }  );
			$.post("http://"+data['cs_ip_backup']+":4567/savesettings", JSON.stringify(settings_2),function(response) { alertify.notify(response, "success", 5);  }  );
		}

    //reload, means gstreamer pipeline is stopped and lauched again
    $.post("http://"+data['cs_ip_main']+":4567/reload", {},function(response) { alertify.notify(response, "success", 5);  }  );
    $.post("http://"+data['cs_ip_backup']+":4567/reload", {},function(response) { alertify.notify(response, "success", 5);  }  );
    alertify.alert(msg[lang]['changing_roles']);
    //finally we try to make check_services.sh work again
    setTimeout(function() { delayedCsenabled(data['cs_ip_main'], data['cs_ip_backup']); }, 10000);

	});

}

MX.Status.delayedCsenabled = function(ip_main, ip_backup)     {
    console.log("cs_enabled");
    $.post("http://"+ip_main+":4567/savesettings", '{"cs_enabled":1}',function(response) { alertify.notify(response, "success", 5);  }  );
    $.post("http://"+ip_backup+":4567/savesettings",'{"cs_enabled":1}',function(response) { alertify.notify(response, "success", 5);  }  );
    setTimeout(function() { location.reload() }, 3000);
    alertify.notify(msg[lang]['reloading'], "warning", 3);
}

MX.Status.getStatusSettings = function(ip,role_id) {
    console.log('get status');
    $.getJSON("http://"+ip+":4567/settings", function(data) {
        $('#buttons_emergency_0').remove();
        $('#buttons_emergency_4').remove();

        $.each(data,function(key,val) {
	        $('#buttons_'+role_id+'_'+key).remove();

            if (key=='cs_enabled')  {
             	$("#buttons_"+role_id).prepend("<button class='icon_button' id='buttons_"+role_id+"_"+key+"' onclick=MX.Status.toggleSettings('cs_enabled',"+val+",'"+ip+"',"+role_id+") title='"+msg[lang]['cs_on_off']+"'></button>");
                $('#buttons_'+role_id+'_'+key).addClass('cs_enabled'+val);
                $('#status_container_'+role_id).removeClass().addClass('status_container enabled'+val);
            }

            if (key=='cs_send_emergency')  {

             	$("#buttons_emergency").prepend("<button class='big_icon_button' id='buttons_"+role_id+"_"+key+"' onclick=MX.Status.toggleEmergency('"+ip+"',"+role_id+",'"+data['cs_ip_main']+"','"+data['cs_ip_backup']+"') title='"+msg[lang]['emergency_on_off']+ip+"'  onmouseover=MX.Status.showInfo('emergency_"+role_id+"')></button>");
                $('#buttons_'+role_id+'_'+key).addClass('cs_emergency_'+role_id+' '+'cs_toggle');

                $("#buttons_emergency").append("<button class='big_icon_button cs_emergency_0' id='buttons_emergency_0' onmouseover=MX.Status.showInfo('emergency_0') onclick=MX.Status.bothEmergency(0,'"+data['cs_ip_main']+"','"+data['cs_ip_backup']+"','"+ip+"',"+role_id+") title='"+msg[lang]['disable_both']+"')></button>");
                $("#buttons_emergency").prepend("<button class='big_icon_button cs_emergency_4' id='buttons_emergency_4' onmouseover=MX.Status.showInfo('emergency_4') onclick=MX.Status.bothEmergency(1,'"+data['cs_ip_main']+"','"+data['cs_ip_backup']+"','"+ip+"',"+role_id+") title='"+msg[lang]['enable_both']+"')></button>");

                //show which option is selected according to emergency configuration
                emergency_config[role_id]=val;
                var emerg_conf = emergency_config[1]+emergency_config[2];

                console.log(emerg_conf);
                $('#buttons_emergency .big_icon_button').removeClass('active');
            		$("#lines_1_e_cfg, #lines_2_e_cfg").attr("stroke-dasharray","10,10");
            		$("#lines_1_e_cfg, #lines_2_e_cfg").css("stroke","None");

                if (emerg_conf==00) {
                  $('#buttons_emergency_0').addClass('active');
                }
                else if (emerg_conf==11) {
                  $('#buttons_emergency_4').addClass('active');
		              $("#lines_1_e_cfg, #lines_2_e_cfg").css("stroke","#000");
                }
                else if (emerg_conf==10) {
                  $('#buttons_1_cs_send_emergency').addClass('active');
		              $("#lines_1_e_cfg").css("stroke","#000");
                }
                else if (emerg_conf==01) {
                  $('#buttons_2_cs_send_emergency').addClass('active');
		              $("#lines_2_e_cfg").css("stroke","#000");
                }
            }
            if (key=='cs_multicast_main')  {
              $('#button_switch').remove();
             	$("#buttons_emergency").before("<button id='button_switch' class='big_icon_button' onclick=MX.Status.toggleRoles('"+ip+"',"+role_id+") title='"+msg[lang]['switch_roles']+"'></button>");
              $('#button_switch').addClass('cs_switch');
		          $("#box_1_r .box_title_r").text(val); // Zeus
            }
            if (key=='cs_multicast_backup')  {
		           $("#box_2_r .box_title_r").text(val); // Zeus
            }
        });
    });
}

MX.Status.statusViewMode = function() {
	if ($('#modeA').is(':visible')) {
		$('#modeA').addClass('hidden');
		$('#modeB').removeClass('hidden');
		$("#mode_button").removeClass('scheme').addClass('log').html("Log mode");
        window.history.pushState('page2', 'Title', '/scheme');
		MX.Status.svgSize();
	} else {
		$('#modeB').addClass('hidden');
		$('#modeA').removeClass('hidden');
		$("#mode_button").removeClass('log').addClass('scheme').html("Scheme mode");
        window.history.pushState('page2', 'Title', '/statushtml');
	}
}


var square_side = 0;
var b_right = 0;
var b_bottom = 0;
var linesWidth = 0;
var linesHeight = 0;
var hipotenuses = 0;

var rotate1;
var rotate2;


MX.Status.svgSize = function() {

    square_side = $('svg').height() * .5 - 10;
    b_right = $('svg').width() - square_side - 1;
    b_bottom = $('svg').height() - square_side - 1;
    linesWidth = $('svg').width() - square_side * 2 - 40;
    linesHeight = $('svg').height() * .5 + 10;
    // hipotenuses = Math.hypot(linesHeight, linesWidth);
    hipotenuses = Math.sqrt(Math.pow(linesHeight, 2) + Math.pow(linesWidth, 2));

    // Zeus tienen q sumar 10 para q cuadre
    lines_increase['data_1']['x'] = linesWidth * .25;
    lines_increase['data_2']['x'] = linesWidth * .2;
    lines_increase['data_3']['x'] = linesWidth * .1;
    lines_increase['data_4']['x'] = linesWidth * .5;

    // lines_increase['data_1']['y'] = linesHeight * .25;
    // lines_increase['data_2']['y'] = linesHeight * .2;
    // lines_increase['data_3']['y'] = linesHeight * .1;
    // lines_increase['data_4']['y'] = linesHeight * .5;

    lines_increase_e['data_1']['x'] = hipotenuses * .25;
    lines_increase_e['data_2']['x'] = hipotenuses * .2;
    lines_increase_e['data_3']['x'] = hipotenuses * .1;
    lines_increase_e['data_4']['x'] = hipotenuses * .5;

    // console.log(lines_increase, lines_increase_e);

    var server_header = square_side * .12;
    var font_header = server_header * .5;
    var tv_height = square_side * 9 / 16;
    var tv_top = (square_side - tv_height) * .5;

	$("#box_1_s").attr({ 'transform':'translate(1 1)' });
	$("#box_2_s").attr({ 'transform':'translate(1 ' + b_bottom + ')' });

	$("#box_1_r").attr({ 'transform':'translate(' + b_right + ' 1)' });
	$("#box_2_r").attr({ 'transform':'translate(' + b_right + ' ' + b_bottom + ')' });

	$("#box_1_s .box, #box_2_s .box").attr({ 'rx':10, 'ry':10, 'width': square_side, 'height': square_side });
    $("#box_1_r .box, #box_2_r .box, #box_1_r image, #box_2_r image").attr({ 'rx':10, 'ry':10, 'width': square_side, 'height': tv_height, 'transform':'translate(0 ' + tv_top + ')' });

    console.log('square_side: ', square_side);
    $("#screenView rect").attr({ 'rx':10, 'ry':10, 'width': square_side, 'height': tv_height });

    // $(".led").attr({ 'cx': server_header * .5, 'cy': server_header * .5, 'r': server_header * .25  });
    $(".box_line").attr({ 'x1': 0, 'y1': server_header, 'x2': square_side, 'y2': server_header });
    $(".box_title_s").attr({ 'x': square_side - 20, 'y': server_header - font_header * .6 }).css('font-size', font_header);
    $(".box_title_r").attr({ 'x': square_side - 20, 'y': tv_height * .5 + 10 }).css('font-size', font_header);

    $('.server_box').each(function() { // Zeus aqui
        var index = 0;
        var lineHeight = square_side * .1;

        $(this).children('.server_info').each(function() {
            index++;
            var posY = server_header + 10 + lineHeight * index;

            $(this).children().each(function() {
                var childrenTag = $(this).prop("tagName");
                if (childrenTag == 'text') {

                    $(this).attr({ 'x': 20, 'y': posY }).css({ 'font-size': font_header, 'line-height': lineHeight });

                } else if (childrenTag == 'rect') {


                    if ($(this).hasClass('bar_total')) var percent = 100.1;
                    if ($(this).hasClass('bar_used')) {
                             if ($(this).attr('id') == 'cpu_used_1') var percent = cpu_1_percent;
                        else if ($(this).attr('id') == 'ram_used_1') var percent = ram_1_percent;
                        else if ($(this).attr('id') == 'shm_used_1') var percent = shm_1_percent;
                        else if ($(this).attr('id') == 'cpu_used_2') var percent = cpu_2_percent;
                        else if ($(this).attr('id') == 'ram_used_2') var percent = ram_2_percent;
                        else if ($(this).attr('id') == 'shm_used_2') var percent = shm_2_percent;
                    }

                    var width = percent * (square_side - 20) / 100;

                    // $(this).attr({ 'x': 10, 'y': posY - 25, 'height': 30, 'width': square_side - 20 });
                    $(this).attr({ 'x': 10, 'y': posY - lineHeight * .6, 'height': lineHeight * .7, 'width': width });
                }
            });
        });
    });

    // $('.cpu_used').attr({ 'x': 20, 'width': square_side - 80, 'height': 20 });

    // $(".box_stand_1").attr({ 'x1': 120, 'y1': square_side - 140, 'x2': square_side - 120, 'y2': square_side - 140 });

    $(".box_stand").attr({ 'height':15, 'width':square_side - 160, 'x': 80, 'y': tv_top + tv_height + 15 });

	var left_end = square_side + 20;
	var right_end = $('svg').width() - square_side - 20;
	var top_end = square_side * .5;
	var bottom_end = $('svg').height() - square_side * .5;

    // Calcular ángulo
    var alfa = Math.atan2(linesHeight - 0, linesWidth - 0);
    var deg = (alfa * 360) / (2 * Math.PI);
    rotate1 = 'rotate(' + deg + 'deg)';
    rotate2 = 'rotate(' + -1 * deg + 'deg)';

    $('#lines_1').attr({ 'transform':'translate(' + left_end + ' ' + top_end + ')', 'width': linesWidth, 'height': linesHeight });
    $("#lines_1_active").attr({ 'x1': 0, 'y1': 0, 'x2': linesWidth, 'y2': 0 });
    $('path[id*="lines_1_data_"]').attr({ 'x': 0, 'y': 0 - 10 });

    $('#lines_1_e').attr({ 'transform':'translate(' + left_end + ' ' + top_end + ')', 'width': linesWidth, 'height': linesHeight });
    $("#lines_1_e_cfg").attr({ 'x1': 0, 'y1': 0, 'x2': linesWidth, 'y2': linesHeight });
    $("#lines_1_e_active").attr({ 'x1': 0, 'y1': 0, 'x2': linesWidth, 'y2': linesHeight });
    $('path[id*="lines_1_e_data_"]').attr({ 'x': 0, 'y': 0 - 10 });

    $('#lines_2_e').attr({ 'transform':'translate(' + left_end + ' ' + top_end + ')', 'width': linesWidth, 'height': linesHeight });
    $("#lines_2_e_cfg").attr({ 'x1': 0, 'y1': linesHeight, 'x2': linesWidth, 'y2': 0 });
    $("#lines_2_e_active").attr({ 'x1': 0, 'y1': linesHeight, 'x2': linesWidth, 'y2': 0 });
    $('#lines_2_e_path').attr({ 'transform':'translate(0 ' + linesHeight + ')' });
    $('path[id*="lines_2_e_data_"]').attr({ 'x': 0, 'y': linesHeight });

    $('#lines_2').attr({ 'transform':'translate(' + left_end + ' ' + bottom_end + ')', 'width': linesWidth, 'height': linesHeight });
    $("#lines_2_active").attr({ 'x1': 0, 'y1': 0, 'x2': linesWidth, 'y2': 0 });
    $('path[id*="lines_2_data_"]').attr({ 'x': 0, 'y': 0 - 10 });

    MX.Status.create_data_line(4);

    MX.Status.updateThumb();
}

MX.Status.create_data_line = function(data_squares_number) {
    $('.line').each(function() {
		var tempObj = {};
		var tempObj2 = {}
    var name = $(this).prop('id');

		for (i=1; i<=data_squares_number; i++) {
			var index = 'data_'+i;
			tempObj3 = {[index] :{'x':0,'y':0}};
			$.extend(tempObj2, tempObj3);
		}
		tempObj = {[name] :tempObj2};
		$.extend(lines_data, tempObj);
	});
}

MX.Status.animateMarker = function() {
    // console.log("lines_data ",lines_data);

    $.each(lines_data, function (key, val) {

        $.each(val, function (key2, val2) {

            var increase_x = 0;
            // var increase_y = 0;

            if (key == 'lines_1' || key == 'lines_2') {
                increase_x = lines_increase[key2]['x'];
                // increase_y = lines_increase[key2]['y'];
            } else if (key == 'lines_1_e' || key == 'lines_2_e') {
                increase_x = lines_increase_e[key2]['x'];
                // increase_y = lines_increase_e[key2]['y'];
            }

            if (key == 'lines_1' || key == 'lines_2') {
                if (lines_data[key][key2]['x'] >= linesWidth + increase_x || lines_data[key][key2]['x'] <= 0) $('#' + key + '_' + key2).hide();
                else $('#' + key + '_' + key2).show();
            } else if (key == 'lines_1_e' || key == 'lines_2_e') {
                if (lines_data[key][key2]['x'] >= hipotenuses + increase_x || lines_data[key][key2]['x'] <= 0) $('#' + key + '_' + key2).hide();
                else $('#' + key + '_' + key2).show();
            }

            if (key == 'lines_1' || key == 'lines_2') {
                if (lines_data[key][key2]['x'] >= linesWidth + increase_x)  {
                    lines_data[key][key2]['x'] = 0;
                    // if (key=='lines_1_e')  { lines_data[key][key2]['y'] = 0; }
                    // else if (key=='lines_2_e')  { lines_data[key][key2]['y'] = linesHeight; }
                }
            }

            if (key == 'lines_1_e' || key == 'lines_2_e') {
                if (lines_data[key][key2]['x'] >= hipotenuses + increase_x)  {
                    lines_data[key][key2]['x'] = 0;
                    // if (key=='lines_1_e')  { lines_data[key][key2]['y'] = 0; }
                    // else if (key=='lines_2_e')  { lines_data[key][key2]['y'] = linesHeight; }
                }
            }

            var posX = Math.round(lines_data[key][key2]['x'] - 10);
            var posY = Math.round(lines_data[key][key2]['y'] - 10);
            var position = posX + ' ' + posY;

            if (key == 'lines_1_e') $('.lines_1_e_g').css({ "transform": rotate1 });
            if (key == 'lines_2_e') $('.lines_2_e_g').css({ "transform": rotate2 });
            $('#' + key + '_' + key2).attr( 'transform', 'translate(' + position + ')' );

        });

    });

}
MX.Status.humanToBytes = function(humanNotation)	{
    var bytes = '';
    if (humanNotation) {
        var units = humanNotation[humanNotation.length -1];
        var units_value = humanNotation.slice(0, -1);
        var factor = 1000;
        if (units=='G') { bytes = units_value * Math.pow(factor, 3); }
        else if (units=='M') { bytes = units_value * Math.pow(factor, 2); }
        else if (units=='K') { bytes = units_value * factor; }
        else bytes = humanNotation;
    }
    return bytes;
}

MX.Status.sizeAndPaintBar = function(key,index,used,total)	{
	var percent = used / total * 100;
	if (percent > 100) percent = 100;
    MX.Status.savePercent(key, index, percent);
	var width = percent * (square_side - 20) / 100;
	if (percent <= 50) var color = 'rgb( 50, 125, 115)';
	else if (percent > 50 && percent < 80) var color = 'rgb(164, 114,  29)';
	else if (percent >= 80 && percent <= 100) var color = 'rgb(155,  30,  50)';
	$('#' + key + '_total' + '_' + index).attr({ 'width': square_side - 20 });
	$('#' + key + '_used' + '_' + index).attr({ 'data-percent': percent, 'width': width }).css({ 'fill': color });
}

MX.Status.savePercent = function(key, index, percent) {
         if (key == 'cpu' && index == '1') cpu_1_percent = percent;
    else if (key == 'cpu' && index == '2') cpu_2_percent = percent;
    else if (key == 'ram' && index == '1') ram_1_percent = percent;
    else if (key == 'ram' && index == '2') ram_2_percent = percent;
    else if (key == 'shm' && index == '1') shm_1_percent = percent;
    else if (key == 'shm' && index == '2') shm_2_percent = percent;
}

MX.Status.main();


$(document).ready(function() {
	MX.Status.updateData();
    MX.Status.showSchemeifNotLogin()
    MX.Status.svgSize();
});


$(window).on('load', function() {
	MX.Status.main();
    MX.Status.showSchemeifNotLogin()
    MX.Status.svgSize();
});

$(window).resize(function() {
    MX.Status.svgSize();
});
