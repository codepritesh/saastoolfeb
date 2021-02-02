var alias = bot_alias;

var trackingSocket = new WebSocket('ws://' + window.location.host +'/ws/' + suff_ws + '/' + alias + srv_id + '/tracking');

$(document).ready(() => {
	trackingSocket.onmessage = function(e) {
	var datas = JSON.parse(e.data);
	var data = datas['message'];
        let ele_parent = $('#table-instance-running');
        $(ele_parent).empty();
        for (item in data) {
            var abot = data[item];
            let append_html = `<tr id=${abot.uuid}>\
                                 <td><a href="/${bot_url}/${abot.uuid}" target="_blank">${abot.uuid}</a></td>\
                                 <td>${abot.time}</td>\
                                 <td>${abot.own_name}</td>\
                                 <td>${abot.ex_id}</td>\
                                 <td>${abot.api_name}</td>\
                                 <td>${abot.pair}</td>\
                                 <td><a href="${abot.link_grafana}" target="_blank">${abot.link_grafana}</a></td>\
                               </tr>`;
            if (ele_parent.length) {
                let ele = $('#' + abot.uuid);
                if (!ele.length) { // not exits
                    if (append_html) {
                        ele_parent.append(append_html);
                    }
                } // end if
            }
          }
        };
        trackingSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
	};
});
