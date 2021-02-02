/**
 * render log
 * @param msg
 */
let count_log = 0;
const NUM_LOG = 200;

function render_log(msg) {
    let cancel_log_area = $('#trader-log');
    var mesg = JSON.parse(msg.data).message
    cancel_log_area.append(`<p id="log_${count_log}">${mesg}</p>`);
    count_log++;
    if (NUM_LOG < count_log) {
        let subtract_log = count_log - NUM_LOG - 1;
        let ele = $(`#log_${subtract_log}`);
        if (ele.length > 0) {
            ele.remove();
        }
    }
    // print warring text
    if (msg.data.includes('ERROR')) {
        // $('#error-lable').text(mesg);
        let alertError = `<div class="alert alert-danger alert-dismissible" style="z-index: 99">
                <button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>
                <h5><i class="icon fas fa-ban"></i> Alert! Something Wrong</h5>
                <span>${mesg}</span>
            </div>`
        $('#eror-area').append(alertError)
    }
    if (msg.data.includes('TERMINATE')) {
        $('#exampleModalCenter').modal('show');
        //    show btn download report
        $('#btn-download-report').show();
    }
    if ($('#scroll-cb').is(":checked")) {
        // it is checked
        let objDiv = document.getElementById("trader-log");
        objDiv.scrollTop = objDiv.scrollHeight;
    }
}

/**
 * render price table
 * @param msg
 */
function render_price_trade(msg) {
    let body_price_table = $('#body_price_table');
    

    // parse data
    var mesg = JSON.parse(msg.data).message;
   
    let chain = mesg.Chain;
    chain = chain.replace('/', '_');
    let bid = mesg.Bid;
    let ask = mesg.Ask;
    let pair_price = body_price_table.find(`#${chain}`);
    if (!pair_price.length) { // exits
        // update ask, bid
        let html_add = `<tr id="${chain}"><td class="chain">${chain}</td><td class="bid">${bid}</td><td class="ask">${ask}</td></tr>`;
        body_price_table.append(html_add);
    } else {
        // update
        let bid_ele = pair_price.find('.bid');
        if (bid_ele.length) {
            define_color_background(bid_ele, bid_ele.text(), bid);
        }
        let ask_ele = pair_price.find('.ask');
        if (ask_ele.length) {
            define_color_background(ask_ele, ask_ele.text(), ask);
        }
        // update data
        bid_ele.text(bid);
        ask_ele.text(ask);
    }
    console.log(mesg);
    put_data_to_table(mesg);
}

/**
 * render pnl table
 * @param msg
 */
function render_pnl_trade(msg) {
    let body_pnl_table = $('#body_pnl_table');
    // parse data
    var mesgs = JSON.parse(msg.data).message
//    console.log('mesgs = ', mesgs)
//    var mesgs = [{"Coin": "BTC", "Start": 12, "Current": 13, "Margin": -1, "PNL": 111, "Price": 1},
//                {"Coin": "USDT", "Start": 1, "Current": 13, "Margin": -1, "PNL": 112, "Price": 2},
//                {"Coin": "BNB", "Start": 2, "Current": 13, "Margin": -1, "PNL": 113, "Price": 3},
//                {"Coin": "TOTAL", "Start": '', "Current": '', "Margin": "TOTAL", "PNL": 555, "Price": ''},
//                {"Coin": "PERCENT", "Start": '', "Current": '', "Margin": "%PNL", "PNL": 0.55, "Price": ''},
//                ]
    for (var i = 0; i < mesgs.length; i++) {
        mesg = mesgs[i]
//        console.log('mes = ', mesg)
        let coin = mesg.Coin;
        let start = mesg.Start ? mesg.Start : ' ';
        let current = mesg.Current ? mesg.Current : ' ';
        let margin = mesg.Margin;
        let pnl = mesg.PNL ? mesg.PNL : 0;
        let price = mesg.Price ? mesg.Price : ' ';
        let pair_price = body_pnl_table.find(`#${coin}`);
        if (!pair_price.length) { // exists
            // update ask, bid
            if (coin == "TOTAL" || coin == "PERCENT") {
                let html_add = `<tr id="${coin}"><td class="coin"></td><td class="start">${start}</td><td class="current">${current}</td><td class="margin"><b>${margin}</b></td><td class="pnl">${pnl}</td><td class="price">${price}</td></tr>`;
                body_pnl_table.append(html_add);
            }
            else {
                let html_add = `<tr id="${coin}"><td class="coin">${coin}</td><td class="start">${start}</td><td class="current">${current}</td><td class="margin">${margin}</td><td class="pnl">${pnl}</td><td class="price">${price}</td></tr>`;
                body_pnl_table.append(html_add);
            }
        } else {
            // update
            let start_ele = pair_price.find('.start');
            let current_ele = pair_price.find('.current');
            let margin_ele = pair_price.find('.margin');
            let pnl_ele = pair_price.find('.pnl');
            let price_ele = pair_price.find('.price');
            if (pnl_ele.length) {
                define_color_background(pnl_ele, 0, pnl);
            }
            if ( typeof margin != 'string') {
                margin_ele.text(margin);
                define_color_background(margin_ele, 0, margin);
            }
            // update data
            start_ele.text(start);
            current_ele.text(current);
            pnl_ele.text(pnl);
            price_ele.text(price);
        }
    }
}

/**
 * define color for element price
 */
function define_color_background(ele, current_value, future_value) {
    if (parseFloat(current_value) < parseFloat(future_value)) {
        $(ele).removeClass('text-success text-danger').addClass('text-success');
    } else if (parseFloat(current_value) > parseFloat(future_value)) {
        $(ele).removeClass('text-success text-danger').addClass('text-danger');
    }
    // equal --> no change
    return true;
}

/**
 * render table pnl
 * data= {
 *      'name': x,
 *     'start': x,
 *     'current': x,
 *     'in_order': x,
 *     'stop': x,
 *     'pnl': x,
 *     'profit_row': x
 * }
 */
function render_table_pnl(ele, data) {
    let $self = $(ele);
    $self.find('th:nth-child(1)').text(data['name']);
    $self.find('td:nth-child(2)').text(data['start']);
    $self.find('td:nth-child(3)').text(data['current']);
    $self.find('td:nth-child(4)').text(data['in_order']);
    $self.find('td:nth-child(5)').text(data['stop']);
    $self.find('td:nth-child(6)').text(data['pnl']);
    $self.find('td:nth-child(8)').text(data['profit_row']);
}

$(document).ready(() => {
    $('#btn-show-stop-bot').on('click', () => {
        // show pop up
        $('#killBotModalCenter').modal('show')
    });
})

$(document).ready(() => {
    let url = location.href;
    let short_url = url.replace(location.origin, '')
    let lastChar = short_url.substring(short_url.length - 1)
    if (lastChar == '/') {
        short_url = short_url.substring(0, short_url.length - 1)
    }
    let li_menu = $('#side-menu').find('li.nav-item.has-treeview');
    let link = $(document).find(`#side-menu a[href='${short_url}']`);
    let allLink = $(document).find(`#side-menu a`);
    if (link.length) {
        $.each(li_menu, (index, value) => {
            console.log('ele ', value);
            $(value).removeClass('menu-open');
            let serach_link = $(value).find(`a[href='${short_url}']`);
            if (serach_link.length) {
                $(value).addClass('menu-open');
            }
        })
        // clear link
        $(link[0]).addClass('active');
    }
})

function numberWithCommas(x) {
    if (!x) {
        return 0;
    }
    return x.toFixed(6).toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",");
}
