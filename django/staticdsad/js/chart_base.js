console.log(`start time ${start_time} __ pair ${pair} end time ${end_time}`);

var data_p = [];
var order_open = {};
var order_history_fill = {};

// Get previous cdl from start_time
start_time = start_time - 60000
data_p = get_historical_klines(pair, '1m', start_time, end_time);

function get_historical_klines(symbol, interval, start_str, end_str) {
    if (!end_str) {
        end_str = Date.now();
    }
    var output_data = []
    let idx = 0;
    let time_frame = 500 // change when change interval
    while (true) {
        // fetch the klines from start_ts up to max 500 entries or the end_ts if set
        let temp_data = fetch_data_candle(start_str, end_str)
        //console.log('template_data ', temp_data)
        if (!temp_data.length) {
            break;
        }
        // append this loops data to our output data
        for (let i = 0; i < temp_data.length; i++) {
            output_data.push(temp_data[i]);
        }
        // set our start timestamp using the last value in the array
        start_str = temp_data[temp_data.length - 1][0]
        idx += 1
        // check if we received less than the required limit and exit the loop
        if (temp_data.length < time_frame) {
            // exit the while loop
            break
        }
        if (idx % 3 === 0) {
            //    sleep 1 s
            setTimeout(() => {
                //console.log("Sleep 1s");
            }, 1000);
        }
        if (parseFloat(start_str) >= parseFloat(end_str)) {
            break;
        }
    }
    let data_event = fetch_data_event();
    split_order_to_open_and_none(data_event);
    return build_data_canvas(output_data, data_event)
}

function split_order_to_open_and_none(data_event) {
    if (!data_event) {
        return
    }
    //
    let keys = Object.keys(data_event);
    for (const key of keys) {
        if (Array.isArray(data_event[key])) {
            //
            for (const order of data_event[key]) {
                if ('open' == order.s) {
                    if (!order_open[order.i] || order.ac > order_open[order.i].ac) {
                        order_open[order.i] = order;
                        if (!order_history_fill[order.i] && parseFloat(order.ac) > 0) {
                            order_history_fill[order.i] = [order]
                        } else if (parseFloat(order.ac) > 0) {
                            order_history_fill[order.i].push(order)
                        }
                        build_order_html(order, $('#body-open-order'), false);
                    }
                } else {
                    build_order_html(order, $('#body-order-history'), true);
                    remove_order_when_close_or_cancel(order);
                }
            }
        }
    }
}

