/**
 * constant
 */
const signal = 'signal';
const init_box_signal = 'init_box_signal';
const follow_box_signal = 'follow_box_signal';
const balancing_box_signal = 'balancing_box_signal';
const follow_balancing_signal = 'follow_balancing_box_signal'

/**
 *
 * @returns {{ex_id: (jQuery|string|undefined), amount: (jQuery|string|undefined), follow_track_box_gap: (jQuery|string|undefined), follow_track_box_amount: (jQuery|string|undefined), inti_box_sell_price: (jQuery|string|undefined), uuid: *, pair: (jQuery|string|undefined), own_name: (string), inti_box_buy_price: (jQuery|string|undefined), port: string, api_name: (jQuery|string|undefined), inti_box_amount: (jQuery|string|undefined), balance_box_count: (jQuery|string|undefined), balance_box_amount: (jQuery|string|undefined)}}
 */
function fetch_data_input() {
    return {
        'own_name': user,
        'uuid': uuid,
        'ex_id': $('#exchange').val(),
        'api_name': $('#api_name').val(),
        'amount': $('#amount').val(),
        'pair': $('#pair').val(),
        // bot initialization
        'inti_box_buy_price': $('#inti_box_buy_price').val(),
        'inti_box_sell_price': $('#inti_box_sell_price').val(),
        'inti_box_amount': $('#inti_box_amount').val(),
        // bot follow track
        'follow_track_box_postOnly': $('#follow_track_box_postOnly').is(':checked'),
        'follow_track_box_gap': $('#follow_track_box_gap').val(),
        'follow_track_box_follow_gap': $('#follow_track_box_follow_gap').val(),
        'follow_track_box_amount': $('#follow_track_box_amount').val(),
        // balancing box
        'balance_box_amount': $('#balance_box_amount').val(),
        'balance_box_count': $('#balance_box_count').val(),
        // follow balancing box
        'follow_balance_box_postOnly': $('#follow_balance_box_postOnly').is(':checked'),
        'follow_balance_box_gap': $('#follow_balance_box_gap').val(),
        'follow_balance_box_follow_gap': $('#follow_balance_box_follow_gap').val(),
        'follow_balance_box_time': $('#follow_balance_box_time').val(),
        'follow_balance_box_amount': $('#follow_balance_box_amount').val(),
        'follow_balance_box_count': $('#follow_balance_box_count').val(),
        'follow_balance_box_profit': $('#follow_balance_box_profit').val(),
        'follow_balance_box_step': $('#follow_balance_box_step').val(),
        'port': port
    };
}

function connect_action_ws() {
    let action_ws = new WebSocket(`ws://${window.location.host}/ws/${ws_define}/${uuid}/action`);

    action_ws.onclose = function (e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function () {
            connect_action_ws();
        }, 1000);
    };

    action_ws.onerror = function (err) {
        console.error('Socket encountered error: ', err.message, 'Closing socket');
        action_ws.close();
    };

    let $init_box_submit = $('#inti_box_submit');
    let $btn_follow_box_sell = $('#follow_track_box_sell');
    let $btn_follow_box_buy = $('#follow_track_box_buy');

    let $btn_balance_box_box_buy = $('#balance_box_box_buy');
    let $btn_balance_box_box_sell = $('#balance_box_box_sell');

    let $btn_follow_balance_box_buy = $('#follow_balance_box_buy');
    let $btn_follow_balance_box_sell = $('#follow_balance_box_sell'); 

    $init_box_submit.unbind()

    $btn_follow_box_buy.unbind();
    $btn_follow_box_sell.unbind();
    $btn_balance_box_box_buy.unbind();
    $btn_balance_box_box_sell.unbind();
    $btn_follow_balance_box_buy.unbind();
    $btn_follow_balance_box_sell.unbind();   

    /**
     * action box follow track
     */
    $btn_follow_box_buy.on('click', () => {
        let data = fetch_data_input();
        data['side'] = 'buy';
        data[signal] = follow_box_signal;
        try {
            action_ws.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });
    $btn_follow_box_sell.on('click', () => {
        let data = fetch_data_input();
        data['side'] = 'sell';
        data[signal] = follow_box_signal;
        try {
            action_ws.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });

    /**
     * action box balancing
     *
     *
     */
    $btn_balance_box_box_buy.on('click', () => {
        let data = fetch_data_input();
        data['side'] = 'buy';
        data[signal] = balancing_box_signal;
        try {
            action_ws.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });
    $btn_balance_box_box_sell.on('click', () => {
        let data = fetch_data_input();
        data['side'] = 'sell';
        data[signal] = balancing_box_signal;
        try {
            action_ws.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });
        /**
     * action box follow balancing
     *
     *
     */
    $btn_follow_balance_box_buy.on('click', () => {
        let data = fetch_data_input();
        data['side'] = 'buy';
        data[signal] = follow_balancing_signal;
        try {
            action_ws.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });
    $btn_follow_balance_box_sell.on('click', () => {
        let data = fetch_data_input();
        data['side'] = 'sell';
        data[signal] = follow_balancing_signal;
        try {
            action_ws.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });
    /**
     *
     */
    $init_box_submit.on('click', () => {
        let data = fetch_data_input();
        data[signal] = init_box_signal;
        try {
            action_ws.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    })

}

function connect_update_data_box() {
    let data_ws = new WebSocket(`ws://${window.location.host}/ws/${ws_define}/${uuid}/update`);

    data_ws.onclose = function (e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function () {
            connect_update_data_box();
        }, 1000);
    };

    data_ws.onerror = function (err) {
        console.error('Socket encountered error: ', err.message, 'Closing socket');
        data_ws.close();
    };
      data_ws.onmessage = function (msg) {
        let ws_data = msg.data;
        let data = JSON.parse(ws_data);
        console.log('data ', data)
        update_farthest_price(data);
    }

}

function update_farthest_price(data) {
    $('#farthest_buy').val(data.message.farthest_buy);
    $('#farthest_sell').val(data.message.farthest_sell);
    $('#mid').val(data.message.mid);
}

$(document).ready(() => {
    connect_action_ws();
    connect_update_data_box();

        // common action
    $('#follow_track_box_postOnly').on('change', () => {
        change_ui_follow_track_box_postOnly()
    })
    change_ui_follow_track_box_postOnly()

    $('#follow_balance_box_postOnly').on('change', () => {
        change_ui_follow_balance_box_postOnly()
    })
    change_ui_follow_balance_box_postOnly()

})




function change_ui_follow_track_box_postOnly() {
    let post_only = $('#follow_track_box_postOnly');
    if (post_only.length) {
        let post_only = $('#follow_track_box_postOnly').is(':checked');
        if (post_only) {
            $('#follow_track_box_gap_container').hide()
            $('#follow_track_box_follow_gap_container').hide()
        } else {
            $('#follow_track_box_gap_container').show()
            $('#follow_track_box_follow_gap_container').show()
        }
    }

}


function change_ui_follow_balance_box_postOnly() {
    let post_only = $('#follow_balance_box_postOnly');
    if (post_only.length) {
        let post_only = $('#follow_balance_box_postOnly').is(':checked');
        if (post_only) {
            $('#follow_balance_box_gap_container').hide()
            $('#follow_balance_box_follow_gap_container').hide()
        } else {
            $('#follow_balance_box_gap_container').show()
            $('#follow_balance_box_follow_gap_container').show()
        }
    }

}
