function fetch_data_input() {
    return {
        'own_name': user,
        'uuid': uuid,
        'ex_id': $('#exchange').val(),
        'api_name': $('#api_name').val(),
        'amount': $('#amount').val(),
        'pair': $('#pair').val(),
        'profit': $('#profit').val(),
        'timer': $('#timer').val(),
        'postOnly': $('#postOnly').is(':checked'),
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

    let $btn_buy_sell = $('#btn-buy-sell');
    let $btn_sell_buy = $('#btn-sell-buy');
    let $btn_stop = $('#btn-stop');

    $btn_buy_sell.unbind();
    $btn_sell_buy.unbind();
    $btn_stop.unbind();

    $btn_buy_sell.on('click', () => {
        let data = fetch_data_input();
        data['action'] = 'buy/sell';
        try {
            action_ws.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });
    $btn_sell_buy.on('click', () => {
        let data = fetch_data_input();
        data['action'] = 'sell/buy';
        try {
            action_ws.send(JSON.stringify(data));
        } catch (e) {
            alert(e.message);
        }
    });

    $btn_stop.on('click', () => {
        let data = fetch_data_input();
        data['action'] = 'stop';
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