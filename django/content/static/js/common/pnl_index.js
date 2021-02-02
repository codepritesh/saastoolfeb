var api_json;

var extra_info = {}

// call api json
invoke_get_apis()


function fetch_data() {
    return {
        ex_id: $('#exchange').val(),
        account: $('#api_name').val(),
        comment: $('#comment').val()
    }
}

function get_pnl() {
    $('#area_loading').show();
    invoke_api_PNL()
}

$(document).ready(() => {
    $('#exchange').append(`<option value="ALL_EX">All Exchange</option>`)
    $('#btn-get-pnl').on('click', () => {
        get_pnl()
    })

    $('#btn-update').on('click', () => {
        invoke_api_update_comment()
    })
    $('#exchange').on('change', (event) => {
        change_option_account()
    })
    $('#api_name').on('change', (event) => {
        get_extension_info_pnl()
    })
    $('#btn-get-history').on('click', (event) => {
        $('#area_loading').show();
        get_history()
    })

    $('#btn-get-balance').on('click', (event) => {
        $('#area_loading').show();
        get_balance()
    })
    $('#area_loading').hide();

    // get today and yesterday
    let toDay = moment().format('YYYY-MM-DD')
    let yesterday = moment().add(-1, 'd').format('YYYY-MM-DD')
    $('#from_date').val(yesterday)
    $('#to_date').val(toDay)
})

$(document).scroll((ev) => {
    let table_balance = $('#theadBalance')
    if (table_balance.length) {
        let headerTable = $(table_balance[0])
        let top_table = $('#table-container').offset().top
        //    cal top
        if (parseInt($(document).scrollTop()) - parseInt(top_table) > 0) {
            let newTopCss = `${parseInt($(document).scrollTop()) - parseInt(top_table) - 12}px`
            headerTable.css('position', 'absolute')
            headerTable.css('top', newTopCss)
        } else {
            headerTable.css('position', 'static')
            headerTable.css('top', '0px')
        }
    }
})

function add_all_account() {
    $('#api_name').append(`<option value="ALL_ACCOUNT">All Account</option>`)
}

function get_balance() {
    $.ajax({
        url: `/balance?ex_id=${$('#exchange').val()}&account=${$('#api_name').val()}`,
        type: 'GET',
        success: (data) => {
            render_balance(data)
        },
        onerror: (e) => {
            console.log('Error ', e);
        }
    })
}

function clear_space() {
    $('#pnl-area').empty()
    $('#table-container').empty()
}

function render_balance(data) {
    clear_space()
    CsvToHtmlTable.init({
        csv_path: `${data.url}`,
        element: 'table-container',
        allow_download: true,
        csv_options: {separator: ',', delimiter: '"'},
        datatables_options: {"paging": false}
    });
    $('#area_loading').hide();

}

function render_balance_bk(data) {
    // clear pnl
    clear_space()
    if (Object.keys(data).includes('TOTAL')) {
        render_balance_ele('TOTAL', data['TOTAL'])
    }
    for (let [key, item] of Object.entries(data)) {
        if (key == 'TOTAL') {
            continue
        }
        render_balance_ele(key, item)
    }
    $('#area_loading').hide();
}

function render_balance_ele(key, all_ele) {
    let html = `<div class="card">
                <div class="card-header bg-warning">
                    <span>
                        ${key}
                    </span>
                </div>
                <div class="card-body">
                    <table class="table table-bordered">
                        <thead>
                        <tr>
                            <th scope="col">#</th>
                            <th scope="col" colspan="2">${all_ele.t}</th>
                            <th scope="col" colspan="2">Price Target</th>
                        </tr>
                        </thead>
                        <tbody>`
    for (const [key, item] of Object.entries(all_ele)) {
        if ('t' == key || 'total' == key) {
            continue
        }
        let coins = `<tr class="${fetch_class_balance_tr(item)}">
                        <th scope="row">${key}</th>
                        <td colspan="2">${numberWithCommas(item['balance'])}</td>
                        <td colspan="2">${item['PriceInTarget']}</td>
                    </tr>`
        html += coins
    }
    // total
    let total_html = `<tr>
                        <th scope="row">TOTAL</th>
                        <td colspan="4" class="text-center bg-light text-primary">${numberWithCommas(all_ele['total'])}</td>
                    </tr>`
    html += total_html
    let footer = `</tbody>
                    </table>
                </div>
            </div>`

    html += footer
    $('#pnl-area').append(html)
}


