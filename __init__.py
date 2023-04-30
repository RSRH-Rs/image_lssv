import asyncio
from functools import cmp_to_key
from nonebot import CommandSession, on_command
from functools import cmp_to_key
from nonebot import CommandSession, on_command
from nonebot import permission as perm
from nonebot.argparse import ArgumentParser
import hoshino
from hoshino import Service, priv, util
from hoshino.typing import HoshinoBot,CQEvent
from .config_image import get_image_services
from .utils import get_random_pic,get_path,get_json_data,write_json_data
from nonebot import MessageSegment
from PIL import Image,UnidentifiedImageError
import os

images_path = get_path("data","imgs")
data_path = get_path("data")

PRIV_TIP = f'群主={priv.OWNER} 群管={priv.ADMIN} 群员={priv.NORMAL} bot维护组={priv.SUPERUSER}'
@on_command('lssv', aliases=('服务列表', '功能列表'), permission=perm.GROUP_ADMIN, only_to_me=False, shell_like=True)
async def send_image_lssv(session:CommandSession):
    parser = ArgumentParser(session=session)
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('-H', '--hidden', action='store_true')
    parser.add_argument('-g', '--group', type=int, default=0)
    args = parser.parse_args(session.argv)
    group_id = str(session.ctx.group_id)

    verbose_all = args.all
    only_hidden = args.hidden
    if session.ctx['user_id'] in session.bot.config.SUPERUSERS:
        gid = args.group or session.ctx.get('group_id')
        if not gid:
            session.finish('Usage: -g|--group <group_id> [-a|--all]')
    else:
        gid = session.ctx['group_id']

    svs = Service.get_loaded_services().values()
    svs = map(lambda sv: (sv, sv.check_enabled(gid)), svs)
    key = cmp_to_key(lambda x, y: (y[1] - x[1]) or (-1 if x[0].name < y[0].name else 1 if x[0].name > y[0].name else 0))
    svs = sorted(svs, key=key)

    svs_list = {}

    for sv, on in svs:
        if verbose_all or (sv.visible ^ only_hidden):
            status = True if on else False
            svs_list[str(sv.name)] = status

    base_w = 850
    based_h = 850 + 155 * len(svs_list)

    previous_services_data = get_json_data(file_path=data_path+"/previous_services_data.json")
    previous_services_data = previous_services_data[group_id] if (previous_services_data is not None and group_id in previous_services_data.keys()) else {}

    if not os.path.exists(get_path("data","imgs","bg.png")):
        get_random_pic("bg.png")

    try:
        bg_image = Image.open(images_path+"/bg.png")
    except UnidentifiedImageError:
        bg_image = get_random_pic(file_name="bg.png")
        hoshino.logger.error("[WARNING] `bg.png`图片丢失，正在获取随机背景图片。")

    if previous_services_data == svs_list and os.path.exists(get_path("data","imgs","config.png")):
        await session.finish(MessageSegment.image("file:///" + images_path + "/config.png"))

    write_json_data(file_path=data_path+"/previous_services_data.json",content={group_id:svs_list})

    sv_image = await get_image_services(image=bg_image,group_id=group_id,sv_list=svs_list,width=base_w,height=based_h)
    sv_image.save(images_path+"/config.png")
    await session.send(MessageSegment.image("file:///"+images_path+"/config.png"))


@on_command('enable', aliases=('启用', '开启', '打开'), permission=perm.GROUP, only_to_me=False)
async def enable_service(session: CommandSession):
    await switch_service(session, turn_on=True)

@on_command('disable', aliases=('禁用', '关闭'), permission=perm.GROUP, only_to_me=False)
async def disable_service(session: CommandSession):
    await switch_service(session, turn_on=False)

async def switch_service(session: CommandSession, turn_on: bool):
    action_tip = '启用' if turn_on else '禁用'
    if session.ctx['message_type'] == 'group':
        names = session.current_arg_text.split()
        if not names:
            session.finish(f"空格后接要{action_tip}的服务名", at_sender=True)
        group_id = session.ctx['group_id']
        svs = Service.get_loaded_services()
        succ, notfound = [], []
        for name in names:
            if name in svs:
                sv = svs[name]
                u_priv = priv.get_user_priv(session.ctx)
                if u_priv >= sv.manage_priv:
                    sv.set_enable(group_id) if turn_on else sv.set_disable(group_id)
                    succ.append(name)
                else:
                    try:
                        await session.send(f'权限不足！{action_tip}{name}需要：{sv.manage_priv}，您的：{u_priv}\n{PRIV_TIP}', at_sender=True)
                    except:
                        pass
            else:
                notfound.append(util.filt_message(name))
        msg = []
        if succ:
            msg.append(f'已{action_tip}服务：' + ', '.join(succ))
        if notfound:
            msg.append('未找到服务：' + ', '.join(notfound))
        if msg:
            session.finish('\n'.join(msg), at_sender=True)

    else:
        if session.ctx['user_id'] not in session.bot.config.SUPERUSERS:
            return
        args = session.current_arg_text.split()
        if len(args) < 2:
            session.finish('Usage: <service_name> <group_id1> [<group_id2>, ...]')
        name, *group_ids = args
        svs = Service.get_loaded_services()
        if name not in svs:
            session.finish(f'未找到服务：{name}')
        sv = svs[name]
        succ = []
        for gid in group_ids:
            try:
                gid = int(gid)
                sv.set_enable(gid) if turn_on else sv.set_disable(gid)
                succ.append(gid)
            except:
                try:
                    await session.send(f'非法群号：{gid}')
                except:
                    pass
        session.finish(f'服务{name}已于{len(succ)}个群内{action_tip}：{succ}')





