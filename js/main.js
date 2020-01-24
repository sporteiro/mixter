//Sebastian Porteiro
//Sebastian Porteiro 2017-20 seba@sebastianporteiro.com
//zeusrs
//javascript controller

var log_autoscroll = false;

//INDEX
$(document).ready(function() {
    // checkLogin();
    checkURL();
    // footer
    serverClock();
    updateClock();

    currentVersion();
    //currentDate();

    getLog();
    // scrollLog();
    // setInterval(clock, 1000);
    getSettings();

    setTimeout(function() { toggleInputOptions(); }, 500);
    setTimeout(function() { toggleOutputOptions(); }, 500);

    checkPipelineAndPrograms();
	  gointer = setInterval(checkPipelineAndPrograms, 5000);

    // Detectar scroll
    setTimeout(function() { floatingButtons()}, 500);
    $('#main_left').scroll(function() { floatingButtons(); });

});

//LOGIN
function checkLogin() {
  try {
    var match = document.cookie.match(new RegExp('(^| )token=([^;]+)'));
    if (match) return match[2];
    else return false;
  }
  catch(error) {
    console.log('no hay sesion');
    return false;
  }
}

function checkURL() {
  if (checkLogin() != false) {
    var match = checkLogin();
    var url = window.location.href;
    var path = window.location.pathname;

    if (url.indexOf(match) < 0) {
      if (path == '/index' || path == '/') { path = '/index'; gotoPath(path); }
      else if (path == '/settingshtml' || path == '/statushtml') { gotoPath(path); }
      else { return false; }
    }
  }
}

function gotoPath(path) {

  if (checkLogin() != false) {
    var match = checkLogin();
    window.location = path + '?' + match;
  } else {
    window.location = '/loginhtml';
  }
}

function logOut()   {
    document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
    window.location = '/';
}

function sendFormAsJSON()   {
    var userinfo = {};
    userinfo['login_username'] = $("#login_username" ).val();
    userinfo['login_password'] = $("#login_password" ).val();
    $.post("/login", JSON.stringify(userinfo),function(response) {
        if (response==403)  {
            alertify.notify('Incorrect username/password', "error", 5);
        }
        else    {
            alertify.notify('Logged succesfully', "success", 5);
            var d=new Date();
            d.setTime(d.getTime()+(24*60*60*1000));

            document.cookie = "token="+response+";  expires="+d.toGMTString();
            setTimeout(function(){ window.location = '/index?'+response; }, 500);
        }
    });
}

function toggle_pass() {
  console.log('pass');
	if($('#login_password').attr('type') == 'password') {
		$('#login_password').attr('type', 'text');
		$('#toggle_pass').removeClass('show_pass').addClass('hide_pass');
	} else {
		$('#login_password').attr('type', 'password');
		$('#toggle_pass').removeClass('hide_pass').addClass('show_pass');
	}
}

function getSettings()    {
    $.getJSON('/settings', function(data) {
        $.each(data,function(key,val) {
            if (key=='input_type' || key=='output_type')  {
               $("#"+val).attr('selected','selected');
            }
            else $("#"+key).val(val);
        });
    });
}

function flushLog() {
  $("#layout_logger_console_content > p").remove();
  APIcall('flush');
}

function APIcall(uri)    {
  $.getJSON(uri, function(data) {
    $.each(data,function(key,val) {
      if (val=="True") $('.led_parent .icon_button.'+key).addClass('active')
      else $('.led_parent .icon_button.' + key).removeClass('active');
    });
  });
  getLog();
  scrollLog();
  updatePipelines(uri);
  
}

function getLog() {
    $.get('/log', function(datados) {
        $("#layout_logger_console_content").html('');
        var lines = datados.split("\n");
        for (nm in lines)	{
	        $("#layout_logger_console_content").append('<p>'+lines[nm]+'</p>');
        }
    });
}

function updatePipelines(uri) {
  $.getJSON('/get_pipelines', function(data) {
	$('#pipelines_list').html('');
	console.log(data)
	var norepeat=[]
    $.each(data,function(key) {
		if (norepeat.includes(key))	{console.log(norepeat);}
		else	{
			norepeat.push(key)
		    $('#pipelines_list').append('<p class="eachpipeline">'+data[key]['name']+': '+data[key]['src']+' --> '+data[key]['sink']+' pipeline: '+data[key]['pipeline_text']+'  <button onclick="killPipeline('+key+')">Kill</button></p> <br />');
		}
    });
  });
}
function killPipeline(id)	{
	    $.post("/kill_pipeline", ''+id+'');
}