function get_history() {
    $.ajax({
        url: `/history?ex_id=${$('#exchange').val()}&account=${$('#api_name').val()}&fromDate=${$('#from_date').val()}&toDate=${$('#to_date').val()}`,
        type: 'GET',
        success: (data) => {
            console.log(data)
            render_history(data)
        },
        onerror: (e) => {
            console.log('Error ', e);
        }
    })
}

function render_history(data) {
    // clear pnl
    clear_space()
    if (data && Object.keys(data).length > 1) {
        // if (data) {
        // add total table
        let ele = Object.values(data)[0]
        let keys = Object.keys(ele[0])
        add_total_history_table(keys, data)
    }
    for (let [key, item] of Object.entries(data)) {
        render_history_ele(key, item)
    }
    $('#area_loading').hide();
}

function add_total_history_table(keys, all_ele) {
    let list_total = []
    let html = `<div class="card">
                <div class="card-header bg-warning">
                    <span>
                        TOTAL
                    </span>
                </div>
                <div class="card-body">
                    <table class="table table-bordered">
                        <thead>
                        <tr>
                            <th scope="col">#</th>
                            <th scope="col">${$('#from_date').val()}</th>
                            <th scope="col">${$('#to_date').val()}</th>
                            <th scope="col">PNL</th>
                            <th scope="col">Price Target</th>
                        </tr>
                        </thead>
                        <tbody>`
    for (const key of keys) {
        if ('t' == key || 'total' == key) {
            continue
        }
        let data = sum_coin_pnl(key, all_ele)
        list_total.push(data)
        let coins = `<tr class="${fetch_class_of_total_table(data)}">
                        <th scope="row">${key}</th>
                        <td>${numberWithCommas(data['start'])}</td>
                        <td>${numberWithCommas(data['current'])}</td>
                        <td class="${define_color_text(numberWithCommas(data['PnL']))}">${numberWithCommas(data['PnL'])}</td>
                        <td>${data['PriceInTarget']}</td>
                    </tr>`
        html += coins
    }
    // total
    let total_html = `<tr>
                        <th scope="row">TOTAL</th>
                        <td colspan="4" class="text-center bg-light ${define_color_text(numberWithCommas(get_total_pnl(list_total)))}">${numberWithCommas(get_total_pnl(list_total))}</td>
                    </tr>`
    html += total_html
    let footer = `</tbody>
                    </table>
                </div>
            </div>`

    html += footer
    $('#pnl-area').append(html)
}

function render_history_ele(api_name, data) {
    let html = `<div class="card">
                <div class="card-header bg-warning">
                    <span>
                        ${api_name}
                    </span>
                </div>
                <div class="card-body">
                    <table class="table table-bordered">
                        <thead>
                        <tr>
                            <th scope="col">#</th>
                            <th scope="col">${data[0].t}</th>
                            <th scope="col">${data[1].t}</th>
                            <th scope="col">PNL</th>
                            <th scope="col">Price Target</th>
                        </tr>
                        </thead>
                        <tbody>`
    for (const [key, item] of Object.entries(data[0])) {
        if ('t' == key || 'total' == key) {
            continue
        }
        let coins = `<tr class="${fetch_class_tr(data, key)}">
                        <th scope="row">${key}</th>
                        <td>${numberWithCommas(data[0][key] ? data[0][key]['balance'] : 0)}</td>
                        <td>${numberWithCommas(data[1][key] ? data[1][key]['balance'] : 0)}</td>
                        <td class="${define_color_text(numberWithCommas(data[1][key] ? data[1][key]['PnL'] : 0))}">${numberWithCommas(data[1][key] ? data[1][key]['PnL'] : 0)}</td>
                        <td>${data[1][key] ? data[1][key]['PriceInTarget'] : 0}</td>
                    </tr>`
        html += coins
    }
    // total
    let total_html = `<tr>
                        <th scope="row">TOTAL</th>
                        <td colspan="4" class="text-center bg-light ${define_color_text(numberWithCommas(data[1]['total']))}">${numberWithCommas(data[1]['total'])}</td>
                    </tr>`
    html += total_html
    let footer = `</tbody>
                    </table>
                </div>
            </div>`

    html += footer
    $('#pnl-area').append(html)
}


