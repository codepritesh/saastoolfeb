function connect() {
    var log_sk = new WebSocket(`ws://${window.location.host}/ws/${ws_define}/${uuid}/log`);

    // log
    log_sk.onclose = (e) => {
        console.log('Socket log is closed. Reconnect will be attempted in 1 second.', e.reason);
    }

    log_sk.onerror = function (err) {
        console.error('Socket log encountered error: ', err.message, 'Closing socket');
        setTimeout(function () {
            connect();
        }, 1000);
    };

    log_sk.onmessage = function (e) {
        render_log(e);
    };
}


$(document).ready(() => {
    connect();
});