function saveReloadPlay()	{
	saveSettings();
	APIcall('reload');
	APIcall('buildpipeline')
}


function checkPipelineAndPrograms() {
    setTimeout(function() { APIcall('checkpipeline'); }, 200);
    setTimeout(function() { APIcall('get_pipelines'); }, 200);
}

function toggleInput() { setTimeout(function() { toggleInputOptions(); }, 200); }

function toggleInputOptions() { 
    $('#options_udp_rtp_src, #options_shm_src, #options_tcp_src').hide();
    var outputOptionSelected = $('#output_type').val();
    console.log(outputOptionSelected);

    if ($('#input_type').val() == 'udp_src' || $('#input_type').val() == 'rtp_src') {
        $('#options_udp_rtp_src').show();
        $('#output_type').html('<option id="window" value="window">window</option>\
                                 <option id="file" value="file">file</option>');
    }
    else if ($('#input_type').val() == 'tcp_src') {
        $('#options_tcp_src').show();
        $('#output_type').html('<option id="window" value="window">window</option>');
    }
    else if ($('#input_type').val() == 'shm_src') {
        $('#options_shm_src').show();
        $('#output_type').html('<option id="window" value="window">window</option>\
                                 <option id="file" value="file">File</option>\
                                 <option id="rtmp" value="rtmp">RTMP</option>\
                                 <option id="tcp" value="tcp">TCP</option>\
                                 <option id="udp" value="udp">UDP</option>\
                                 <option id="mpeg2" value="mpeg2">MPEG2</option>');
    }

    if ($('#output_type option[value=' + outputOptionSelected + ']').length > 0) $('#output_type').val(outputOptionSelected);
    else $('#output_type').val('window');
    toggleOutputOptions()
}

function toggleOutput() { setTimeout(function() { toggleOutputOptions(); }, 200); }

function toggleOutputOptions() {
  $('#options_file, #options_rtmp, #options_tcp, #options_udp').hide();

       if ($('#output_type').val() == 'window');
  else if ($('#output_type').val() == 'file') $('#options_file').show();
  else if ($('#output_type').val() == 'rtmp') $('#options_rtmp').show();
  else if ($('#output_type').val() == 'tcp') $('#options_tcp').show();
  else if ($('#output_type').val() == 'udp') $('#options_udp').show();
  else if ($('#output_type').val() == 'mpeg2') $('#options_udp').show();
  //console.log('output');
}

function toggleButtons(str) {
  console.log(str);
  if ($('.led_parent .icon_button.'+str).hasClass('active')) $('.led_parent .icon_button.' + str).removeClass('active');
  else $('.led_parent .icon_button.'+str).addClass('active')
}

function showChildren(str) {
  $('.led_children.' + str).show();
}

function hideChildren(str) {
  $('.led_children.' + str).hide();
}

function floatingButtons() { 
  if ($('.big_buttons_container').length > 0) {
    var offset = $('.big_buttons_container').offset();
    if (offset.top > $('#main_left').height() - $('.big_buttons_container').height()) $('.big_buttons_container').addClass('floating_buttons');
    else $('.big_buttons_container').removeClass('floating_buttons');
	}
}

function saveSettings()    {
    var settings = {};
        settings['audio_src'] = $("#audio_src" ).val();
        settings['video_src'] = $("#video_src" ).val();
        settings['tcp_ip'] = $("#tcp_ip" ).val();
        settings['tcp_port'] = $("#tcp_port" ).val();
        settings['tcp_ip_src'] = $("#tcp_ip_src" ).val();
        settings['tcp_port_src'] = $("#tcp_port_src" ).val();
        settings['udp_ip'] = $("#udp_ip" ).val();
        settings['udp_port'] = $("#udp_port" ).val();
        settings['udp_ip_src'] = $("#udp_ip_src" ).val();
        settings['udp_port_src'] = $("#udp_port_src" ).val();
        settings['file_path'] = $("#file_path" ).val();
        settings['file_duration'] = $("#file_duration" ).val();
        settings['file_bitrate'] = $("#file_bitrate" ).val();
        settings['file_tmp_path'] = $("#file_tmp_path" ).val();
        settings['rtmp_url'] = $("#rtmp_url" ).val();
        settings['video_format'] = $("#video_format" ).val();
        settings['input_type'] = $("#input_type").val();
        settings['output_type'] = $("#output_type").val();
        console.log('settings to save', settings);
        $.post("/savesettings", JSON.stringify(settings),function(response) {
                alertify.notify(response, "success", 5);
        });
}