function change_option_account() {
    if (api_json) {
        $('#api_name').empty()
        let list_api_exchange = fetch_api_follow_exchange($('#exchange').val())
        if (list_api_exchange.length > 0) {
            add_all_account()
        }
        for (let i = 0; i < list_api_exchange.length; i++) {
            let item = list_api_exchange[i]
            $('#api_name').append(`<option value="${item[0]}">${item[0]}</option>`)
        }

    }
    get_extension_info_pnl();
}

function fetch_api_follow_exchange(ex_id) {
    let rs = []
    for (let i = 0; i < api_json.length; i++) {
        let item = api_json[i]
        if (item[1] == $('#exchange').val()) {
            rs.push(item)
        }
    }
    return rs
}

function invoke_api_PNL() {
    $.ajax({
        url: `/pnls?ex_id=${$('#exchange').val()}&account=${$('#api_name').val()}`,
        type: 'GET',
        success: (data) => {
            render_pnl_table(data);
        },
        onerror: (e) => {
            console.log('Error ', e);
        }
    })
}

function invoke_get_apis() {
    $.ajax({
        url: `/apis`,
        type: 'GET',
        success: (data) => {
            api_json = data.apis
            change_option_account()
        },
        onerror: (e) => {
            console.log('Error ', e);
        }
    })
}

function invoke_api_update_comment() {
    $.ajax({
        url: `/update-comment?ex_id=${$('#exchange').val()}&account=${$('#api_name').val()}&comment=${$('#comment').val()}`,
        success: (data) => {
            if (data.rs) {
                alert('Update success')
            } else {
                alert(data.err)
            }
        },
        onerror: (e) => {
            console.log('Error ', e);
        }
    })
}

function get_extension_info_pnl() {
    $.ajax({
        url: `/extension-info-pnl?ex_id=${$('#exchange').val()}&account=${$('#api_name').val()}`,
        success: (data) => {
            console.log('data ', data);
            // call update comment, time refresh
            extra_info[$('#api_name').val()] = data
            update_comment_time_refresh(data)
        },
        onerror: (e) => {
            console.log('Error ', e);
        }
    })
}

function update_comment_time_refresh(data) {
    // $('#fresh_time').val(data['time_refresh'])
    $('#comment').val(data['comment'])
}

function render_pnl_table(data) {
    // clear pnl
    clear_space()
    if (data && Object.keys(data).length > 1) {
        // if (data) {
        // add total table
        let ele = Object.values(data)[0]
        let keys = Object.keys(ele[0])
        add_total_table(keys, data)
    }
    for (let [key, item] of Object.entries(data)) {
        render_pnl_ele(key, item)
    }
    $('#area_loading').hide();
}

function add_total_table(keys, all_ele) {
    let list_total = []
    let html = `<div class="card">
                <div class="card-header bg-warning">
                    <span>
                        TOTAL
                    </span>
                </div>
                <div class="card-body">
                    <table class="table table-bordered">
                        <thead>
                        <tr>
                            <th scope="col">#</th>
                            <th scope="col">START</th>
                            <th scope="col">STOP</th>
                            <th scope="col">PNL</th>
                            <th scope="col">Price Target</th>
                        </tr>
                        </thead>
                        <tbody>`
    for (const key of keys) {
        if ('t' == key || 'total' == key) {
            continue
        }
        let data = sum_coin_pnl(key, all_ele)
        list_total.push(data)
        let coins = `<tr class="${fetch_class_of_total_table(data)}">
                        <th scope="row">${key}</th>
                        <td>${numberWithCommas(data['start'])}</td>
                        <td>${numberWithCommas(data['current'])}</td>
                        <td class="${define_color_text(numberWithCommas(data['PnL']))}">${numberWithCommas(data['PnL'])}</td>
                        <td>${data['PriceInTarget']}</td>
                    </tr>`
        html += coins
    }
    // total
    let total_html = `<tr>
                        <th scope="row">TOTAL</th>
                        <td colspan="4" class="text-center bg-light ${define_color_text(numberWithCommas(get_total_pnl(list_total)))}">${numberWithCommas(get_total_pnl(list_total))}</td>
                    </tr>`
    html += total_html
    let footer = `</tbody>
                    </table>
                </div>
            </div>`

    html += footer
    $('#pnl-area').append(html)
}

