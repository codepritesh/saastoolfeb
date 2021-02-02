function put_data_to_table(mesg) {

	$("#socket_table").css("display", "block");
//$("#id").css("display", "block");
//"mesg" variable defined in index.js	static/js/common/index.js
// for allbot pls refer---->templates/components/bot_trading_socket_data_tab.html
	$('#all_row1_date').text(mesg['all_bot']['1']['timestamp']);
	$('#all_row1_pair').text(mesg['all_bot']['1']['pair']);
	$('#all_row1_type').text(mesg['all_bot']['1']['order_type']);
	$('#all_row1_side').text(mesg['all_bot']['1']['side']);
	$('#all_row1_apiname').text(mesg['all_bot']['1']['api_name']);
	$('#all_row1_price').text(mesg['all_bot']['1']['price']);
	$('#all_row1_Order_Id').text(mesg['all_bot']['1']['order_id']);
	$('#all_row1_amount').text(mesg['all_bot']['1']['amount']);
	$('#all_row1_ExId').text(mesg['all_bot']['1']['ex_id']);
	$('#all_row1_Bot_Name').text(mesg['all_bot']['1']['database_bot_name']);
	$('#all_row1_status').text(mesg['all_bot']['1']['status']);

	$('#all_row2_date').text(mesg['all_bot']['2']['timestamp']);
	$('#all_row2_pair').text(mesg['all_bot']['2']['pair']);
	$('#all_row2_type').text(mesg['all_bot']['2']['order_type']);
	$('#all_row2_side').text(mesg['all_bot']['2']['side']);
	$('#all_row2_apiname').text(mesg['all_bot']['2']['api_name']);
	$('#all_row2_price').text(mesg['all_bot']['2']['price']);
	$('#all_row2_Order_Id').text(mesg['all_bot']['2']['order_id']);
	$('#all_row2_amount').text(mesg['all_bot']['2']['amount']);
	$('#all_row2_ExId').text(mesg['all_bot']['2']['ex_id']);
	$('#all_row2_Bot_Name').text(mesg['all_bot']['2']['database_bot_name']);
	$('#all_row2_status').text(mesg['all_bot']['2']['status']);

    $('#all_row3_date').text(mesg['all_bot']['3']['timestamp']);
	$('#all_row3_pair').text(mesg['all_bot']['3']['pair']);
	$('#all_row3_type').text(mesg['all_bot']['3']['order_type']);
	$('#all_row3_side').text(mesg['all_bot']['3']['side']);
	$('#all_row3_apiname').text(mesg['all_bot']['3']['api_name']);
	$('#all_row3_price').text(mesg['all_bot']['3']['price']);
	$('#all_row3_Order_Id').text(mesg['all_bot']['3']['order_id']);
	$('#all_row3_amount').text(mesg['all_bot']['3']['amount']);
	$('#all_row3_ExId').text(mesg['all_bot']['3']['ex_id']);
	$('#all_row3_Bot_Name').text(mesg['all_bot']['3']['database_bot_name']);
	$('#all_row3_status').text(mesg['all_bot']['3']['status']);
// for allbot

// for bot1
$('#bot1_row1_date').text(mesg['bot1']['1']['timestamp']);
$('#bot1_row1_accu_amount').text(mesg['bot1']['1']['accu_amount']);
$('#bot1_row1_amount').text(mesg['bot1']['1']['amount']);
$('#bot1_row1_api_name').text(mesg['bot1']['1']['api_name']);
$('#bot1_row1_avg_price').text(mesg['bot1']['1']['avg_price']);
$('#bot1_row1_creation_time').text(mesg['bot1']['1']['creation_time']);
$('#bot1_row1_ex_id').text(mesg['bot1']['1']['ex_id']);
$('#bot1_row1_input_pair').text(mesg['bot1']['1']['input_pair']);
$('#bot1_row1_input_side').text(mesg['bot1']['1']['input_side']);
$('#bot1_row1_input_signal').text(mesg['bot1']['1']['input_signal']);
$('#bot1_row1_is_using').text(mesg['bot1']['1']['is_using']);
$('#bot1_row1_pair').text(mesg['bot1']['1']['pair']);
$('#bot1_row1_order_id').text(mesg['bot1']['1']['order_id']);
$('#bot1_row1_price').text(mesg['bot1']['1']['price']);
$('#bot1_row1_price_type').text(mesg['bot1']['1']['price_type']);
$('#bot1_row1_side').text(mesg['bot1']['1']['side']);
//$('#bot1_row1_update_time').text(mesg['bot1']['1']['update_time']);
$('#bot1_row1_uuid').text(mesg['bot1']['1']['uuid']);
$('#bot1_row1_order_status').text(mesg['bot1']['1']['order_status']);

$('#bot1_row2_date').text(mesg['bot1']['2']['timestamp']);
$('#bot1_row2_accu_amount').text(mesg['bot1']['2']['accu_amount']);
$('#bot1_row2_amount').text(mesg['bot1']['2']['amount']);
$('#bot1_row2_api_name').text(mesg['bot1']['2']['api_name']);
$('#bot1_row2_avg_price').text(mesg['bot1']['2']['avg_price']);
$('#bot1_row2_creation_time').text(mesg['bot1']['2']['creation_time']);
$('#bot1_row2_ex_id').text(mesg['bot1']['2']['ex_id']);
$('#bot1_row2_input_pair').text(mesg['bot1']['2']['input_pair']);
$('#bot1_row2_input_side').text(mesg['bot1']['2']['input_side']);
$('#bot1_row2_input_signal').text(mesg['bot1']['2']['input_signal']);
$('#bot1_row2_is_using').text(mesg['bot1']['2']['is_using']);
$('#bot1_row2_pair').text(mesg['bot1']['2']['pair']);
$('#bot1_row2_order_id').text(mesg['bot1']['2']['order_id']);
$('#bot1_row2_price').text(mesg['bot1']['2']['price']);
$('#bot1_row2_price_type').text(mesg['bot1']['2']['price_type']);
$('#bot1_row2_side').text(mesg['bot1']['2']['side']);
//$('#bot1_row2_update_time').text(mesg['bot1']['2']['update_time']);
$('#bot1_row2_uuid').text(mesg['bot1']['2']['uuid']);
$('#bot1_row2_order_status').text(mesg['bot1']['2']['order_status']);

$('#bot1_row3_date').text(mesg['bot1']['3']['timestamp']);
$('#bot1_row3_accu_amount').text(mesg['bot1']['3']['accu_amount']);
$('#bot1_row3_amount').text(mesg['bot1']['3']['amount']);
$('#bot1_row3_api_name').text(mesg['bot1']['3']['api_name']);
$('#bot1_row3_avg_price').text(mesg['bot1']['3']['avg_price']);
$('#bot1_row3_creation_time').text(mesg['bot1']['3']['creation_time']);
$('#bot1_row3_ex_id').text(mesg['bot1']['3']['ex_id']);
$('#bot1_row3_input_pair').text(mesg['bot1']['3']['input_pair']);
$('#bot1_row3_input_side').text(mesg['bot1']['3']['input_side']);
$('#bot1_row3_input_signal').text(mesg['bot1']['3']['input_signal']);
$('#bot1_row3_is_using').text(mesg['bot1']['3']['is_using']);
$('#bot1_row3_pair').text(mesg['bot1']['3']['pair']);
$('#bot1_row3_order_id').text(mesg['bot1']['3']['order_id']);
$('#bot1_row3_price').text(mesg['bot1']['3']['price']);
$('#bot1_row3_price_type').text(mesg['bot1']['3']['price_type']);
$('#bot1_row3_side').text(mesg['bot1']['3']['side']);
//$('#bot1_row3_update_time').text(mesg['bot1']['3']['update_time']);
$('#bot1_row3_uuid').text(mesg['bot1']['3']['uuid']);
$('#bot1_row3_order_status').text(mesg['bot1']['3']['order_status']);
// for bot1

// for bot2

$('#bot2_row1_date').text(mesg['bot2']['1']['timestamp']);
$('#bot2_row1_amount').text(mesg['bot2']['1']['amount']);
$('#bot2_row1_api_name').text(mesg['bot2']['1']['api_name']);
$('#bot2_row1_average').text(mesg['bot2']['1']['average']);
$('#bot2_row1_ex_id').text(mesg['bot2']['1']['ex_id']);
$('#bot2_row1_filled').text(mesg['bot2']['1']['filled']);
$('#bot2_row1_follow_gap').text(mesg['bot2']['1']['follow_gap']);
$('#bot2_row1_gap').text(mesg['bot2']['1']['gap']);
$('#bot2_row1_order_id').text(mesg['bot2']['1']['order_id']);
$('#bot2_row1_pair').text(mesg['bot2']['1']['pair']);
$('#bot2_row1_place_order_profit').text(mesg['bot2']['1']['place_order_profit']);
$('#bot2_row1_position').text(mesg['bot2']['1']['position']);
$('#bot2_row1_postOnly').text(mesg['bot2']['1']['postOnly']);
$('#bot2_row1_price').text(mesg['bot2']['1']['price']);
$('#bot2_row1_profit').text(mesg['bot2']['1']['profit']);
$('#bot2_row1_stop_loss').text(mesg['bot2']['1']['stop_loss']);
$('#bot2_row1_symbol').text(mesg['bot2']['1']['symbol']);
$('#bot2_row1_trailing_margin').text(mesg['bot2']['1']['trailing_margin']);
$('#bot2_row1_uuid').text(mesg['bot2']['1']['uuid']);
$('#bot2_row1_status').text(mesg['bot2']['1']['status']);

$('#bot2_row2_date').text(mesg['bot2']['2']['timestamp']);
$('#bot2_row2_amount').text(mesg['bot2']['2']['amount']);
$('#bot2_row2_api_name').text(mesg['bot2']['2']['api_name']);
$('#bot2_row2_average').text(mesg['bot2']['2']['average']);
$('#bot2_row2_ex_id').text(mesg['bot2']['2']['ex_id']);
$('#bot2_row2_filled').text(mesg['bot2']['2']['filled']);
$('#bot2_row2_follow_gap').text(mesg['bot2']['2']['follow_gap']);
$('#bot2_row2_gap').text(mesg['bot2']['2']['gap']);
$('#bot2_row2_order_id').text(mesg['bot2']['2']['order_id']);
$('#bot2_row2_pair').text(mesg['bot2']['2']['pair']);
$('#bot2_row2_place_order_profit').text(mesg['bot2']['2']['place_order_profit']);
$('#bot2_row2_position').text(mesg['bot2']['2']['position']);
$('#bot2_row2_postOnly').text(mesg['bot2']['2']['postOnly']);
$('#bot2_row2_price').text(mesg['bot2']['2']['price']);
$('#bot2_row2_profit').text(mesg['bot2']['2']['profit']);
$('#bot2_row2_stop_loss').text(mesg['bot2']['2']['stop_loss']);
$('#bot2_row2_symbol').text(mesg['bot2']['2']['symbol']);
$('#bot2_row2_trailing_margin').text(mesg['bot2']['2']['trailing_margin']);
$('#bot2_row2_uuid').text(mesg['bot2']['2']['uuid']);
$('#bot2_row2_status').text(mesg['bot2']['2']['status']);

$('#bot2_row3_date').text(mesg['bot2']['3']['timestamp']);
$('#bot2_row3_amount').text(mesg['bot2']['3']['amount']);
$('#bot2_row3_api_name').text(mesg['bot2']['3']['api_name']);
$('#bot2_row3_average').text(mesg['bot2']['3']['average']);
$('#bot2_row3_ex_id').text(mesg['bot2']['3']['ex_id']);
$('#bot2_row3_filled').text(mesg['bot2']['3']['filled']);
$('#bot2_row3_follow_gap').text(mesg['bot2']['3']['follow_gap']);
$('#bot2_row3_gap').text(mesg['bot2']['3']['gap']);
$('#bot2_row3_order_id').text(mesg['bot2']['3']['order_id']);
$('#bot2_row3_pair').text(mesg['bot2']['3']['pair']);
$('#bot2_row3_place_order_profit').text(mesg['bot2']['3']['place_order_profit']);
$('#bot2_row3_position').text(mesg['bot2']['3']['position']);
$('#bot2_row3_postOnly').text(mesg['bot2']['3']['postOnly']);
$('#bot2_row3_price').text(mesg['bot2']['3']['price']);
$('#bot2_row3_profit').text(mesg['bot2']['3']['profit']);
$('#bot2_row3_stop_loss').text(mesg['bot2']['3']['stop_loss']);
$('#bot2_row3_symbol').text(mesg['bot2']['3']['symbol']);
$('#bot2_row3_trailing_margin').text(mesg['bot2']['3']['trailing_margin']);
$('#bot2_row3_uuid').text(mesg['bot2']['3']['uuid']);
$('#bot2_row3_status').text(mesg['bot2']['3']['status']);




// for bot2


// for bot3
$('#bot3_row1_date').text(mesg['bot3']['1']['timestamp']);
$('#bot3_row1_amount').text(mesg['bot3']['1']['amount']);
$('#bot3_row1_api_name').text(mesg['bot3']['1']['api_name']);
$('#bot3_row1_average').text(mesg['bot3']['1']['average']);
$('#bot3_row1_cancel_threshold').text(mesg['bot3']['1']['cancel_threshold']);
$('#bot3_row1_entry_price').text(mesg['bot3']['1']['entry_price']);
$('#bot3_row1_ex_id').text(mesg['bot3']['1']['ex_id']);
$('#bot3_row1_filled').text(mesg['bot3']['1']['filled']);
$('#bot3_row1_follow_gap').text(mesg['bot3']['1']['follow_gap']);
$('#bot3_row1_gap').text(mesg['bot3']['1']['gap']);
$('#bot3_row1_input_amount').text(mesg['bot3']['1']['input_amount']);
$('#bot3_row1_input_pair').text(mesg['bot3']['1']['input_pair']);
$('#bot3_row1_min_profit').text(mesg['bot3']['1']['min_profit']);
$('#bot3_row1_order_id').text(mesg['bot3']['1']['order_id']);
$('#bot3_row1_position').text(mesg['bot3']['1']['position']);
$('#bot3_row1_postOnly').text(mesg['bot3']['1']['postOnly']);
$('#bot3_row1_price').text(mesg['bot3']['1']['price']);
$('#bot3_row1_symbol').text(mesg['bot3']['1']['symbol']);
$('#bot3_row1_uuid').text(mesg['bot3']['1']['uuid']);
$('#bot3_row1_status').text(mesg['bot3']['1']['status']);

$('#bot3_row2_date').text(mesg['bot3']['2']['timestamp']);
$('#bot3_row2_amount').text(mesg['bot3']['2']['amount']);
$('#bot3_row2_api_name').text(mesg['bot3']['2']['api_name']);
$('#bot3_row2_average').text(mesg['bot3']['2']['average']);
$('#bot3_row2_cancel_threshold').text(mesg['bot3']['2']['cancel_threshold']);
$('#bot3_row2_entry_price').text(mesg['bot3']['2']['entry_price']);
$('#bot3_row2_ex_id').text(mesg['bot3']['2']['ex_id']);
$('#bot3_row2_filled').text(mesg['bot3']['2']['filled']);
$('#bot3_row2_follow_gap').text(mesg['bot3']['2']['follow_gap']);
$('#bot3_row2_gap').text(mesg['bot3']['2']['gap']);
$('#bot3_row2_input_amount').text(mesg['bot3']['2']['input_amount']);
$('#bot3_row2_input_pair').text(mesg['bot3']['2']['input_pair']);
$('#bot3_row2_min_profit').text(mesg['bot3']['2']['min_profit']);
$('#bot3_row2_order_id').text(mesg['bot3']['2']['order_id']);
$('#bot3_row2_position').text(mesg['bot3']['2']['position']);
$('#bot3_row2_postOnly').text(mesg['bot3']['2']['postOnly']);
$('#bot3_row2_price').text(mesg['bot3']['2']['price']);
$('#bot3_row2_symbol').text(mesg['bot3']['2']['symbol']);
$('#bot3_row2_uuid').text(mesg['bot3']['2']['uuid']);
$('#bot3_row2_status').text(mesg['bot3']['2']['status']);


$('#bot3_row3_date').text(mesg['bot3']['3']['timestamp']);
$('#bot3_row3_amount').text(mesg['bot3']['3']['amount']);
$('#bot3_row3_api_name').text(mesg['bot3']['3']['api_name']);
$('#bot3_row3_average').text(mesg['bot3']['3']['average']);
$('#bot3_row3_cancel_threshold').text(mesg['bot3']['3']['cancel_threshold']);
$('#bot3_row3_entry_price').text(mesg['bot3']['3']['entry_price']);
$('#bot3_row3_ex_id').text(mesg['bot3']['3']['ex_id']);
$('#bot3_row3_filled').text(mesg['bot3']['3']['filled']);
$('#bot3_row3_follow_gap').text(mesg['bot3']['3']['follow_gap']);
$('#bot3_row3_gap').text(mesg['bot3']['3']['gap']);
$('#bot3_row3_input_amount').text(mesg['bot3']['3']['input_amount']);
$('#bot3_row3_input_pair').text(mesg['bot3']['3']['input_pair']);
$('#bot3_row3_min_profit').text(mesg['bot3']['3']['min_profit']);
$('#bot3_row3_order_id').text(mesg['bot3']['3']['order_id']);
$('#bot3_row3_position').text(mesg['bot3']['3']['position']);
$('#bot3_row3_postOnly').text(mesg['bot3']['3']['postOnly']);
$('#bot3_row3_price').text(mesg['bot3']['3']['price']);
$('#bot3_row3_symbol').text(mesg['bot3']['3']['symbol']);
$('#bot3_row3_uuid').text(mesg['bot3']['3']['uuid']);
$('#bot3_row3_status').text(mesg['bot3']['3']['status']);



// for bot3
// for bot4

$('#bot4_row1_date').text(mesg['bot4']['1']['timestamp']);
$('#bot4_row1_amount').text(mesg['bot4']['1']['amount']);
$('#bot4_row1_api_name1').text(mesg['bot4']['1']['api_name1']);
$('#bot4_row1_api_name2').text(mesg['bot4']['1']['api_name2']);
$('#bot4_row1_average').text(mesg['bot4']['1']['average']);
$('#bot4_row1_ex_id1').text(mesg['bot4']['1']['ex_id1']);
$('#bot4_row1_ex_id2').text(mesg['bot4']['1']['ex_id2']);
$('#bot4_row1_filled').text(mesg['bot4']['1']['filled']);
$('#bot4_row1_follow_gap').text(mesg['bot4']['1']['follow_gap']);
$('#bot4_row1_follow_market').text(mesg['bot4']['1']['follow_market']);
$('#bot4_row1_gap').text(mesg['bot4']['1']['gap']);
$('#bot4_row1_input_price').text(mesg['bot4']['1']['input_price']);
$('#bot4_row1_is_parallel').text(mesg['bot4']['1']['is_parallel']);
$('#bot4_row1_min_profit').text(mesg['bot4']['1']['min_profit']);
$('#bot4_row1_order_id').text(mesg['bot4']['1']['order_id']);
$('#bot4_row1_position').text(mesg['bot4']['1']['position']);
$('#bot4_row1_postOnly').text(mesg['bot4']['1']['postOnly']);
$('#bot4_row1_price').text(mesg['bot4']['1']['price']);
$('#bot4_row1_profit').text(mesg['bot4']['1']['profit']);
$('#bot4_row1_symbol').text(mesg['bot4']['1']['symbol']);
$('#bot4_row1_trailing_margin').text(mesg['bot4']['1']['trailing_margin']);
$('#bot4_row1_uuid').text(mesg['bot4']['1']['uuid']);
$('#bot4_row1_status').text(mesg['bot4']['1']['status']);

$('#bot4_row2_date').text(mesg['bot4']['2']['timestamp']);
$('#bot4_row2_amount').text(mesg['bot4']['2']['amount']);
$('#bot4_row2_api_name1').text(mesg['bot4']['2']['api_name1']);
$('#bot4_row2_api_name2').text(mesg['bot4']['2']['api_name2']);
$('#bot4_row2_average').text(mesg['bot4']['2']['average']);
$('#bot4_row2_ex_id1').text(mesg['bot4']['2']['ex_id1']);
$('#bot4_row2_ex_id2').text(mesg['bot4']['2']['ex_id2']);
$('#bot4_row2_filled').text(mesg['bot4']['2']['filled']);
$('#bot4_row2_follow_gap').text(mesg['bot4']['2']['follow_gap']);
$('#bot4_row2_follow_market').text(mesg['bot4']['2']['follow_market']);
$('#bot4_row2_gap').text(mesg['bot4']['2']['gap']);
$('#bot4_row2_input_price').text(mesg['bot4']['2']['input_price']);
$('#bot4_row2_is_parallel').text(mesg['bot4']['2']['is_parallel']);
$('#bot4_row2_min_profit').text(mesg['bot4']['2']['min_profit']);
$('#bot4_row2_order_id').text(mesg['bot4']['2']['order_id']);
$('#bot4_row2_position').text(mesg['bot4']['2']['position']);
$('#bot4_row2_postOnly').text(mesg['bot4']['2']['postOnly']);
$('#bot4_row2_price').text(mesg['bot4']['2']['price']);
$('#bot4_row2_profit').text(mesg['bot4']['2']['profit']);
$('#bot4_row2_symbol').text(mesg['bot4']['2']['symbol']);
$('#bot4_row2_trailing_margin').text(mesg['bot4']['2']['trailing_margin']);
$('#bot4_row2_uuid').text(mesg['bot4']['2']['uuid']);
$('#bot4_row2_status').text(mesg['bot4']['2']['status']);

$('#bot4_row3_date').text(mesg['bot4']['3']['timestamp']);
$('#bot4_row3_amount').text(mesg['bot4']['3']['amount']);
$('#bot4_row3_api_name1').text(mesg['bot4']['3']['api_name1']);
$('#bot4_row3_api_name2').text(mesg['bot4']['3']['api_name2']);
$('#bot4_row3_average').text(mesg['bot4']['3']['average']);
$('#bot4_row3_ex_id1').text(mesg['bot4']['3']['ex_id1']);
$('#bot4_row3_ex_id2').text(mesg['bot4']['3']['ex_id2']);
$('#bot4_row3_filled').text(mesg['bot4']['3']['filled']);
$('#bot4_row3_follow_gap').text(mesg['bot4']['3']['follow_gap']);
$('#bot4_row3_follow_market').text(mesg['bot4']['3']['follow_market']);
$('#bot4_row3_gap').text(mesg['bot4']['3']['gap']);
$('#bot4_row3_input_price').text(mesg['bot4']['3']['input_price']);
$('#bot4_row3_is_parallel').text(mesg['bot4']['3']['is_parallel']);
$('#bot4_row3_min_profit').text(mesg['bot4']['3']['min_profit']);
$('#bot4_row3_order_id').text(mesg['bot4']['3']['order_id']);
$('#bot4_row3_position').text(mesg['bot4']['3']['position']);
$('#bot4_row3_postOnly').text(mesg['bot4']['3']['postOnly']);
$('#bot4_row3_price').text(mesg['bot4']['3']['price']);
$('#bot4_row3_profit').text(mesg['bot4']['3']['profit']);
$('#bot4_row3_symbol').text(mesg['bot4']['3']['symbol']);
$('#bot4_row3_trailing_margin').text(mesg['bot4']['3']['trailing_margin']);
$('#bot4_row3_uuid').text(mesg['bot4']['3']['uuid']);
$('#bot4_row3_status').text(mesg['bot4']['3']['status']);



// for bot4
// for bot5

$('#bot5_row1_date').text(mesg['bot5']['1']['timestamp']);
$('#bot5_row1_api_name').text(mesg['bot5']['1']['api_name']);
$('#bot5_row1_average').text(mesg['bot5']['1']['average']);
$('#bot5_row1_bot_amount').text(mesg['bot5']['1']['bot_amount']);
$('#bot5_row1_bot_price').text(mesg['bot5']['1']['bot_price']);
$('#bot5_row1_ex_id').text(mesg['bot5']['1']['ex_id']);
$('#bot5_row1_filled').text(mesg['bot5']['1']['filled']);
$('#bot5_row1_input_amount').text(mesg['bot5']['1']['input_amount']);
$('#bot5_row1_input_base_amount').text(mesg['bot5']['1']['input_base_amount']);
$('#bot5_row1_input_fees').text(mesg['bot5']['1']['input_fees']);
$('#bot5_row1_input_price').text(mesg['bot5']['1']['input_price']);
$('#bot5_row1_input_profit').text(mesg['bot5']['1']['input_profit']);
$('#bot5_row1_input_input_trailing_margin').text(mesg['bot5']['1']['input_trailing_margin']);
$('#bot5_row1_input_order_id').text(mesg['bot5']['1']['order_id']);
$('#bot5_row1_input_order_trl_margin').text(mesg['bot5']['1']['order_trl_margin']);
$('#bot5_row1_position').text(mesg['bot5']['1']['position']);
$('#bot5_row1_symbol').text(mesg['bot5']['1']['symbol']);
$('#bot5_row1_trade_id').text(mesg['bot5']['1']['trade_id']);
$('#bot5_row1_uuid').text(mesg['bot5']['1']['uuid']);
$('#bot5_row1_status').text(mesg['bot5']['1']['status']);

$('#bot5_row2_date').text(mesg['bot5']['2']['timestamp']);
$('#bot5_row2_api_name').text(mesg['bot5']['2']['api_name']);
$('#bot5_row2_average').text(mesg['bot5']['2']['average']);
$('#bot5_row2_bot_amount').text(mesg['bot5']['2']['bot_amount']);
$('#bot5_row2_bot_price').text(mesg['bot5']['2']['bot_price']);
$('#bot5_row2_ex_id').text(mesg['bot5']['2']['ex_id']);
$('#bot5_row2_filled').text(mesg['bot5']['2']['filled']);
$('#bot5_row2_input_amount').text(mesg['bot5']['2']['input_amount']);
$('#bot5_row2_input_base_amount').text(mesg['bot5']['2']['input_base_amount']);
$('#bot5_row2_input_fees').text(mesg['bot5']['2']['input_fees']);
$('#bot5_row2_input_price').text(mesg['bot5']['2']['input_price']);
$('#bot5_row2_input_profit').text(mesg['bot5']['2']['input_profit']);
$('#bot5_row2_input_input_trailing_margin').text(mesg['bot5']['2']['input_trailing_margin']);
$('#bot5_row2_input_order_id').text(mesg['bot5']['2']['order_id']);
$('#bot5_row2_input_order_trl_margin').text(mesg['bot5']['2']['order_trl_margin']);
$('#bot5_row2_position').text(mesg['bot5']['2']['position']);
$('#bot5_row2_symbol').text(mesg['bot5']['2']['symbol']);
$('#bot5_row2_trade_id').text(mesg['bot5']['2']['trade_id']);
$('#bot5_row2_uuid').text(mesg['bot5']['2']['uuid']);
$('#bot5_row2_status').text(mesg['bot5']['2']['status']);

$('#bot5_row3_date').text(mesg['bot5']['3']['timestamp']);
$('#bot5_row3_api_name').text(mesg['bot5']['3']['api_name']);
$('#bot5_row3_average').text(mesg['bot5']['3']['average']);
$('#bot5_row3_bot_amount').text(mesg['bot5']['3']['bot_amount']);
$('#bot5_row3_bot_price').text(mesg['bot5']['3']['bot_price']);
$('#bot5_row3_ex_id').text(mesg['bot5']['3']['ex_id']);
$('#bot5_row3_filled').text(mesg['bot5']['3']['filled']);
$('#bot5_row3_input_amount').text(mesg['bot5']['3']['input_amount']);
$('#bot5_row3_input_base_amount').text(mesg['bot5']['3']['input_base_amount']);
$('#bot5_row3_input_fees').text(mesg['bot5']['3']['input_fees']);
$('#bot5_row3_input_price').text(mesg['bot5']['3']['input_price']);
$('#bot5_row3_input_profit').text(mesg['bot5']['3']['input_profit']);
$('#bot5_row3_input_input_trailing_margin').text(mesg['bot5']['3']['input_trailing_margin']);
$('#bot5_row3_input_order_id').text(mesg['bot5']['3']['order_id']);
$('#bot5_row3_input_order_trl_margin').text(mesg['bot5']['3']['order_trl_margin']);
$('#bot5_row3_position').text(mesg['bot5']['3']['position']);
$('#bot5_row3_symbol').text(mesg['bot5']['3']['symbol']);
$('#bot5_row3_trade_id').text(mesg['bot5']['3']['trade_id']);
$('#bot5_row3_uuid').text(mesg['bot5']['3']['uuid']);
$('#bot5_row3_status').text(mesg['bot5']['3']['status']);




// for bot6
$('#bot6_row1_order_time').text(mesg['bot6']['1']['order_time']);
$('#bot6_row1_api_name').text(mesg['bot6']['1']['api_name']);
$('#bot6_row1_average').text(mesg['bot6']['1']['average']);
$('#bot6_row1_ex_id').text(mesg['bot6']['1']['ex_id']);
$('#bot6_row1_filled').text(mesg['bot6']['1']['filled']);
$('#bot6_row1_follow_gap').text(mesg['bot6']['1']['follow_gap']);
$('#bot6_row1_follow_market').text(mesg['bot6']['1']['follow_market']);
$('#bot6_row1_gap').text(mesg['bot6']['1']['gap']);
$('#bot6_row1_input_amount').text(mesg['bot6']['1']['input_amount']);
$('#bot6_row1_min_profit').text(mesg['bot6']['1']['min_profit']);
$('#bot6_row1_order_amount').text(mesg['bot6']['1']['order_amount']);
$('#bot6_row1_order_id').text(mesg['bot6']['1']['order_id']);
$('#bot6_row1_ori_amount').text(mesg['bot6']['1']['ori_amount']);
$('#bot6_row1_ori_price').text(mesg['bot6']['1']['ori_price']);
$('#bot6_row1_pair2').text(mesg['bot6']['1']['pair2']);
$('#bot6_row1_pair_first').text(mesg['bot6']['1']['pair_first']);
$('#bot6_row1_pair_symbol').text(mesg['bot6']['1']['pair_symbol']);
$('#bot6_row1_position').text(mesg['bot6']['1']['position']);
$('#bot6_row1_postOnly').text(mesg['bot6']['1']['postOnly']);
$('#bot6_row1_price').text(mesg['bot6']['1']['price']);
$('#bot6_row1_side').text(mesg['bot6']['1']['side']);
$('#bot6_row1_symbol').text(mesg['bot6']['1']['symbol']);
$('#bot6_row1_trailing_margin').text(mesg['bot6']['1']['trailing_margin']);
$('#bot6_row1_uuid').text(mesg['bot6']['1']['uuid']);
$('#bot6_row1_status').text(mesg['bot6']['1']['status']);

$('#bot6_row2_order_time').text(mesg['bot6']['2']['order_time']);
$('#bot6_row2_api_name').text(mesg['bot6']['2']['api_name']);
$('#bot6_row2_average').text(mesg['bot6']['2']['average']);
$('#bot6_row2_ex_id').text(mesg['bot6']['2']['ex_id']);
$('#bot6_row2_filled').text(mesg['bot6']['2']['filled']);
$('#bot6_row2_follow_gap').text(mesg['bot6']['2']['follow_gap']);
$('#bot6_row2_follow_market').text(mesg['bot6']['2']['follow_market']);
$('#bot6_row2_gap').text(mesg['bot6']['2']['gap']);
$('#bot6_row2_input_amount').text(mesg['bot6']['2']['input_amount']);
$('#bot6_row2_min_profit').text(mesg['bot6']['2']['min_profit']);
$('#bot6_row2_order_amount').text(mesg['bot6']['2']['order_amount']);
$('#bot6_row2_order_id').text(mesg['bot6']['2']['order_id']);
$('#bot6_row2_ori_amount').text(mesg['bot6']['2']['ori_amount']);
$('#bot6_row2_ori_price').text(mesg['bot6']['2']['ori_price']);
$('#bot6_row2_pair2').text(mesg['bot6']['2']['pair2']);
$('#bot6_row2_pair_first').text(mesg['bot6']['2']['pair_first']);
$('#bot6_row2_pair_symbol').text(mesg['bot6']['2']['pair_symbol']);
$('#bot6_row2_position').text(mesg['bot6']['2']['position']);
$('#bot6_row2_postOnly').text(mesg['bot6']['2']['postOnly']);
$('#bot6_row2_price').text(mesg['bot6']['2']['price']);
$('#bot6_row2_side').text(mesg['bot6']['2']['side']);
$('#bot6_row2_symbol').text(mesg['bot6']['2']['symbol']);
$('#bot6_row2_trailing_margin').text(mesg['bot6']['2']['trailing_margin']);
$('#bot6_row2_uuid').text(mesg['bot6']['2']['uuid']);
$('#bot6_row2_status').text(mesg['bot6']['2']['status']);

$('#bot6_row3_order_time').text(mesg['bot6']['3']['order_time']);
$('#bot6_row3_api_name').text(mesg['bot6']['3']['api_name']);
$('#bot6_row3_average').text(mesg['bot6']['3']['average']);
$('#bot6_row3_ex_id').text(mesg['bot6']['3']['ex_id']);
$('#bot6_row3_filled').text(mesg['bot6']['3']['filled']);
$('#bot6_row3_follow_gap').text(mesg['bot6']['3']['follow_gap']);
$('#bot6_row3_follow_market').text(mesg['bot6']['3']['follow_market']);
$('#bot6_row3_gap').text(mesg['bot6']['3']['gap']);
$('#bot6_row3_input_amount').text(mesg['bot6']['3']['input_amount']);
$('#bot6_row3_min_profit').text(mesg['bot6']['3']['min_profit']);
$('#bot6_row3_order_amount').text(mesg['bot6']['3']['order_amount']);
$('#bot6_row3_order_id').text(mesg['bot6']['3']['order_id']);
$('#bot6_row3_ori_amount').text(mesg['bot6']['3']['ori_amount']);
$('#bot6_row3_ori_price').text(mesg['bot6']['3']['ori_price']);
$('#bot6_row3_pair2').text(mesg['bot6']['3']['pair2']);
$('#bot6_row3_pair_first').text(mesg['bot6']['3']['pair_first']);
$('#bot6_row3_pair_symbol').text(mesg['bot6']['3']['pair_symbol']);
$('#bot6_row3_position').text(mesg['bot6']['3']['position']);
$('#bot6_row3_postOnly').text(mesg['bot6']['3']['postOnly']);
$('#bot6_row3_price').text(mesg['bot6']['3']['price']);
$('#bot6_row3_side').text(mesg['bot6']['3']['side']);
$('#bot6_row3_symbol').text(mesg['bot6']['3']['symbol']);
$('#bot6_row3_trailing_margin').text(mesg['bot6']['3']['trailing_margin']);
$('#bot6_row3_uuid').text(mesg['bot6']['3']['uuid']);
$('#bot6_row3_status').text(mesg['bot6']['3']['status']);


// for bot6
// for bot7
$('#bot7_row1_ts_time').text(mesg['bot7']['1']['ts_time']);
$('#bot7_row1_amount').text(mesg['bot7']['1']['amount']);
$('#bot7_row1_api_name').text(mesg['bot7']['1']['api_name']);
$('#bot7_row1_average').text(mesg['bot7']['1']['average']);
$('#bot7_row1_balance_box_amount').text(mesg['bot7']['1']['balance_box_amount']);
$('#bot7_row1_balance_box_count').text(mesg['bot7']['1']['balance_box_count']);
$('#bot7_row1_ex_id').text(mesg['bot7']['1']['ex_id']);
$('#bot7_row1_filled').text(mesg['bot7']['1']['filled']);
$('#bot7_row1_follow_balance_box_amount').text(mesg['bot7']['1']['follow_balance_box_amount']);
$('#bot7_row1_follow_balance_box_count').text(mesg['bot7']['1']['follow_balance_box_count']);
$('#bot7_row1_follow_balance_box_follow_gap').text(mesg['bot7']['1']['follow_balance_box_follow_gap']);
$('#bot7_row1_follow_balance_box_gap').text(mesg['bot7']['1']['follow_balance_box_gap']);
$('#bot7_row1_follow_balance_box_postOnly').text(mesg['bot7']['1']['follow_balance_box_postOnly']);
$('#bot7_row1_follow_balance_box_profit').text(mesg['bot7']['1']['follow_balance_box_profit']);
$('#bot7_row1_follow_balance_box_step').text(mesg['bot7']['1']['follow_balance_box_step']);
$('#bot7_row1_follow_balance_box_time').text(mesg['bot7']['1']['follow_balance_box_time']);
$('#bot7_row1_follow_track_box_amount').text(mesg['bot7']['1']['follow_track_box_amount']);
$('#bot7_row1_follow_track_box_follow_gap').text(mesg['bot7']['1']['follow_track_box_follow_gap']);
$('#bot7_row1_follow_track_box_gap').text(mesg['bot7']['1']['follow_track_box_gap']);
$('#bot7_row1_follow_track_box_postOnly').text(mesg['bot7']['1']['follow_track_box_postOnly']);
$('#bot7_row1_inti_box_buy_price').text(mesg['bot7']['1']['inti_box_buy_price']);
$('#bot7_row1_inti_box_sell_price').text(mesg['bot7']['1']['inti_box_sell_price']);
$('#bot7_row1_order_id').text(mesg['bot7']['1']['order_id']);
$('#bot7_row1_pair').text(mesg['bot7']['1']['pair']);
$('#bot7_row1_position').text(mesg['bot7']['1']['position']);
$('#bot7_row1_price').text(mesg['bot7']['1']['price']);
$('#bot7_row1_symbol').text(mesg['bot7']['1']['symbol']);
$('#bot7_row1_uuid').text(mesg['bot7']['1']['uuid']);
$('#bot7_row1_status').text(mesg['bot7']['1']['status']);

$('#bot7_row2_ts_time').text(mesg['bot7']['2']['ts_time']);
$('#bot7_row2_amount').text(mesg['bot7']['2']['amount']);
$('#bot7_row2_api_name').text(mesg['bot7']['2']['api_name']);
$('#bot7_row2_average').text(mesg['bot7']['2']['average']);
$('#bot7_row2_balance_box_amount').text(mesg['bot7']['2']['balance_box_amount']);
$('#bot7_row2_balance_box_count').text(mesg['bot7']['2']['balance_box_count']);
$('#bot7_row2_ex_id').text(mesg['bot7']['2']['ex_id']);
$('#bot7_row2_filled').text(mesg['bot7']['2']['filled']);
$('#bot7_row2_follow_balance_box_amount').text(mesg['bot7']['2']['follow_balance_box_amount']);
$('#bot7_row2_follow_balance_box_count').text(mesg['bot7']['2']['follow_balance_box_count']);
$('#bot7_row2_follow_balance_box_follow_gap').text(mesg['bot7']['2']['follow_balance_box_follow_gap']);
$('#bot7_row2_follow_balance_box_gap').text(mesg['bot7']['2']['follow_balance_box_gap']);
$('#bot7_row2_follow_balance_box_postOnly').text(mesg['bot7']['2']['follow_balance_box_postOnly']);
$('#bot7_row2_follow_balance_box_profit').text(mesg['bot7']['2']['follow_balance_box_profit']);
$('#bot7_row2_follow_balance_box_step').text(mesg['bot7']['2']['follow_balance_box_step']);
$('#bot7_row2_follow_balance_box_time').text(mesg['bot7']['2']['follow_balance_box_time']);
$('#bot7_row2_follow_track_box_amount').text(mesg['bot7']['2']['follow_track_box_amount']);
$('#bot7_row2_follow_track_box_follow_gap').text(mesg['bot7']['2']['follow_track_box_follow_gap']);
$('#bot7_row2_follow_track_box_gap').text(mesg['bot7']['2']['follow_track_box_gap']);
$('#bot7_row2_follow_track_box_postOnly').text(mesg['bot7']['2']['follow_track_box_postOnly']);
$('#bot7_row2_inti_box_buy_price').text(mesg['bot7']['2']['inti_box_buy_price']);
$('#bot7_row2_inti_box_sell_price').text(mesg['bot7']['2']['inti_box_sell_price']);
$('#bot7_row2_order_id').text(mesg['bot7']['2']['order_id']);
$('#bot7_row2_pair').text(mesg['bot7']['2']['pair']);
$('#bot7_row2_position').text(mesg['bot7']['2']['position']);
$('#bot7_row2_price').text(mesg['bot7']['2']['price']);
$('#bot7_row2_symbol').text(mesg['bot7']['2']['symbol']);
$('#bot7_row2_uuid').text(mesg['bot7']['2']['uuid']);
$('#bot7_row2_status').text(mesg['bot7']['2']['status']);

$('#bot7_row3_ts_time').text(mesg['bot7']['3']['ts_time']);
$('#bot7_row3_amount').text(mesg['bot7']['3']['amount']);
$('#bot7_row3_api_name').text(mesg['bot7']['3']['api_name']);
$('#bot7_row3_average').text(mesg['bot7']['3']['average']);
$('#bot7_row3_balance_box_amount').text(mesg['bot7']['3']['balance_box_amount']);
$('#bot7_row3_balance_box_count').text(mesg['bot7']['3']['balance_box_count']);
$('#bot7_row3_ex_id').text(mesg['bot7']['3']['ex_id']);
$('#bot7_row3_filled').text(mesg['bot7']['3']['filled']);
$('#bot7_row3_follow_balance_box_amount').text(mesg['bot7']['3']['follow_balance_box_amount']);
$('#bot7_row3_follow_balance_box_count').text(mesg['bot7']['3']['follow_balance_box_count']);
$('#bot7_row3_follow_balance_box_follow_gap').text(mesg['bot7']['3']['follow_balance_box_follow_gap']);
$('#bot7_row3_follow_balance_box_gap').text(mesg['bot7']['3']['follow_balance_box_gap']);
$('#bot7_row3_follow_balance_box_postOnly').text(mesg['bot7']['3']['follow_balance_box_postOnly']);
$('#bot7_row3_follow_balance_box_profit').text(mesg['bot7']['3']['follow_balance_box_profit']);
$('#bot7_row3_follow_balance_box_step').text(mesg['bot7']['3']['follow_balance_box_step']);
$('#bot7_row3_follow_balance_box_time').text(mesg['bot7']['3']['follow_balance_box_time']);
$('#bot7_row3_follow_track_box_amount').text(mesg['bot7']['3']['follow_track_box_amount']);
$('#bot7_row3_follow_track_box_follow_gap').text(mesg['bot7']['3']['follow_track_box_follow_gap']);
$('#bot7_row3_follow_track_box_gap').text(mesg['bot7']['3']['follow_track_box_gap']);
$('#bot7_row3_follow_track_box_postOnly').text(mesg['bot7']['3']['follow_track_box_postOnly']);
$('#bot7_row3_inti_box_buy_price').text(mesg['bot7']['3']['inti_box_buy_price']);
$('#bot7_row3_inti_box_sell_price').text(mesg['bot7']['3']['inti_box_sell_price']);
$('#bot7_row3_order_id').text(mesg['bot7']['3']['order_id']);
$('#bot7_row3_pair').text(mesg['bot7']['3']['pair']);
$('#bot7_row3_position').text(mesg['bot7']['3']['position']);
$('#bot7_row3_price').text(mesg['bot7']['3']['price']);
$('#bot7_row3_symbol').text(mesg['bot7']['3']['symbol']);
$('#bot7_row3_uuid').text(mesg['bot7']['3']['uuid']);
$('#bot7_row3_status').text(mesg['bot7']['3']['status']);




// for bot7
// for bot8
$('#bot8_row1_update_date_time').text(mesg['bot8']['1']['update_date_time']);
$('#bot8_row1_action').text(mesg['bot8']['1']['action']);
$('#bot8_row1_amount').text(mesg['bot8']['1']['amount']);
$('#bot8_row1_api_name').text(mesg['bot8']['1']['api_name']);
$('#bot8_row1_average').text(mesg['bot8']['1']['average']);
$('#bot8_row1_ex_id').text(mesg['bot8']['1']['ex_id']);
$('#bot8_row1_ex_id').text(mesg['bot8']['1']['ex_id']);
$('#bot8_row1_filled').text(mesg['bot8']['1']['filled']);
$('#bot8_row1_order_id').text(mesg['bot8']['1']['order_id']);
$('#bot8_row1_ori_amount').text(mesg['bot8']['1']['ori_amount']);
$('#bot8_row1_ori_price').text(mesg['bot8']['1']['ori_price']);
$('#bot8_row1_pair').text(mesg['bot8']['1']['pair']);
$('#bot8_row1_position').text(mesg['bot8']['1']['position']);
$('#bot8_row1_postOnly').text(mesg['bot8']['1']['postOnly']);
$('#bot8_row1_price').text(mesg['bot8']['1']['price']);
$('#bot8_row1_profit').text(mesg['bot8']['1']['profit']);
$('#bot8_row1_symbol').text(mesg['bot8']['1']['symbol']);
$('#bot8_row1_timer').text(mesg['bot8']['1']['timer']);
$('#bot8_row1_trade_id').text(mesg['bot8']['1']['trade_id']);
$('#bot8_row1_trailing_margin').text(mesg['bot8']['1']['trailing_margin']);
$('#bot8_row1_uuid').text(mesg['bot8']['1']['uuid']);
$('#bot8_row1_status').text(mesg['bot8']['1']['status']);

$('#bot8_row2_update_date_time').text(mesg['bot8']['2']['update_date_time']);
$('#bot8_row2_action').text(mesg['bot8']['2']['action']);
$('#bot8_row2_amount').text(mesg['bot8']['2']['amount']);
$('#bot8_row2_api_name').text(mesg['bot8']['2']['api_name']);
$('#bot8_row2_average').text(mesg['bot8']['2']['average']);
$('#bot8_row2_ex_id').text(mesg['bot8']['2']['ex_id']);
$('#bot8_row2_ex_id').text(mesg['bot8']['2']['ex_id']);
$('#bot8_row2_filled').text(mesg['bot8']['2']['filled']);
$('#bot8_row2_order_id').text(mesg['bot8']['2']['order_id']);
$('#bot8_row2_ori_amount').text(mesg['bot8']['2']['ori_amount']);
$('#bot8_row2_ori_price').text(mesg['bot8']['2']['ori_price']);
$('#bot8_row2_pair').text(mesg['bot8']['2']['pair']);
$('#bot8_row2_position').text(mesg['bot8']['2']['position']);
$('#bot8_row2_postOnly').text(mesg['bot8']['2']['postOnly']);
$('#bot8_row2_price').text(mesg['bot8']['2']['price']);
$('#bot8_row2_profit').text(mesg['bot8']['2']['profit']);
$('#bot8_row2_symbol').text(mesg['bot8']['2']['symbol']);
$('#bot8_row2_timer').text(mesg['bot8']['2']['timer']);
$('#bot8_row2_trade_id').text(mesg['bot8']['2']['trade_id']);
$('#bot8_row2_trailing_margin').text(mesg['bot8']['2']['trailing_margin']);
$('#bot8_row2_uuid').text(mesg['bot8']['2']['uuid']);
$('#bot8_row2_status').text(mesg['bot8']['2']['status']);

$('#bot8_row3_update_date_time').text(mesg['bot8']['3']['update_date_time']);
$('#bot8_row3_action').text(mesg['bot8']['3']['action']);
$('#bot8_row3_amount').text(mesg['bot8']['3']['amount']);
$('#bot8_row3_api_name').text(mesg['bot8']['3']['api_name']);
$('#bot8_row3_average').text(mesg['bot8']['3']['average']);
$('#bot8_row3_ex_id').text(mesg['bot8']['3']['ex_id']);
$('#bot8_row3_ex_id').text(mesg['bot8']['3']['ex_id']);
$('#bot8_row3_filled').text(mesg['bot8']['3']['filled']);
$('#bot8_row3_order_id').text(mesg['bot8']['3']['order_id']);
$('#bot8_row3_ori_amount').text(mesg['bot8']['3']['ori_amount']);
$('#bot8_row3_ori_price').text(mesg['bot8']['3']['ori_price']);
$('#bot8_row3_pair').text(mesg['bot8']['3']['pair']);
$('#bot8_row3_position').text(mesg['bot8']['3']['position']);
$('#bot8_row3_postOnly').text(mesg['bot8']['3']['postOnly']);
$('#bot8_row3_price').text(mesg['bot8']['3']['price']);
$('#bot8_row3_profit').text(mesg['bot8']['3']['profit']);
$('#bot8_row3_symbol').text(mesg['bot8']['3']['symbol']);
$('#bot8_row3_timer').text(mesg['bot8']['3']['timer']);
$('#bot8_row3_trade_id').text(mesg['bot8']['3']['trade_id']);
$('#bot8_row3_trailing_margin').text(mesg['bot8']['3']['trailing_margin']);
$('#bot8_row3_uuid').text(mesg['bot8']['3']['uuid']);
$('#bot8_row3_status').text(mesg['bot8']['3']['status']);

//timer



// for bot8




}
    
