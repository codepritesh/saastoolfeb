var uuid = uuidv1()
var control_sk = new WebSocket('ws://' + window.location.host + '/ws/backtest/' + uuid + '/control');
var dataPoints = []
var data_p = []

$(document).ready(() => {
    $('#area_loading').hide();
    $('#btn-download-backtest').on('click', () => {
        let data = fetch_data_input();
        try {
            control_sk.send(JSON.stringify(data));
            $('#area_loading').show();
        } catch (e) {
            alert(e)
        }

    })
    control_sk.onmessage = (e) => {
        let i_data = JSON.parse(e.data).message
        let url = i_data.url
        if (!url) {
            url = i_data;
            alert(url);
            download_log(url);
            $('#area_loading').hide();
        } else {
            dataPoints = i_data.d_data
            console.log(url, dataPoints)
            render_chart_bt()
            alert(url);
            download_log(url);
            $('#area_loading').hide();
        }
    }
    $("#cb_using_time_out").change(() => {
        init_state_condition_finish();
    });
    // init state
    init_state_condition_finish();
    index_link();
})

function index_link() {
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
            $(value).removeClass('menu-open');
            let serach_link = $(value).find(`a[href='${short_url}']`);
            if (serach_link.length) {
                $(value).addClass('menu-open');
            }
        })
        // clear link
        $(link[0]).addClass('active');
    }
}

function render_chart_bt() {
    // dataPoints = JSON.parse(dataPoints)
    console.log(dataPoints)

    if (!dataPoints.length) {
        return;
    }
    for (var i = 0; i < dataPoints.length; i++) {
        n = dataPoints[i]
        data_p[i] = {x: new Date(n.x), y: n.y, e: n.e}
    }
    chart.render();
}

function init_state_condition_finish() {
    if ($('#cb_using_time_out').is(':checked')) {
        $('#duration').parent().show();
        $('#profit_desire').parent().hide();
    } else {
        $('#duration').parent().hide();
        $('#profit_desire').parent().show();
    }
}

/**
 * Download log
 */
function download_log(file) {
    window.location.href = `/logs/${file}`;
}
