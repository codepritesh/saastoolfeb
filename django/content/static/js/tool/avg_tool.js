const signal_clear = 'clear';
const signal_cancel = 'cancel';
const signal_average = 'average';

var uuid = uuidv1();
var bot_alias = bot_alias;
try {
    if (null != uuid_web) {
        uuid = uuid_web;
    }
} catch (e) {
    console.error('error', e);
}

var control_sk = new WebSocket('ws://' + window.location.host + '/ws/avg_tool/' + uuid + '/control');
var log_sk = new WebSocket('ws://' + window.location.host + '/ws/avg_tool/' + uuid + '/log');
var price_sk = new WebSocket('ws://' + window.location.host + '/ws/avg_tool/' + uuid + '/price');


$(document).ready(() => {

   log_sk.onmessage = function(e) {
	   render_log(e);
   };
   price_sk.onmessage = function(e) {
	   render_price_trade(e);
   };

   // clear
    $('#btn_clear_order').on('click', () => {
        let data = fetch_data_input();
        data['signal'] = signal_clear;
        data['uuid'] = uuid;
        try {
             control_sk.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });
    // cancel
    $('#btn_cancel_order').on('click', () => {
        let data = fetch_data_input();
        data['signal'] = signal_cancel;
        data['uuid'] = uuid;
        try {
             control_sk.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });
    // average
    $('#btn_avg_order').on('click', () => {
        let data = fetch_data_input();
        data['signal'] = signal_average;
        data['uuid'] = uuid;
        try {
             control_sk.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });

   // download log
    $('#btn-download-log').on('click', () => {
        download_log(bot_alias)
    });
});

function fetch_data_input() {
    return  {
        'own_name': user,
        'ex_id': $('#exchange').val(),
        'api_name': $('#api_name').val(),
        'pair': $('#pair').val(),
        'side': $('#side').val(),
        'price_type': $('#price_type').val(),
    };
}

/**
 * Download log
 */
function download_log(file) {
    window.location.href = `/avg-tool/logs/${file}_${uuid}.log`;
}