function build_order_html(order_info, ele_father, is_not_open) {
    let s_class = 'table-light'
    if (order_info.s == 'closed') {
        s_class = 'table-success';
    } else if (order_info.s == 'canceled') {
        s_class = 'table-danger';
    }
    if (ele_father.find(`tr#${order_info.i}`).length) {
        // TODO: check partial fill for open order
        if (!is_not_open) {
            // update view
            // console.log('Update partial filled', order_info);
            $($(ele_father.find(`tr#${order_info.i}`)[0]).find('td:nth-child(6)')[0]).text(order_info.ac)
        }
        return
    }
    let side_class = 'text-danger';
    if ('buy' == order_info.d) {
        side_class = 'text-success';
    }
    let html = '';
    if (!is_not_open) {
        html = `<tr id="${order_info.i}" class="${s_class}">
                    <td>${CanvasJS.formatDate(new Date(parseInt(order_info.t)), 'YYYY-MMM-DD HH:mm:ss')}</td>
                    <td>${order_info.i}</td>
                    <td>${order_info.r}</td>
                    <td><span class="${side_class}">${order_info.d} </span></td>
                    <td>${order_info.a}</td>
                    <td>${order_info.ac}</td>
                    <td>${order_info.p}</td>
                    <td>${order_info.s}</td>
                </tr>`;
    } else {
        html = `<tr id="${order_info.i}" class="${s_class}" data-toggle="collapse" data-target=".collapse-${order_info.i}" aria-expanded="false" data-time="${order_info.t}">
                    <th scope="row">${$(ele_father).find('tr').length}</th>
                    <td>${order_open[order_info.i] ? CanvasJS.formatDate(new Date(parseInt(order_open[order_info.i].t)), 'YYYY-MMM-DD HH:mm:ss') : CanvasJS.formatDate(new Date(parseInt(order_info.t)), 'YYYY-MMM-DD HH:mm:ss')}</td>
                    <td>${CanvasJS.formatDate(new Date(parseInt(order_info.t)), 'YYYY-MMM-DD HH:mm:ss')}</td>
                    <td>${order_info.i}</td>
                    <td>${order_info.r}</td>
                    <td><span class="${side_class}">${order_info.d} </span></td>
                    <td>${order_info.a}</td>
                    <td>${order_info.ac}</td>
                    <td>${order_info.p}</td>
                    <td>${order_info.s}</td>
                </tr>`;
        if (order_history_fill[order_info.i]) {
            for (const item of order_history_fill[order_info.i]) {
                //console.log(item);
                let partial_html = ` <tr>
                    <td colspan="2"  class="hiddenRow"></td>
                    <td colspan="1"  class="hiddenRow">
                        <div class="collapse-${order_info.i} accordian-body collapse">${CanvasJS.formatDate(new Date(parseInt(item.t)), 'YYYY-MMM-DD HH:mm:ss')}</div>
                    </td>
                    <td colspan="4"  class="hiddenRow"></td>
                    <td colspan="1"  class="hiddenRow">
                        <div class="collapse-${order_info.i} accordian-body collapse">${item.ac}</div>
                    </td>
                    <td colspan="2"  class="hiddenRow"></td>
                </tr>`;
                html += (partial_html)
            }
        }
    }
    $(ele_father).append(html);
    if (is_not_open && $('#scroll-cb-open-order').is(":checked")) {
        let objDiv = document.getElementById("open-order-list");
        objDiv.scrollTop = objDiv.scrollHeight;
    } else if (!is_not_open && $('#scroll-cb-order-history').is(":checked")) {
        let objDiv = document.getElementById("order-history-list");
        objDiv.scrollTop = objDiv.scrollHeight;
    }
    if (!is_not_open) {
        $('#total_number_order').text(Object.values(order_open).length);
    }
}

function remove_order_when_close_or_cancel(order_info) {
    let open_order_ele = $('#body-open-order');
    if (open_order_ele.find(`tr#${order_info.i}`).length) {
        open_order_ele.find(`tr#${order_info.i}`).remove();
        delete order_open[order_info.i];
        $('#total_number_order').text(Object.values(order_open).length);
    }
}

function fetch_data_candle(start, end_time) {
    let rs_data = [];
    $.ajax({
        url: `https://api.binance.com/api/v3/klines?symbol=${pair}&interval=1m&startTime=${start}&endTime=${end_time}&limit=500`,
        success: (data) => {
            rs_data = data;
        },
        async: false,
        onerror: (e) => {
            console.log('Error ', e);
            return []
        }
    })
    return rs_data;
}

function fetch_data_event() {
    let rs_data = [];
    let last_time = '';
    let last_open_ele = $($('#body-order-history').find(`tr`).last())
    if (last_open_ele.length) {
        last_time = last_open_ele.attr('data-time');
        if (last_time == null) {
            last_time = ''
        }
        console.log(`last_time ${last_time}`);
    }
    $.ajax({
        url: `/event-bot?uuid=${uuid}&last_time=${last_time}`,
        success: (data) => {
            rs_data = data;
        },
        async: false,
        onerror: (e) => {
            console.log('Error ', e);
            rs_data = []
        }
    })
    return rs_data;
}

