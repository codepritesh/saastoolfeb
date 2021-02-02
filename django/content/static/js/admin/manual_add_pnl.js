const csrftoken = Cookies.get('csrftoken');
var api_manual = {}

function fetch_data() {
    let data = {
        ex_id: $('#exchange').val(),
        api_name: $('#account').val(),
        coins: {}
        // date: $('#date').val(),
    }
    // for (const ele in $('#coins').find('.form-group')) {
    let coin_input = $('#coins').find('.form-group')
    if (coin_input.length) {
        for (let i = 0; i < coin_input.length; i++) {
            const coin_ele_input = $(coin_input[i]).find('input').first()
            data.coins[$(coin_ele_input).attr('id')] = coin_ele_input.val()
        }
    }
    return data
}

get_all_coins()
get_list_api()

$(document).ready(() => {
    $('#btn-add').on('click', (e) => {
        let data = fetch_data()
        data.action = 'update'
        invoke_api_update_pnl(data)
    })
    $('#btn-delete').on('click', (e) => {
        let data = fetch_data()
        data.action = 'delete'
        invoke_api_update_pnl(data)
    })
    $(document).on('click', '#api-list > li', (event) => {
        const ele = $(event.target)
        // fill data
        $('#account').val($(ele).text())
        $('#exchange').val($(ele).attr('exchange'))
        // coin

        const api_name = $(ele).text()
        change_follow_action_add_or_update(api_name)
        change_coin_balance(api_name)
        // let coin_input = $('#coins').find('.form-group')
        // if (coin_input.length) {
        //     for (let i = 0; i < coin_input.length; i++) {
        //         const coin_ele_input = $(coin_input[i]).find('input').first()
        //         if (coin_ele_input.length) {
        //             let coin = $(coin_ele_input[0]).attr('id')
        //             if (api_manual[api_name]) {
        //                 coin_ele_input.val(api_manual[api_name]['balance'][coin])
        //             }
        //         }
        //     }
        // }
    })
    $('#account').on('input', function (e) {
        let api = $(e.target).val()
        change_follow_action_add_or_update(api)
    });
})

function change_coin_balance(api_name) {
    let coin_input = $('#coins').find('.form-group')
    if (coin_input.length) {
        for (let i = 0; i < coin_input.length; i++) {
            const coin_ele_input = $(coin_input[i]).find('input').first()
            if (coin_ele_input.length) {
                let coin = $(coin_ele_input[0]).attr('id')
                if (api_manual[api_name]) {
                    coin_ele_input.val(api_manual[api_name]['balance'][coin])
                }
            }
        }
    }
}

function change_follow_action_add_or_update(api) {
    let api_ele = $('#api-list').find(`.${api}`)
    if (api_ele.length) {
        // show delete
        $('#btn-delete').show()
        // change text cho update
        $('#btn-add').text('Update')
        // change_coin_balance(api)
    } else {
        $('#btn-delete').hide()
        $('#btn-add').text('Add')
    }
}

function invoke_api_update_pnl(data) {
    $.ajax({
        header: {
            'X-CSRFToken': csrftoken
        },
        url: `/pnl-manual`,
        type: 'POST',
        data: JSON.stringify(data),
        success: (json_data) => {
            console.log(json_data)
            alert('Save PNL Manual Success')
            $('#api-list').empty()
            get_list_api()
        },
        onerror: (e) => {
            console.log('Error ', e);
            alert('Save PNL Manual Error')
        }
    })
}

function get_list_api() {
    $.ajax({
        url: `/list-manual-api`,
        success: (data) => {
            api_manual = data;
            console.log('data get coin list ', data)
            //    update html
            for (const [key, value] of Object.entries(data)) {
                let html = `<li class="api ${key}" exchange="${value.ex}">${key}</li>`
                $('#api-list').append(html)
            }
        },
        onerror: (e) => {
            console.log('Error ', e);
        }
    })
}


/**
 *
 */
function get_all_coins() {
    $.ajax({
        url: `/coins`,
        success: (data) => {
            console.log(data.coins)
            for (const coin of data.coins) {
                let html = `<div class="form-group col-md-2">
                    <label for="${coin}" class="text-bold">${coin}</label>
                    <input type="number" class="form-control" id="${coin}" value="">
                </div>`
                $('#coins').append(html)
            }
        },
        onerror: (e) => {
            console.log('Error ', e);
        }
    })
}