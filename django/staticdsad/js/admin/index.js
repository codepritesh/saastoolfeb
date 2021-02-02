function fetch_data() {
    return {
        time_refresh: $('#time_refresh').val(),
        coin_list: $('#coin_list').val(),
    }
}

$(document).ready(() => {
    $('#btn-update').on('click', (e) => {
        update_time_refresh()
        // get_all_coins()
    })
})

function update_time_refresh() {
    $.ajax({
        url: `/update-time-refresh?time_refresh=${$('#time_refresh').val()}&coins=${$('#coin_list').val()}`,
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

function get_all_coins() {
    $.ajax({
        url: `/coins`,
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