function build_data_canvas(ohlcv, events) {
    let p = [];
    for (let i = 0; i < ohlcv.length; i++) {
        let item = {
            x: new Date(parseInt(ohlcv[i][0])), y: [parseFloat(ohlcv[i][1]),
                parseFloat(ohlcv[i][2]), parseFloat(ohlcv[i][3]), parseFloat(ohlcv[i][4])],
            e: ""
        };
        let key = ohlcv[i][0];
        if (events[key]) {
            item = {
                x: new Date(parseInt(ohlcv[i][0])), y: [parseFloat(ohlcv[i][1]),
                    parseFloat(ohlcv[i][2]), parseFloat(ohlcv[i][3]), parseFloat(ohlcv[i][4])],
                e: events[key]
            }

        }
        p.push(item)
    }
    return p;
}

var chart = new CanvasJS.Chart("chartContainer", {
    title: {
        text: uuid,
        fontFamily: "times new roman"
    },
    theme: "dark1",
    zoomEnabled: true,
    exportEnabled: true,
    axisY: {
        includeZero: false,
	gridColor: "#231717",
    },
    toolTip: {
        contentFormatter: function (e) {
            var content = "";
            var color = "green";
            var event_type = "";
            var filled_data = "";
            for (var i = 0; i < e.entries.length; i++) {
                content = '<strong>Time: </strong>'+CanvasJS.formatDate(e.entries[i].dataPoint.x, 'YYYY-MMM-DD HH:mm');
                content += '<br/>' + '<strong>O:</strong>' + e.entries[i].dataPoint.y[0] +
                            '<strong> H:</strong>' + e.entries[i].dataPoint.y[1] +
                            '<strong> L:</strong>' + e.entries[i].dataPoint.y[2] +
                            '<strong> C:</strong>' + e.entries[i].dataPoint.y[3];
                if (e.entries[i].dataPoint.e){
                    content += '<br/><br/>' + '<strong>Event:</strong><br/>'
                    for (let event of e.entries[i].dataPoint.e) {
                        event_type = ""
                        filled_data = ""
                        if (event.d == 'buy') {
                            color = 'green'
                        } else {
                            color = 'red'
                        }
                        if (event.s == 'open') {
                            if (event.ap) {
                                event_type = 'partial-filled'
                                filled_data = ' <strong>filled: </strong>'+event.ac+'@'+event.ap
                            } else {
                                event_type = 'placed order'
                            }
                        } else if (event.s == 'closed') {
                            event_type = 'order fulfilled'
                            filled_data = ' <strong>filled: </strong>'+event.ac+'@'+event.ap
                        } else if (event.s == 'canceled') {
                            event_type = 'canceled order'
                            if (event.ac > 0) {
                                filled_data = ' <strong>but filled: </strong>'+event.ac+'@'+event.ap
                            }
                        }
                        content += '<strong>'+CanvasJS.formatDate(parseInt(event.t), 'HH:mm:ss')+'</strong>'+' '+event_type+' '+`<span style="color:${color};">`+event.d+'</span>'+' '+event.a+'_'+event.r+'@'+event.p+filled_data+'<br/>'
                    }
                }

            }
            return content;
        }
    },
    data: [{
        type: "candlestick",
        risingColor: "#74e185",
        fallingColor: "#b2271f",
        dataPoints: data_p
    }]
});
chart.render();


var interval = setInterval(() => {
    // if has end time, no need to refresh
    if (end_time) {
        clearInterval(interval);
        return
    }
    let last_item = data_p[data_p.length - 1];
    let start_time = last_item.x.getTime();
    let data = get_historical_klines(pair, '1m', start_time, end_time);
    for (let i = 0; i < data.length; i ++) {
        const item = data[i];
        if (last_item.x.getTime() === item.x.getTime()) {
            data_p.pop();
        }
        if (data.length - 1 === i) {
            // last item
            item.p = Object.values(order_open)
        }
        data_p.push(item);
    }
    chart.render();
}, 1 * 1000);


$(document).ready(() => {
    $('.accordian-body').on('show.bs.collapse', function () {
        $(this).closest("table")
            .find(".collapse.in")
            .not(this)
            .collapse('toggle')
    })
})
