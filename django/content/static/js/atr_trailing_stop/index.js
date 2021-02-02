const MODE_SIMPLE = 'simple';
const MODE_DIVIDE_AND_CORQUE = 'divide_and_conrque';
const MODE_TRAILING_STOP = 'trailing_stop';

function fetch_data_input() {
    return {
        'own_name': user,
        'ex_id': $('#exchange').val(),
        'api_name': $('#api_name').val(),
        'amount': $('#amount').val(),
        'pair': $('#pair').val(),
        'fees': $('#fees').val(),
        'mode': $('#mode').val(),
        'loss_covering': $('#cb_loss_covering').is(':checked'),
        'step_amount': $('#step_amount').val(),
        'trailing_margin': $('#trailing_margin').val(),
        'min_profit': $('#min_profit').val(),
        'port': port
    };
}


$(document).ready(() => {
    $("#mode").on('change', (ev) => {
        change_ui_follow_dropdown();
    })
    change_ui_follow_dropdown();
})

function show_divide() {
    $("#step_amount_container").show();
}

function hide_divide() {
    $("#step_amount_container").hide();
}

function show_trailing() {
    $('#trailing_margin_container').show();
    $('#min_profit_container').show();
}

function hide_trailing() {
    $('#trailing_margin_container').hide();
    $('#min_profit_container').hide();
}

function change_ui_follow_dropdown() {
    let mode = $('#mode').val();
    if (MODE_SIMPLE == mode) {
        // hide divide
        hide_divide()
        // hide trailing
        hide_trailing()
    } else if (MODE_DIVIDE_AND_CORQUE == mode) {
        // hide trailing
        hide_trailing()
        // show divide
        show_divide()
    } else if (MODE_TRAILING_STOP == mode) {
        // hide divide
        hide_divide()
        // show trailing
        show_trailing()
    }
}