// Logger
function toggle_scrollLog() {
  if (log_autoscroll == false) {
    log_autoscroll = true;
    $('#toggle_scroll').removeClass('scroll_active').addClass('scroll_inactive');
    scrollLog();
  } else {
    log_autoscroll = false;
    $('#toggle_scroll').removeClass('scroll_inactive').addClass('scroll_active');
  }

}

function scrollLog() {
  if (log_autoscroll == true && $('#layout_logger_console_content p').length > 0) {
    $('#layout_logger_console_content').animate({scrollTop: $('#layout_logger_console_content').prop("scrollHeight")}, 0);
  }
}

//SETTINGS
function getAllsettings()    {
    $.getJSON('/settings', function(data) {
        createInputsHTML(sortObject(data));
    });
}
function sortObject(o) {
    return Object.keys(o).sort().reduce((r, k) => (r[k] = o[k], r), {});
}
function createInputsHTML(data) {
  var index = 0;
  $("#json_content").html('');
  $.each(data,function(key,val) {
    // console.log(val);
    var id = 'check' + index;
    if (val == 'On') {
      $("#json_content").append('<div class="fieldrow"> <label>'+key+'</label> <input id="'+id+'" class="input_settings" type="checkbox" name="'+key+'" value="On" checked onchange="checkboxChange('+id+');"></input> </div>');
    } else if (val == 'Off') {
      $("#json_content").append('<div class="fieldrow"> <label>'+key+'</label> <input id="'+id+'" class="input_settings" type="checkbox" name="'+key+'" value="Off" onchange="checkboxChange('+id+');"></input> </div>');
    } else {
      $("#json_content").append('<div class="fieldrow"><label>'+key+'</label><input class="input_settings" type="text" name="'+key+'" value="'+val+'"></input></div>');
    }
    index++
  });
}

function checkboxChange(id) {
  if ($(id).is(":checked")) $(id).attr('value', 'On');
  else $(id).attr('value', 'Off');
}

function saveAllsettings()    {
    var settings = {};
        $(".input_settings").each(function() {
            settings[$(this).attr("name")] = $(this).val();
        });
    $.post("/savesettings", JSON.stringify(settings),function(response) { alertify.notify(response, "success", 5);  }  );
}


// Footer
function serverClock()  {
  $.get('/datetime', function(data) {
    var Y = data.substr(0,4);
    var M = data.substr(4,2);
    var D = data.substr(6,2);
    var H = data.substr(9,2);
    var mm = data.substr(12,2);
    var ss = data.substr(15,2);

    date = new Date(Y,M-1,D,H,mm,ss,0);
  });
}

function updateClock() {
  setInterval(function() {
  	date.setSeconds(date.getSeconds() + 1);
  	var time = date.getTime() / 1000;
  	clock(date);
    currentDate(date);
  }, 1000);
}

function currentDate(date) {
  try   {
      var day = date.getDate();
      var month = date.getMonth() + 1;
      var year = date.getFullYear();
      if (day < 10) day = '0' + day;
      if (month < 10) month = '0' + month;
      var current_date = day + '/' + month + '/' + year;
      if ($('#current_date p').text() != current_date) $('#current_date p').text(current_date);
  }
  catch(error) {
    console.log('ERROR: ',error);
  }

}

function clock(date) {
  if (date) {
      if ($('#time_clockHour').text() != date.getHours()) $('#time_clockHour').html((date.getHours() < 10?'0':'') + date.getHours());
      if ($('#time_clockMinute').text() != date.getMinutes()) $('#time_clockMinute').html((date.getMinutes() < 10?'0':'') + date.getMinutes());
      if ($('#time_clockSecond').text() != date.getSeconds()) $('#time_clockSecond').html((date.getSeconds() < 10?'0':'') + date.getSeconds());
    }
}

function currentVersion() {
	$.get('/VERSION', function(data) {
		$('#current_version').append('<p>ver. ' + data + '</p>');
	});
}
