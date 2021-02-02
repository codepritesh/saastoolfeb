const signal_start = 'start';
const signal_stop = 'stop';

var uuid = uuidv1();
var bot_alias = bot_alias;
var own_name = own_name;
console.log(own_name)
try {
    if (null != uuid_web) {
        uuid = uuid_web;
    }
} catch (e) {
    console.error('error', e);
}

var control_sk = new WebSocket('ws://' + window.location.host + '/ws/ma/' + uuid + '/control');
var log_sk = new WebSocket('ws://' + window.location.host + '/ws/ma/' + uuid + '/log');
var price_sk = new WebSocket('ws://' + window.location.host + '/ws/ma/' + uuid + '/price');

$(document).ready(() => {

   log_sk.onmessage = function(e) {
	   render_log(e);
   };
   price_sk.onmessage = function(e) {
	   render_price_trade(e);
   };

   $('#btn-start-bot').on('click', () => {
	let data = fetch_data_input();
	data['signal'] = signal_start;
	data['uuid'] = uuid;
	console.log(data)
	try {
	     control_sk.send(JSON.stringify(data));
	} catch (e) {
		alert(e.message);
	}
   });

   $('#btn-stop-bot').on('click', () => {
	let data = fetch_data_input();
	data['signal'] = signal_stop;
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
   // download report
    $('#btn-download-report').on('click', () => {
        download_report(bot_alias)
    });
});

function fetch_data_input() {
    return  {
	'own_name': own_name,
	'socket': 1232,
        'ex_id': $('#exchange').val(),
        'api_name': $('#api_name').val(),
        'bot_type': $('#bot_type').val(),
        'pair': $('#pair').val(),
        'amount': $('#amount').val(),
        'limit_order': $('#limit_order').val(),
        'profit': $('#profit').val(),
        'loss_price': $('#loss_price').val(),
        'ohlc_interval': $('#ohlc_interval').val(),
        'ma_first': $('#ma_first').val(),
        'ma_second': $('#ma_second').val(),
        'ma_source': $('#ma_source').val(),
        'base_closed_volume': $('#base_closed_volume').val(),
        'subsequent_level_volume': $('#subsequent_level_volume').val(),
        'subsequent_level_spread': $('#subsequent_level_spread').val(),
    };
}

/**
 * Download log
 */
function download_log(file) {
    window.location.href = `/ma-bot/logs/${file}_${uuid}.log`;
}

/**
 * Download report
 */
function download_report(file) {
    window.location.href = `/ma-bot/reports/${file}_${uuid}.csv`;
}
