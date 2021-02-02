function fetch_data_input() {
    return {
        'own_name': user,
        'uuid': uuid,
        'ex_id': $('#exchange').val(),
        'api_name': $('#api_name').val(),
        'pair': $('#pair').val(),
        'amount': $('#amount').val(),
        'stop_loss': $('#stop_loss').val(),
        'price': $('#price').val(),
        'profit': $('#profit').val(),
        'gap': $('#gap').val(),
        'follow_gap': $('#follow_gap').val(),
        'place_order_stop_loss': $('#cb_place_order_stop_loss').is(':checked'),
        'place_order_profit': $('#cb_place_order_profit').is(':checked'),
        'postOnly': $('#postOnly').is(':checked'),
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
        data['signal'] = 'buy_trigger';
        try {
            control_sk.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });
    $btn_sell.on('click', () => {
        let data = fetch_data_input();
        data['side'] = 'sell';
        data['signal'] = 'sell_trigger';
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