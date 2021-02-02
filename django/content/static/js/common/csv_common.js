$(document).ready(() => {

    $('#area_loading').show();
    if (!data_url) {
        console.log('data_url cannot found!!!')
    } else {
        render_monitor_link(data_url)
        $('#area_loading').hide();
    }
})

$(document).scroll((ev) => {
    let table_balance = $('#theadBalance')
    if (table_balance.length) {
        let headerTable = $(table_balance[0])
        let top_table = $('#table-monitor-link').offset().top
        //    cal top
        if (parseInt($(document).scrollTop()) - parseInt(top_table) > 0) {
            let newTopCss = `${parseInt($(document).scrollTop()) - parseInt(top_table) - 20}px`
            headerTable.css('position', 'absolute')
            headerTable.css('top', newTopCss)
        } else {
            headerTable.css('position', 'static')
            headerTable.css('top', '0px')
        }
    }
})

function clear_space() {
    $('#table-monitor-link').empty()
}

function render_monitor_link(data) {
    CsvToHtmlTable.init({
        csv_path: `${data}`,
        element: 'table-monitor-link',
        allow_download: true,
        csv_options: {separator: ',', delimiter: '"'},
        datatables_options: {"paging": false},
        custom_formatting: [[3, format_link]] //execute the function on the 4th column of every row
    });
    $('#area_loading').hide();

}

//my custom function that creates a hyperlink
function format_link(link) {
    if (link)
        return "<span class='uuid link text-primary' style='cursor: pointer'>" + link + "</span>" +
            "</br>" +
            "<span class='text-primary kill-bot' style='cursor: pointer'> Kill Bot</span>";
    else
        return "";
}

var choose_bot_action = null;

$(document).ready(() => {
    // $(document).on('click','.uuid.link',  (event) => {
        // show pop up
        // console.log('Open modal action support');
        // update selector bot
        // when had trigger kill bot or ... , using selector to send request kill bot
        // choose_bot_action = event.target;
        // console.log('Target is ', choose_bot_action);
        // get_info_bot();
        // $('#supportActionModalCenter').modal('show');
    // });
    $(document).on('click','.kill-bot',  (event) => {
        var response = confirm('Confirm Kill Bot');
        choose_bot_action = event.target;
        if (response == true) {
            console.log("You pressed OK!");
            let info = get_info_bot();
            $.ajax({
                  method: "POST",
                  url: "/support-kill-bot",
                  data: JSON.stringify({ info: info }),
                  contentType: "application/json",
                })
              .done(function( msg ) {
                // alert( "Data Saved: " + msg );
                  console.log(msg);
              });
        }
        else {
            console.log("You pressed Cancel!");
        }
    })
    $('#action-kill-bot').click((event) => {
        console.log('#action-kill-bot, Selector is ', choose_bot_action);
        get_info_bot()
    })

    $('#action-open-tracking').click((event) => {
        console.log('#action-open-tracking Selector is ', choose_bot_action);
        get_info_bot()
    })
})


function get_info_bot() {
    if (choose_bot_action) {
        let $span_bot_alias = $(choose_bot_action);
        let $tr_ele = $span_bot_alias.parent().parent();
        let tds = $tr_ele.find('td');
        let srv_info = $(tds[0]).text();
        let status = $(tds[1]).text();
        let uuid = $(tds[2]).text();
        let bot_alias = $($span_bot_alias.parent().find('.uuid.link').first()).text();

        let user = $(tds[4]).text();
        let api_name = $(tds[5]).text();
        console.log(`srv info ${srv_info} -- status ${status} -- uuid ${uuid} -- ${bot_alias} -- ${user} -- ${api_name}`)
        return [srv_info, status, uuid, bot_alias, user, api_name]
    } else {
        alert('Error when get info bot to action, sorry about that, Please reload page');
    }
}
