var alias = bot_alias;

var trackingSocket = new WebSocket('ws://' + window.location.host +'/ws/' + suff_ws + '/' + alias + srv_id + '/tracking');
//console.log(trackingSocket);
//

$(document).ready(() => {
    trackingSocket.onmessage = function(e) {
    var datas = JSON.parse(e.data);
    var data = datas['message'];
    if (Array.isArray(data)) {
        let ele_parent = $('#table-instance-running');
        $(ele_parent).empty();
        for (item in data) {

            
            var abot = data[item];
            if(abot.own_name==tracking_user){
            //console.log(abot.own_name+tracking_user);
            let append_html = `<tr id=${abot.uuid}>\
                                 <td><a href="/${bot_url}/${abot.uuid}" target="_blank">${abot.uuid}</a></td>\
                                 <td>${abot.time}</td>\
                                 <td>${abot.own_name}</td>\
                                 <td>${abot.ex_id}</td>\
                                 <td>${abot.api_name}</td>\
                                 <td>${abot.pair}</td>\
                                 <td><a href="${abot.link_grafana}" target="_blank">${abot.link_grafana}</a></td>\
                               </tr>`;
            if (ele_parent.length) {
                let ele = $('#' + abot.uuid);
                if (!ele.length) { // not exits
                    if (append_html) {
                        ele_parent.append(append_html);
                    }//end if--1
                } // end if --2
            }// end if --3
        } // end abot.own_name
          }//endfor
  //  block of code to be executed if the condition is true
} 
else {
      //console.log(data);
       get_bot_running_data(data)
       
       
 

}

        
        };// end on message function(e)
        trackingSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
    };// end on onclose function(e)
}); // end document.ready



function get_bot_running_data(data) {
    var i;
    var j;
    for (i = 0; i < Object.keys(data).length; i++) {
               var botvar = data[Object.keys(data)[i]];
                    switch (Object.keys(data)[i]) {
                      case 'Arb2WayBot':
                      var k = 0;
                        for (j = 0; j < botvar.length; j++) {
                                       //console.log(botvar[j]);
                                         var user_bot = botvar[j]
                                         if (user_bot["own_name"] == user ){
                                               k=k+1;
                                           } 
                                       } 
                        $('#bot_count_four').text(k);
                        
                        break;

                      case 'AtrTrailingStopTool':
                      var k = 0;
                        for (j = 0; j < botvar.length; j++) {
                                       //console.log(botvar[j]);
                                         var user_bot = botvar[j]
                                         if (user_bot["own_name"] == user ){
                                               k=k+1;
                                           } 
                                       } 
                      
                      $('#bot_count_five').text(k);
                        
                        break;

                      case 'BSSBContinuouslyTool':
                      var k = 0;
                        for (j = 0; j < botvar.length; j++) {
                                       //console.log(botvar[j]);
                                         var user_bot = botvar[j]
                                         if (user_bot["own_name"] == user ){
                                               k=k+1;
                                           } 
                                       } 
                      
                      $('#bot_count_eight').text(k);
                        
                        break;


                      case 'ClearOrderBot':
                        var k = 0;
                        for (j = 0; j < botvar.length; j++) {
                                       //console.log(botvar[j]);
                                         var user_bot = botvar[j]
                                         if (user_bot["own_name"] == user ){
                                               k=k+1;
                                           } 
                                       }                 
                       $('#bot_count_one').text(k);
                        
                        break;


                      case 'SupportBigAmountBot':
                      var k = 0;
                        for (j = 0; j < botvar.length; j++) {
                                       //console.log(botvar[j]);
                                         var user_bot = botvar[j]
                                         if (user_bot["own_name"] == user ){
                                               k=k+1;
                                           } 
                                       } 
                      
                      $('#bot_count_two').text(k);
                        break;


                      case 'SupportMultiBoxBot':
                      var k = 0;
                        for (j = 0; j < botvar.length; j++) {
                                       //console.log(botvar[j]);
                                         var user_bot = botvar[j]
                                         if (user_bot["own_name"] == user ){
                                               k=k+1;
                                           } 
                                       } 
                      
                      $('#bot_count_seven').text(k);
                        
                        break;


                      case 'SupportTrailingStopBot':
                      var k = 0;
                        for (j = 0; j < botvar.length; j++) {
                                       //console.log(botvar[j]);
                                         var user_bot = botvar[j]
                                         if (user_bot["own_name"] == user ){
                                               k=k+1;
                                           } 
                                       } 
                      
                      $('#bot_count_three').text(k);
                                              
                        break;


                      case 'TwoWaySpBot':
                      var k = 0;
                        for (j = 0; j < botvar.length; j++) {
                                       //console.log(botvar[j]);
                                         var user_bot = botvar[j]
                                         if (user_bot["own_name"] == user ){
                                               k=k+1;
                                           } 
                                       } 
                      
                      $('#bot_count_six').text(k);
                        
                    }
                                   

                                } 
    return true ;

}

