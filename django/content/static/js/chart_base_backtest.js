// var data_p = []
// // dataPoints = JSON.parse(dataPoints)
// console.log(dataPoints)

// for(var i=0; i< dataPoints.length; i++){
// 	n = dataPoints[i]
// 	data_p[i] = {x: new Date(n.x), y: n.y, e: n.e}
// }

// Get previous cdl from start_time

var chart = new CanvasJS.Chart("chartContainer", {
    title: {
        text: uuid,
        fontFamily: "times new roman"
    },
    zoomEnabled: true,
    exportEnabled: true,
    axisY: {
        includeZero: false,
        title: "Prices",
        prefix: "$ "
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
                            event_type = 'placed order'
                        } else if (event.s == 'filled') {
                            event_type = 'order fulfilled'
                            filled_data = ' <strong>filled: </strong>'+event.ac+'@'+event.ap
                        } else if (event.s == 'canceled') {
                            event_type = 'canceled order'
                            if (event.ac > 0) {
                                filled_data = ' <strong>but filled: </strong>'+event.ac+'@'+event.ap
                            }
                        }
                        content += '<strong>'+CanvasJS.formatDate(event.t * 1000, 'HH:mm:ss')+'</strong>'+': '+event_type+' '+`<span style="color:${color};">`+event.d+'</span>'+' '+event.a+'_'+event.r+'@'+event.p+filled_data+'<br/>'
                    }
                }

            }
            return content;
        }
    },
    theme: "dark1",
    gridColor: "#231717",
    data: [{
        type: "candlestick",
        risingColor: "green",
        fallingColor: "red",
        dataPoints: data_p
    }]
});
// chart.render();
