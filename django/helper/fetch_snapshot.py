import os, sys
dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = dir_path + '/../../libs'
sys.path.append(dir_path + '/../../repositories')
sys.path.append(dir_path + '/../services')
sys.path.append(lib_path)
from base_service import BaseService


class SnapshotRepository:
    pass

def fetch_allbot_with_snapshot(us, port, bot_alias):
    # bot under bot_alias
    snapshot = SnapshotRepository()
    snapshot_data = snapshot.fetch_all_bot(bot_alias)
    web_input = []
    for item in snapshot_data:
        if not item.get('bot_config'): # or not item.get('snapshot_data'):
            continue
        web_input.append({
            'bot_config': item['bot_config'],
            'own_name': item['bot_config']['own_name'],
            'time': item['bot_config']['time'],
            'uuid': item['bot_config']['uuid'],
            'pair': item['bot_config']['pair']
        })
    # bot not in user/port
    for item in web_input.copy():
        if us != item['own_name']:
            web_input.remove(item)
            continue
        elif item['bot_config'].get('port', False) and port != item['bot_config']['port']:
            web_input.remove(item)
            continue
    return web_input

def fetch_snap_shot_bot(us, port, bot_alias):
    # bot not ternimal
    snapshot = SnapshotRepository()
    snapshot_data = snapshot.fetch_data(bot_alias)
    web_input = []
    for item in snapshot_data:
        if not item or not item.get('bot_config'):
            continue
        web_input.append({
            'bot_config': item.get('bot_config'),
            'own_name': item['bot_config'].get('own_name'),
            'time': item['bot_config'].get('time'),
            'uuid': item['bot_config'].get('uuid'),
            'pair': item['bot_config'].get('pair', 'N/A'),
            'api_name': item['bot_config'].get('api_name', 'N/A'),
            'ex_id': item['bot_config'].get('pair', 'N/A'),
        })
    base_srv = BaseService()
    # bot not running
    for item in web_input.copy():
        data = base_srv.fetch_detail(bot_alias, str(item['uuid']))
        if data:
            # delete
            web_input.remove(item)
            continue
        if us != item['own_name']:
            web_input.remove(item)
            continue
        elif item['bot_config'].get('port', False) and port != item['bot_config']['port']:
            web_input.remove(item)
            continue
    return web_input


def fetch_snapshot_bot_detail(uuid: str, us, port, bot_alias, all_bot=False):
    if all_bot:
        snapshot_bots = fetch_allbot_with_snapshot(us, port, bot_alias)
    else:
        snapshot_bots = fetch_snap_shot_bot(us, port, bot_alias)

    for item in snapshot_bots:
        if uuid == item['uuid']:
            return item['bot_config']
    return None


def fetch_mode_display(modes, value):
    for item in modes:
        if item['value'] == value:
            return [item]
    return None