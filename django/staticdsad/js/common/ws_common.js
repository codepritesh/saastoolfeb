const signal_start = 'start';
const signal_stop = 'stop';

var uuid = uuidv1();
var bot_alias = bot_alias;
try {
    if (null != uuid_web) {
        uuid = uuid_web;
    }
} catch (e) {
    console.error('error', e);
}

function connect() {
    console.log('ws define ', ws_define);
    if (!ws_define) {
        // alert('Error when trying to get ws url, please refresh your browser');
        return;
    }
    var control_sk = new WebSocket(`ws://${window.location.host}/ws/${ws_define}/${uuid}/control`);
    var log_sk = new WebSocket(`ws://${window.location.host}/ws/${ws_define}/${uuid}/log`);
    var price_sk = new WebSocket(`ws://${window.location.host}/ws/${ws_define}/${uuid}/price`);
    var pnl_sk = new WebSocket(`ws://${window.location.host}/ws/${ws_define}/${uuid}/pnl`);
    // var table_pnl_msg = new WebSocket(`ws://${window.location.host}/ws/${ws_define}/${uuid}/table_pnl_msg`);
    var table_profit_price_msg = new WebSocket(`ws://${window.location.host}/ws/${ws_define}/${uuid}/profit_price`);

    control_sk.onclose = function (e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function () {
            connect();
        }, 1000);
    };

    control_sk.onerror = function (err) {
        console.error('Socket encountered error: ', err.message, 'Closing socket');
        control_sk.close();
    };

    // log
    log_sk.onclose = () => {
        console.log('Socket log is closed. Reconnect will be attempted in 1 second.');
    }

    log_sk.onerror = function (err) {
        console.error('Socket log encountered error: ', err.message, 'Closing socket');
        log_sk.close();
    };
    // price_sk
    price_sk.onclose = () => {
        console.log('Socket price_sk is closed. Reconnect will be attempted in 1 second.');
    }

    price_sk.onerror = function (err) {
        console.error('Socket price_sk encountered error: ', err.message, 'Closing socket');
        price_sk.close();
    };
    // pnl_sk
    pnl_sk.onclose = () => {
        console.log('Socket pnl_sk is closed. Reconnect will be attempted in 1 second.');
    }

    pnl_sk.onerror = function (err) {
        console.error('Socket pnl_sk encountered error: ', err.message, 'Closing socket');
        pnl_sk.close();
    };
    // table_pnl_msg
    // table_pnl_msg.onclose = () => {
    //     console.log('Socket price_sk is closed. Reconnect will be attempted in 1 second.');
    // }

    // table_pnl_msg.onerror = function (err) {
    //     console.error('Socket price_sk encountered error: ', err.message, 'Closing socket');
    //     table_pnl_msg.close();
    // };
    // table_profit_price_msg
    table_profit_price_msg.onclose = () => {
        console.log('Socket price_sk is closed. Reconnect will be attempted in 1 second.');
    }

    table_profit_price_msg.onerror = function (err) {
        console.error('Socket price_sk encountered error: ', err.message, 'Closing socket');
        table_profit_price_msg.close();
    };
    table_profit_price_msg.onmessage = function (msg) {
        let profit_data = msg.data;
        profit_data = JSON.parse(profit_data);
        let data = profit_data.message;
        for (var i = 0; i < profit_data.message.length; i++) {
            let ele = $($($("#body-profit-table").find('tr')[i]).find('td')[1]);
            ele.text(numberWithCommas(data[i]))
            define_color_background(ele, parseFloat($("#threshold_profit").val()), parseFloat(data[i]))
        }
    }
    log_sk.onmessage = function (e) {
        render_log(e);
    };
    price_sk.onmessage = function (e) {
        render_price_trade(e);
    };
    pnl_sk.onmessage = function (e) {
        render_pnl_trade(e);
    };
    $('#btn-resume-bot').unbind();
    $('#btn-start-bot').unbind();
    $('#btn-stop-bot').unbind();

    $('#btn-start-bot').on('click', () => {
        let data = fetch_data_input();
        data['signal'] = signal_start;
        data['uuid'] = uuid;
        data['is_production'] = $('#is_production').is(':checked');
        try {
            control_sk.send(JSON.stringify(data));
            $('#btn-start-bot').prop('disabled', true);
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
            // show btn download report
            $('#btn-download-report').show();
        } catch (e) {
            alert(e.message);
        }
    });

    $('#btn-resume-bot').on('click', () => {
        let data = fetch_data_input();
        data['signal'] = signal_start;
        data['uuid'] = uuid;
        data['resume'] = true;
        data['is_production'] = $('#is_production').is(':checked');
        console.log('uuid ', uuid, data)
        try {
            control_sk.send(JSON.stringify(data));
             $('#btn-resume-bot').prop('disabled', true);
        } catch (e) {
            alert(e.message);
        }
    });

    // table_pnl_msg.onmessage = function (msg) {
    //     let msg_data = msg.data;
    //     msg_data = JSON.parse(msg_data);
    //     let data = msg_data.message;
    //     console.log('dpnl data ', msg_data);
    //     render_table_pnl('#base-currency', data['base-currency']);
    //     render_table_pnl('#quote-currency', data['quote-currency']);
    //     render_table_pnl('#coin-fee', data['coin-fee']);
    // };

    $('#trigger_buy').on('change', (ev) => {
        let data = fetch_data_input();
        data['signal'] = signal_manual;
        data['trigger_side'] = 'buysell';
        data['uuid'] = uuid;
        console.log('data ', data)
        try {
            control_sk.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    })
    $('#trigger_sell').on('change', (ev) => {
        let data = fetch_data_input();
        data['signal'] = signal_manual;
        data['trigger_side'] = 'sellbuy';
        data['uuid'] = uuid;
        console.log('data ', data)
        try {
            control_sk.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    })

}


$(document).ready(() => {
    connect();

    // download log
    $('#btn-download-log').on('click', () => {
        download_log(bot_alias)
    });

    $('#btn-download-report').on('click', () => {
        download_report(bot_alias)
    });

    // common action
    $('#postOnly').on('change', () => {
        change_ui_follow_post_only()
    })
    change_ui_follow_post_only()

//    timer_load()
});

function timer_load() {
    if (!data_url) {
        data_url = `/data/pnl_${uuid}.csv`
        console.log('Change data url ', data_url)
        timer_load()
    } else {
        render_monitor_link(data_url)
        setInterval(() => {
            console.log('Reset pnl table')
            render_monitor_link(data_url)
        }, 5*1000)
    }
}
function clear_space() {
    $('#table-monitor-link').empty()
}

function render_monitor_link(data) {
    CsvToHtmlTable.init({
        csv_path: `${data}`,
        element: 'table-monitor-link',
        allow_download: true,
        csv_options: {separator: ',', delimiter: '"'},
        datatables_options: {"paging": false, "pageLength": 12, 'searching': false, 'ordering':  false, 'fixedColumns': true},
    });
    $("#table-monitor-link-table_info").hide();
}

function change_ui_follow_post_only() {
    let post_only = $('#postOnly');
    if (post_only.length) {
        let post_only = $('#postOnly').is(':checked');
        if (post_only) {
            $('#gap_container').hide()
            $('#follow_gap_container').hide()
        } else {
            $('#gap_container').show()
            $('#follow_gap_container').show()
        }
    }

}

/**
 * Download log
 */
function download_log(file) {
    window.location.href = `/logs/${file}_${uuid}.log`;
}

function download_report(file) {
    window.location.href = `/reports/${file}_${uuid}.csv`;
}
