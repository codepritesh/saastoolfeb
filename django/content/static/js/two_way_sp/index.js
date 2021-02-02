function fetch_data_input() {
    return {
        'own_name': user,
        'uuid': uuid,
        'ex_id': $('#exchange').val(),
        'api_name': $('#api_name').val(),
        'amount': $('#amount').val(),
        'pair': [$('#pair1').val(), $('#pair2').val()],
        'follow_market': $('#follow_market').is(':checked'),
        'pair_first': $('#pair_first').val(),
        'min_profit': $('#min_profit').val(),
        'postOnly': $('#postOnly').is(':checked'),
        'gap': $('#gap').val(),
        'follow_gap': $('#follow_gap').val(),
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
    change_ui_follow_place_order_cb()
    $('#place_order_parallel').on('change', () => {
        change_ui_follow_place_order_cb();
    })
})

function change_ui_follow_place_order_cb() {
    if ($('#place_order_parallel').is(':checked')) {
        $('#choose_pair_first').hide();
    } else {
        $('#choose_pair_first').show();
    }
}