function fetch_data_input() {
    return {
        'own_name': user,
        'uuid': uuid,
        'ex_id': $('#exchange').val(),
        'api_name': $('#api_name').val(),
        'amount': $('#amount').val(),
        'pair': $('#pair').val(),
        'entry_price': $('#entry_price').val(),
        'trailing_margin': $('#trailing_margin').val(),
        'cancel_threshold': $('#cancel_threshold').val(),
        'postOnly': $('#postOnly').is(':checked'),
        'gap': $('#gap').val(),
        'follow_gap': $('#follow_gap').val(),
        'min_profit': $('#min_profit').val(),
        'port': port
    };
}

/**
 * connect websocket
 */
function connect_control_ws() {
    let control_sk = new WebSocket(`ws://${window.location.host}/ws/${ws_define}/${uuid}/control`);

    control_sk.onclose = function (e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function () {
            connect_control_ws();
        }, 1000);
    };

    control_sk.onerror = function (err) {
        console.error('Socket encountered error: ', err.message, 'Closing socket');
        control_sk.close();
    };

    let $btn_sell = $('#btn-place-sell');
    let $btn_buy = $('#btn-place-buy');

    $btn_buy.unbind();
    $btn_sell.unbind();

    $btn_buy.on('click', () => {
        let data = fetch_data_input();
        data['side'] = 'buy';
        data['signal'] = 'begin_trading';
        try {
            control_sk.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });
    $btn_sell.on('click', () => {
        let data = fetch_data_input();
        data['side'] = 'sell';
        data['signal'] = 'begin_trading';
        try {
            control_sk.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });
}

$(document).ready(() => {
    connect_control_ws();
})