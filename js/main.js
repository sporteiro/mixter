//Sebastian Porteiro
//20200427
//MIXTER javascript controller
MX = {};
var animation_index = 1;
var log_autoscroll = false;
var pipe_sett = {};
var pipe_data = {};
console.log(pipes_blueprint);

//INDEX
$(document).ready(function() {
    // checkLogin();
    MX.checkURL();
    // footer
    MX.serverClock();
    MX.updateClock();
    MX.currentVersion();

    // MX.currentDate();
    // setInterval(MX.clock, 1000);
    MX.getSettings();

    MX.checkPipelineAndPrograms();
	gointer = setInterval(MX.checkPipelineAndPrograms, 4000);

    // Detectar scroll
    setTimeout(function() { MX.floatingButtons()}, 500);
    $('#main_left').scroll(function() { MX.floatingButtons(); });

});

//LOGIN
MX.checkLogin = function() {
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

MX.checkURL = function() {
    if (MX.checkLogin() != false)  {
        var match = MX.checkLogin();
        var url = window.location.href;
        var path = window.location.pathname;

        if (url.indexOf(match) < 0) {
            if (path == '/index' || path == '/') { path = '/index'; MX.gotoPath(path); }
            else if (path == '/settingshtml' || path == '/statushtml' ) { MX.gotoPath(path); }
            else { return false; }
        }
    }
}

MX.gotoPath = function(path) {
    if (MX.checkLogin() != false) {
        var match = MX.checkLogin();
        window.location = path + '?' + match;
    } else {
        window.location = '/loginhtml';
    }
}

MX.logOut = function() {
    document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
    window.location = '/';
}

MX.sendFormAsJSON = function() {
    var userinfo = {};
    userinfo['login_username'] = $("#login_username" ).val();
    userinfo['login_password'] = $("#login_password" ).val();
    $.post("/login", JSON.stringify(userinfo),function(response) {
        if (response==403)  {
            alertify.notify('Incorrect username/password', "error", 5);
        } else {
            alertify.notify('Logged succesfully', "success", 5);
            var d=new Date();
            d.setTime(d.getTime()+(24*60*60*1000));

            document.cookie = "token="+response+";  expires="+d.toGMTString();
            setTimeout(function(){ window.location = '/index?'+response; }, 500);
        }
    });
}

MX.toggle_pass = function() {
    console.log('pass');
	if($('#login_password').attr('type') == 'password') {
		$('#login_password').attr('type', 'text');
		$('#toggle_pass').removeClass('show_pass').addClass('hide_pass');
	} else {
		$('#login_password').attr('type', 'password');
		$('#toggle_pass').removeClass('hide_pass').addClass('show_pass');
	}
}

MX.getSettings = function(id) {
    $.getJSON('/settings', function(data) {
        pipe_sett = data;
        $.each(data, function(key, val) {
            if (key == 'input_type' || key == 'output_type')  {
                $("#"+val).attr('selected','selected');
            } else {
                $("#"+key).val(val);
            }
        });
    });
}

MX.checkPipelineAndPrograms = function() {
    MX.updateDisplay('checkobplayer');
    MX.updateDisplay('checksnowmix');
    MX.updateDisplay('checkbrave');
    MX.updatePipelines();
    MX.getLog();
    MX.scrollLog();
}

MX.updateDisplay = function(uri) {
    $.getJSON(uri, function(data) {
        $.each(data,function(key,val) {
            if (val=="True") $('.led_parent .icon_button.'+key).addClass('active')
            else $('.led_parent .icon_button.' + key).removeClass('active');
        });
    });
}

MX.toggleButtons = function(str) {
    console.log(str);
    if ($('.led_parent .icon_button.'+str).hasClass('active')) $('.led_parent .icon_button.' + str).removeClass('active');
    else $('.led_parent .icon_button.'+str).addClass('active')
}

MX.showChildren = function(str) {
    $('.led_children.' + str).show();
}

MX.hideChildren = function(str) {
    $('.led_children.' + str).hide();
}

MX.floatingButtons = function() { // Zeus
    if ($('.big_buttons_container').length > 0) {
        var offset = $('.big_buttons_container').offset();
        if (offset.top > $('#main_left').height() - $('.big_buttons_container').height()) $('.big_buttons_container').addClass('floating_buttons');
        else $('.big_buttons_container').removeClass('floating_buttons');
	}
}

MX.restartBrave = function() {
    $.post("http://192.168.53.39:5000/api/restart", '{"config":"current"}');
}


//SETTINGS
MX.getAllsettings = function() {
    $.getJSON('/settings', function(data) {
        MX.createInputsHTML(MX.sortObject(data));
    });
}

MX.sortObject = function(o) {
    return Object.keys(o).sort().reduce((r, k) => (r[k] = o[k], r), {});
}

MX.createInputsHTML = function(data) {
    var index = 0;
    $("#json_content").html('');
    $.each(data,function(key,val) {
    // console.log(val);
        var id = 'check' + index;
        if (val == 'On') {
            $("#json_content").append('<div class="fieldrow"> <label>'+key+'</label> <input id="'+id+'" class="input_settings" type="checkbox" name="'+key+'" value="On" checked onchange="MX.checkboxChange('+id+');"></input> </div>');
        } else if (val == 'Off') {
            $("#json_content").append('<div class="fieldrow"> <label>'+key+'</label> <input id="'+id+'" class="input_settings" type="checkbox" name="'+key+'" value="Off" onchange="MX.checkboxChange('+id+');"></input> </div>');
        } else if (key == 'pipeline_list') {
            $("#json_content").append("<div class='fieldrow'><label>"+key+"</label><textarea class='input_settings' type='text' name='"+key+"'> "+val+" </textarea></div>");
        } else {
            $("#json_content").append("<div class='fieldrow'><label>"+key+"</label><input class='input_settings' type='text' name='"+key+"' value='"+val+"'></input></div>");
        }
        index++
    });
}

MX.checkboxChange = function(id) {
    console.log('MX.checkboxChange. ID: '+ id);
    if ($(id).is(":checked")) $(id).attr('value', 'On');
    else $(id).attr('value', 'Off');
}

MX.saveSettingFromInputs = function() {
    var settings = {};
    $(".input_settings").each(function() {
        if ($(this).is(':visible')) {
            console.log($(this).attr("name"), $(this).val());
            settings[$(this).attr("name")] = $(this).val();
        }
    });
    MX.saveSettings(JSON.stringify(settings));
}

MX.saveSettings = function(settings) {
    // $.post("/savesettings", settings, function(response) {
    //     alertify.notify(response, "success", 5);
    //     $.get('/reload');
    // });

    $.post("/savesettings", settings, function(response) {
        alertify.notify(response, "success", 5);
    }).done(function() {
        //alert( "second success" );
        $.get('/reload');
    });
}

MX.loadPipelines = function() {
    $.get('/reload');
    $.get('/buildmultiplepipelines');
    MX.updatePipelines();
}

MX.updatePipelines = function() {
    $.getJSON('/get_pipelines', function(data) {
    	$('#pipeline_list').html('');
    	console.log(data)
        pipe_data = data; // Zeus

    	var norepeat = []
        $.each(data,function(key) {
    		if (norepeat.includes(key))	{
                console.log(norepeat);
            } else {
    			norepeat.push(key);
                // $('#pipeline_list').append('<div class="eachpipeline"><h3>'+data[key]['name']+'</h2>Input: '+data[key]['src']+'<br />Output: '+data[key]['sink']+'<br /><p class="pipeline_desc invisible"> pipeline: '+data[key]['pipeline_text']+' </p>  <button onclick="showPipelineInfo()">More</button> <button onclick="reconnectPipeline('+key+')">reconnect</button> <button onclick="killPipeline('+key+')">Kill</button></div> ');

                var pipe_id = data[key]['pipeline_id'];
                var pipe_name = data[key]['pipeline_settings']['pipeline_name'];
                var pipe_type = MX.checkVal(data[key]['pipeline_settings']['pipeline_type']);
                var pipe_1_src = MX.checkVal(data[key]['pipeline_settings']['input_1_type']);
                var pipe_2_src = MX.checkVal(data[key]['pipeline_settings']['input_2_type']);
                var pipe_sink = MX.checkVal(data[key]['pipeline_settings']['output_type']);
                var pipeline = '';
                var pipeflow = '';
                var pipebtns = '';

                pipeline += '<p><span class="pipe_name">' + pipe_name + '</span> <span class="pipe_id">(' + pipe_id + ')</span></p>';
                pipeline += '<p>' + pipe_type + '</p>';

                pipeflow += '<p class="pipe_in_1">1. ' + pipe_1_src + '</p>';
                pipeflow += '<p class="pipe_conn"> <span class="flow_1"> > </span> <span class="flow_2"> > </span> <span class="flow_3"> > </span> </p>';
                pipeflow += '<p class="pipe_out">' + pipe_sink + '</p>';
                pipeline += '<div class="pipe_flow">' + pipeflow + '</div>';

                if (pipe_2_src != 'None') pipeline += '<p class="pipe_in_2">2. ' + pipe_2_src + '</p>';

                pipebtns += '<button class="pipe_info icon_button unapproved" onclick="MX.showPipelineInfo(' + key + ')" title="Info"></button>';
                pipebtns += '<button class="pipe_reconn icon_button reconnect" onclick="MX.reconnectPipeline(' + key + ')" title="Reconnect"></button>';
                pipebtns += '<button class="pipe_forward icon_button forward" onclick="MX.forwardPipeline(' + key + ')" title="Forward"></button>';
                pipebtns += '<button class="pipe_kill icon_button kill" onclick="MX.killPipeline(' + key + ')" title="Kill"></button>';
                pipeline += '<div class="pipe_buttons">' + pipebtns + '</div>';

    		    $('#pipeline_list').append('<div class="pipeline">' + pipeline + '</div>');
            }
        });
    });
}

MX.killPipelines = function() {
    $.post('/kill_all_pipelines');
}

MX.savePipelineList = function() {
    var pipelines = {};
    var pipeline_list = {};

    $.each(pipe_data, function(key) {
        var index = 'pipe_' + key;
        pipelines[index] = pipe_data[key]['pipeline_settings'];
    });

    console.log(pipeline_list);
    pipeline_list["pipeline_list"] = JSON.stringify(pipelines);
    MX.saveSettings(JSON.stringify(pipeline_list));
    $.get('/reload');
}

//sebastian we can just rely on translation
MX.checkVal = function(str) {
    if (str!=undefined)   {
        new_str = msg[lang][str];
        if (new_str==undefined){
            new_str=str;
        }
    }
    return new_str;
/*
    var new_str;
    switch(str) {
        // Type
        case 'none_type': new_str = 'None'; break;
        case 'gstreamer': new_str = 'GStreamer'; break;
        case 'ffmpeg': new_str = 'FFmpeg'; break;
        // Inputs
        case 'none_src': new_str = 'None'; break;
        case 'udp_src': new_str = 'UDP'; break;
        case 'rtp_src': new_str = 'RTP'; break;
        case 'tcp_src': new_str = 'TCP'; break;
        case 'shm_src': new_str = 'Shared memory'; break;
        // Outputs
        case 'none_sink': new_str = 'None'; break;
        case 'window_sink': new_str = 'Window'; break;
        case 'file_sink': new_str = 'File'; break;
        case 'rtmp_sink': new_str = 'RTMP'; break;
        case 'tcp_sink': new_str = 'TCP'; break;
        case 'udp_sink': new_str = 'UDP'; break;
        case 'shm_sink': new_str = 'Shared memory'; break;
        case 'mpeg2_sink': new_str = 'MPEG2'; break;

        default:
            new_str = 'Undefined';
    }
    return new_str;
*/
}

MX.animateFlow = function() {
    $(".pipe_conn span").removeClass('invisible');
    $(".flow_" + animation_index).addClass('invisible');
    if (animation_index == 1) animation_index = 3;
    else if (animation_index == 3) animation_index = 1;
}

MX.newPipeline = function() {
    MX.openModalWindow('html/addPipeline.html');
}

MX.togglePipelineType = function() {
    setTimeout(function() { MX.togglePipelineTypeOptions(); }, 200);
}

MX.togglePipelineTypeOptions = function() {
    var in_options_1 = '';
    var in_options_2 = '';

    input_1_type = Object.keys(pipes_blueprint['pipeline_type'][$('#pipeline_type').val()]['input_1_type'])
    input_2_type = Object.keys(pipes_blueprint['pipeline_type'][$('#pipeline_type').val()]['input_2_type'])

    for (n in input_1_type)    {
        var opt_name = msg[lang][input_1_type[n]]
        var opt_name = typeof opt_name != "undefined" ? opt_name : input_1_type[n];
        in_options_1 += '<option value="'+input_1_type[n]+'">'+opt_name+'</option>';
    }
    for (n in input_2_type)    {
        var opt_name = msg[lang][input_2_type[n]]
        var opt_name = typeof opt_name != "undefined" ? opt_name : input_2_type[n];
        in_options_2 += '<option value="'+input_2_type[n]+'">'+opt_name+'</option>';
    }

    $('#input_1_type').html(in_options_1);
    $('#input_2_type').html(in_options_2);
    $('#opt_input_1_options').html('');
    $('#opt_input_2_options').html('');
    $('#opt_output_options').html('');
    //$('#opt_udp_rtp_1_src, #opt_shm_1_src, #opt_tcp_1_src').hide();
    //$('#opt_udp_rtp_2_src, #opt_shm_2_src, #opt_tcp_2_src').hide();

    $('#output_type').html('<option value="none_sink">None</option>');
    //$('#opt_file_sink, #opt_rtmp_sink, #opt_tcp_sink, #opt_udp_sink, #opt_shm_sink').hide();
}

MX.toggleInput = function(num) {
    setTimeout(function() { MX.toggleInputOptions(num); }, 200);
}

MX.toggleInputOptions = function(num) { // Zeus - Esta mal. Hay q contemplar los dos src
    //$('#opt_udp_rtp_' + num + '_src, #opt_shm_' + num + '_src, #opt_tcp_' + num + '_src').hide();
    $('#opt_output_options').html('');
    var in_val = $('#input_' + num + '_type').val();
    var id = '';
    var out_opt = '';
    var opt_input_options = '';
    var input_options = '';
    
    //output depends only on input_1
    if (num==1) {
        output_type = Object.keys(pipes_blueprint['pipeline_type'][$('#pipeline_type').val()]['input_'+num+'_type'][in_val]['output_type'])
    }
    input_options = pipes_blueprint['pipeline_type'][$('#pipeline_type').val()]['input_'+num+'_type'][in_val]['options']

    for (n in output_type)    {
        var opt_name = msg[lang][output_type[n]]
        var opt_name = typeof opt_name != "undefined" ? opt_name : output_type[n];
        out_opt += '<option value="'+output_type[n]+'">'+opt_name+'</option>';
    }
    for (m in input_options)    {
        var label = msg[lang][input_options[m]]
        var label = typeof label != "undefined" ? label : input_options[m];
        opt_input_options +=  '<div class="fieldrow"><label>'+label+'</label> <input id="'+input_options[m]+'" class="input_settings" name="'+input_options[m]+'" type="text"></input></div>';
    }

    $('#opt_input_'+num+'_options').html(opt_input_options);
    $('#output_type').html(out_opt);
    MX.fillWithSettings('opt_input_'+num+'_options');
}

MX.toggleOutput = function() {
    setTimeout(function() { MX.toggleOutputOptions(); }, 200);
}

MX.toggleOutputOptions = function() { // Zeus
   // $('#opt_file_sink, #opt_rtmp_sink, #opt_tcp_sink, #opt_udp_sink, #opt_shm_sink, #opt_overlay').hide();

    var in_val = $('#input_1_type').val();
    var out_val = $('#output_type').val();
    var id = '';
    var opt_output_options = '';

    output_options = pipes_blueprint['pipeline_type'][$('#pipeline_type').val()]['input_1_type'][in_val]['output_type'][out_val]['options']

    for (n in output_options)    {
        var label = msg[lang][output_options[n]]
        var label = typeof label != "undefined" ? label : output_options[n];
        opt_output_options += '<div class="fieldrow"><label>'+label+'</label> <input id="'+output_options[n]+'" class="input_settings" name="'+output_options[n]+'" type="text"></input> </div>';
        MX.setNewPipelineSettings(output_options[n]);
    }

/*
         // if (out_val == 'window') id = 'opt_window_sink';
         if (out_val == 'file_sink') id = 'opt_file_sink';
    else if (out_val == 'rtmp_sink') id = 'opt_rtmp_sink';
    else if (out_val == 'tcp_sink') id = 'opt_tcp_sink';
    else if (out_val == 'udp_sink') id = 'opt_udp_sink';
    else if (out_val == 'shm_sink') id = 'opt_shm_sink';
    else if (out_val == 'mpeg2_sink') id = 'opt_udp_sink';

    MX.setNewPipelineSettings(id);
    $('#' + id).show();
*/
    $('#opt_output_options').html(opt_output_options);
    $('#opt_overlay').show();
    MX.fillWithSettings('opt_output_options');

    //sebastian FIXME this is just temporary, should be another option or be available for all
    if (out_val == 'tcp_sink' || out_val == 'udp_sink' || out_val == 'shm_sink') {
        $('#opt_overlay').show();
    }
/*
    if (out_val == 'tcp_sink' || out_val == 'udp_sink' || out_val == 'shm_sink') {
        id = 'opt_overlay';
        MX.setNewPipelineSettings(id);
        $('#' + id).show();
    }

*/

}
//fill in the values with settings when creating new pipeline
MX.fillWithSettings = function(containerid) {
    $("#"+containerid).find('.input_settings').each(function() {
        var input_name = $(this).attr('name');
        var key = $(this).attr('id');
        $("#"+input_name).val(pipe_sett[key]);
    });
}
//FIXME this function was doing the same as one above?
MX.setNewPipelineSettings = function(id) {
    setTimeout(function() {
        $.each($('#' + id + ' .input_settings'), function() {
            var type = $(this).attr('type');
            // if (type == 'text') {
                var key = $(this).attr('id');
                $(this).val(pipe_sett[key]);
            // } else if (type == 'checkbox') {
            //     // var key = $(this).is(":checked");
            //     // console.log(key);
            //     // var key = $(this).attr('value');
            //     // if (key == 'on') $(this).attr('selected', true);
            //     var key = $(this).attr('value');
            //     console.log(key);
            //     $(this).val(pipe_sett[key]);
            // }
        });
    }, 200);
}

MX.addPipelineSwitch = function() {
    if ($("#addPipelineForm").hasClass('hidden')) {
        $("#addPipelineText, #pipeline_info_paste").addClass('hidden');
        $("#addPipelineForm").removeClass('hidden');
        $("#addPipelineSwitch").html(msg[lang]['pipeline']);
    } else {
        $("#addPipelineForm").addClass('hidden');
        $("#addPipelineText, #pipeline_info_paste").removeClass('hidden');
        $("#addPipelineSwitch").html(msg[lang]['form']);
    }
}

MX.showPipelineInfo = function(id) {
    MX.openModalWindow('html/infoPipeline.html');

    setTimeout(function() {
        $("#pipeline_graph, #pipeline_graph_full").attr('src', '../gst_png/' + pipe_data[id]['pipeline_id'] + '.png');
        $("#dot_download_link").attr('href', '../gst_png/' + pipe_data[id]['pipeline_id'] + '.dot');
        $("#pipeline_info_text").html(pipe_data[id]['pipeline_text']);
    }, 1000);
}

MX.imgFullscreen = function() {
    if ($('#fullscreen_container').hasClass('hidden')) {
        $('#fullscreen_container').removeClass('hidden');
    } else {
        $('#fullscreen_container').addClass('hidden');
    }
}

MX.reconnectPipeline = function(id) {
    $.post("/reconnect", ''+id+'');
}

//sebastian modified to adjust to pipes_blueprint values
MX.forwardPipeline = function(id) {
    MX.openModalWindow('html/addPipeline.html');

    var name = pipe_data[id]['pipeline_settings']['pipeline_name'];
    var type = pipe_data[id]['pipeline_settings']['pipeline_type'];
    var output = pipe_data[id]['pipeline_settings']['output_type'];
    console.log('output---------------> ', output);
    //fill pipeline type
    setTimeout( function() {
        console.log('---------------> ', pipe_data);
        $("#pipeline_name").val(name + '_copia');
        $("#pipeline_type").val(type);
       // $("#input_1_type").val(output.replace('sink', '1_src'));
        $("#pipeline_type, #input_1_type").attr('readonly', 'true');
        //MX.toggleInputOptions(1);
        MX.togglePipelineType();
    }, 500);
    //fill input 1 type
    setTimeout( function() {
        $("#input_1_type").val(output.replace('sink', '1_src'));
        $("#pipeline_type, #input_1_type").attr('readonly', 'true');
        MX.toggleInputOptions(1);
    }, 1000);
    //fill input 1 settings
    setTimeout( function() {
        //$("#input_1_type").children('.input_settings').each(function() {
        $("#opt_input_1_options").find('.input_settings').each(function() {
            // settings[$(this).attr("name")] = $(this).val();
            var input_name = $(this).attr('name');
            var sink_value = pipe_data[id]['pipeline_settings'][input_name.replace('1_src', 'sink')];
            $("#"+input_name).val(sink_value);
        });
        // $("#input_type_1").children('.input_settings');
    }, 2000);
}

MX.killPipeline = function(id) {
    $.post("/kill_pipeline", ''+id+'');
}

MX.addPipeline = function() {
    var content = '';

    if ($('#addPipelineForm').is(':visible')) {
        var settings = {};
        $(".input_settings").each(function() {
            if ($(this).is(':visible')) {
                console.log($(this).attr("name"), $(this).val());
                settings[$(this).attr("name")] = $(this).val();
            }
        });
        content = JSON.stringify(settings);
    } else {
        content = $('#pipeline_info_text').val();
    }

    $.post('/buildpipeline', content);

    MX.closeModalWindow();
}

MX.selectPipelineText = function() {
    $("#pipeline_info_text").select();
}

MX.copyText = function(id) {
	var text = $('#' + id).html();
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val(text).select();
    document.execCommand('copy');
    $temp.remove();

    alertify.notify('Texto copiado al portapapeles.', "success", 5);
}

MX.pasteText = function(id) {
    $('#' + id).focus();
    // $('#' + id).select();
    setTimeout( function() {
        document.execCommand("paste");
    }, 1000);

    console.log($('#' + id).textContent);

}

MX.openModalWindow = function(file) {
    // $('#layout_modal_container').showFlex();
    // $('#layout_modal_window').draggable({ containment: 'document' });

    // if(file) {
        // $('#layout_modal_window').html(OB.UI.getHTML(file));
        // OB.UI.widgetHTML( $('#layout_modal_window') );
        // OB.UI.translateHTML( $('#layout_modal_window') );
    // } else {
        // $('#layout_modal_window').html('');
    // }
    // window resize event resets position (browser glitchy?)
    // Zeus no se si es necesario $(window).resize();

    $('#layout_modal_window').draggable({ containment: 'document' });
    $.get(file, function(form) {
        $('#layout_modal_window').html(form);
        $('#layout_modal_container').css('display', 'flex');
    });
}

MX.closeModalWindow = function() {
    $('#layout_modal_container').hide();
    $('#layout_modal_window').html(''); // clear out html to avoid ID conflicts, etc.
}

// Logger
MX.getLog = function() {
    $.get('/log', function(datados) {
        $("#layout_logger_console_content").html('');
        var lines = datados.split("\n");
        for (nm in lines)	{
	        $("#layout_logger_console_content").append('<p>'+lines[nm]+'</p>');
        }
    });
}

MX.toggle_scrollLog = function() {
    if (log_autoscroll == false) {
        log_autoscroll = true;
        $('#toggle_scroll').removeClass('scroll_active').addClass('scroll_inactive');
        MX.scrollLog();
    } else {
        log_autoscroll = false;
        $('#toggle_scroll').removeClass('scroll_inactive').addClass('scroll_active');
    }
}

MX.scrollLog = function() {
    if (log_autoscroll == true && $('#layout_logger_console_content p').length > 0 ) {
        $('#layout_logger_console_content').animate({scrollTop: $('#layout_logger_console_content').prop("scrollHeight")}, 0);
    }
}

MX.flushLog = function() {
    $("#layout_logger_console_content > p").remove();
    $.get('/flush');
    MX.getLog();
}

// Footer
MX.serverClock = function() {
    $.get('/datetime', function(data) {
        var year = data.substr(0,4);
        var month = data.substr(4,2);
        var day = data.substr(6,2);
        var hh = data.substr(9,2);
        var mm = data.substr(12,2);
        var ss = data.substr(15,2);

        date = new Date(year, month-1, day, hh, mm, ss, 0);
    });
}

MX.updateClock = function() {
    setInterval(function() {
    	date.setSeconds(date.getSeconds() + 1);
    	var time = date.getTime() / 1000;
    	MX.clock(date);
        MX.currentDate(date);

        MX.animateFlow();
    }, 1000);
}

MX.currentDate = function(date) { // Zeus
    try {
        var day = date.getDate();
        var month = date.getMonth() + 1;
        var year = date.getFullYear();
        if (day < 10) day = '0' + day;
        if (month < 10) month = '0' + month;
        var current_date = day + '/' + month + '/' + year;
        if ($('#current_date p').text() != current_date) $('#current_date p').text(current_date);
    } catch(error) {
        console.log('ERROR: ', error);
    }
}

MX.clock = function(date) {
    if (date) {
        if ($('#time_clockHour').text() != date.getHours()) $('#time_clockHour').html((date.getHours() < 10?'0':'') + date.getHours());
        if ($('#time_clockMinute').text() != date.getMinutes()) $('#time_clockMinute').html((date.getMinutes() < 10?'0':'') + date.getMinutes());
        if ($('#time_clockSecond').text() != date.getSeconds()) $('#time_clockSecond').html((date.getSeconds() < 10?'0':'') + date.getSeconds());
    }
}

MX.currentVersion = function() {
	$.get('/VERSION', function(data) {
		$('#current_version').append('<p>ver. ' + data + '</p>');
	});
}
