function fetch_data_input() {
    return {
        'own_name': user,
        'uuid': uuid,
        'ex_id1': $('#ex_id1').val(),
        'api_name1': $('#api_name1').val(),
        'ex_id2': $('#ex_id2').val(),
        'api_name2': $('#api_name2').val(),
        'exchange_profit': $('#exchange_profit').val(),
        'amount': $('#amount').val(),
        'pair': $('#pair').val(),
        'profit': $('#profit').val(),
        'min_profit': $('#min_profit').val(),
        'price': $('#price').val(),
        'follow_market': $('#follow_market').is(':checked'),
        'is_parallel': $('#is_parallel').is(':checked'),
        'postOnly': $('#postOnly').is(':checked'),
        'gap': $('#gap').val(),
        'follow_gap': $('#follow_gap').val(),
        // 'fees': $('#fees').val(),
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

    let $btn_sell = $('#btn-place-sell');
    let $btn_buy = $('#btn-place-buy');

    $btn_buy.unbind();
    $btn_sell.unbind();

    $btn_buy.on('click', () => {
        let data = fetch_data_input();
        data['side'] = 'buy';
        try {
            action_ws.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });
    $btn_sell.on('click', () => {
        let data = fetch_data_input();
        data['side'] = 'sell';
        try {
            action_ws.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });
}

$(document).ready(() => {
    connect_action_ws();
})