function define_color_text(data) {
    if (parseFloat(data) > 0) {
        return 'text-success'
    } else if (parseFloat(data) == 0) {
        return 'text-dark'
    }
    return 'text-danger'
}

function sum_coin_pnl(coin, all_ele) {
    let start = 0
    let current = 0
    let PNL = 0
    let PriceInTarget = 0

    for ([key, item] of Object.entries(all_ele)) {
        if (item.length == 2) {
            start += item[0][coin] ? item[0][coin]['balance'] : 0
            current += item[1][coin] ? item[1][coin]['balance'] : 0
            PriceInTarget = item[1][coin] ? item[1][coin]['PriceInTarget'] : 0
        }
    }
    PNL = current - start
    return {
        start: start,
        current: current,
        PnL: PNL,
        PriceInTarget: PriceInTarget
    }
}

function get_total_pnl(arr_total) {
    // start * price / sum(current * price)
    let sum_pnl = 0
    for (const total of arr_total) {
        sum_pnl += total['PnL'] * total['PriceInTarget']
    }
    return sum_pnl
}

function render_pnl_ele(key, data) {
    if (!data || data.length < 2) {
        return
    }
    let html = `<div class="card">
                <div class="card-header bg-warning">
                    <span>
                         ${key}
                    </span>
                </div>
                <div class="card-body">
                    <table class="table table-bordered">
                        <thead>
                        <tr>
                            <th scope="col">#</th>
                            <th scope="col">${data[0].t}</th>
                            <th scope="col">${data[1].t}</th>
                            <th scope="col">PNL</th>
                            <th scope="col">Price Target</th>
                        </tr>
                        </thead>
                        <tbody>`
    for (const [key, item] of Object.entries(data[0])) {
        if ('t' == key || 'total' == key) {
            continue
        }
        let coins = `<tr class="${fetch_class_tr(data, key)}">
                        <th scope="row">${key}</th>
                        <td>${numberWithCommas(data[0][key] ? data[0][key]['balance'] : 0)}</td>
                        <td>${numberWithCommas(data[1][key] ? data[1][key]['balance'] : 0)}</td>
                        <td class="${define_color_text(numberWithCommas(data[1][key] ? data[1][key]['PnL'] : 0))}">${numberWithCommas(data[1][key] ? data[1][key]['PnL'] : 0)}</td>
                        <td>${data[1][key] ? data[1][key]['PriceInTarget'] : 0}</td>
                    </tr>`
        html += coins
    }
    // total
    let total_html = `<tr>
                        <th scope="row">TOTAL</th>
                        <td colspan="4" class="text-center bg-light ${define_color_text(numberWithCommas(data[1]['total']))}(">${numberWithCommas(data[1]['total'])}</td>
                    </tr>`
    html += total_html
    let footer = `</tbody>
                    </table>
                </div>
            </div>`

    html += footer
    $('#pnl-area').append(html)
}

function numberWithCommas(x) {
    if (!x) {
        return 0;
    }
    return x.toFixed(6).toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",");
}

function fetch_class_tr(data, key) {
    if (data.length >= 2) {
        if (parseFloat(numberWithCommas(data[0][key]['balance'])) == 0 && (!data[1][key] || parseFloat(numberWithCommas(data[1][key]['balance'])) == 0)) {
            return 'hidden';
        }
    }
    return 'normal';
}

function fetch_class_balance_tr(data, key) {
    if (parseFloat(numberWithCommas(data['balance'])) == 0) {
        return 'hidden';
    }
    return 'normal';
}

function fetch_class_of_total_table(data) {
    console.log(data, parseFloat(data['start']) == 0)
    if (parseFloat(numberWithCommas(data['start'])) == 0 && parseFloat(numberWithCommas(data['current'])) == 0) {
        return 'hidden';
    }
    return 'normal';
}