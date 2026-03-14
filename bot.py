import asyncio, sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

tok = "8601229427:AAGuSTOHuPo0dSIZnJ0efdoAh8acNVqySBc"
Own = 7306010609

b = Bot(token=tok)
storage = MemoryStorage()
d = Dispatcher(storage=storage)

def conn():
    return sqlite3.connect("BOT.db")

def podnyal():
    c = conn(); k = c.cursor()
    k.execute("CREATE TABLE IF NOT EXISTS zapis (id INTEGER PRIMARY KEY AUTOINCREMENT, tipok INTEGER, nik TEXT, titul TEXT, palka TEXT, chto_bylo TEXT, hochet TEXT, stat TEXT DEFAULT 'ojid')")
    k.execute("CREATE TABLE IF NOT EXISTS svoi (uid INTEGER PRIMARY KEY)")
    k.execute("INSERT OR IGNORE INTO svoi VALUES (?)", (Own,))
    c.commit(); c.close()

def svoy(uid):
    c = conn(); k = c.cursor()
    k.execute("SELECT uid FROM svoi WHERE uid=?", (uid,))
    r = k.fetchone(); c.close(); return r is not None

class FF(StatesGroup):
    q1 = State(); q2 = State(); q3 = State(); q4 = State(); fin = State()

def mm():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Оспорить", callback_data="f0")],[InlineKeyboardButton(text="Заявления", callback_data="ml")]])

def xod():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Отмена", callback_data="die")]])

def end_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Отправить", callback_data="snd"), InlineKeyboardButton(text="Назад", callback_data="bk")]])

@d.message(Command("start"))
async def _s(m: Message, state: FSMContext):
    await state.clear(); await m.answer("Оспаривание решений:", reply_markup=mm())

@d.message(Command("admin"))
async def _a(m: Message):
    if not svoy(m.from_user.id):
        await m.answer("Нет прав."); return
    await m.answer("Админ-панель:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Заявления", callback_data="amenu")]]))

@d.callback_query(F.data == "die")
async def _die(c: CallbackQuery, st: FSMContext):
    await st.clear(); await c.message.edit_text("Оспаривание решений:", reply_markup=mm())

@d.callback_query(F.data == "gmain")
async def _gm(c: CallbackQuery, st: FSMContext):
    await st.clear(); await c.message.edit_text("Оспаривание решений:", reply_markup=mm())

@d.callback_query(F.data == "f0")
async def _f0(c: CallbackQuery, st: FSMContext):
    await st.set_state(FF.q1); await c.message.edit_text("Введи название заявления:", reply_markup=xod())

@d.message(FF.q1)
async def _q1(m: Message, st: FSMContext):
    await st.update_data(t=m.text); await st.set_state(FF.q2)
    await m.answer("Какое наказание тебе выдали и за что:", reply_markup=xod())

@d.message(FF.q2)
async def _q2(m: Message, st: FSMContext):
    await st.update_data(p=m.text); await st.set_state(FF.q3)
    await m.answer("Опиши ситуацию подробно:", reply_markup=xod())

@d.message(FF.q3)
async def _q3(m: Message, st: FSMContext):
    await st.update_data(s=m.text); await st.set_state(FF.q4)
    await m.answer("Что ты считаешь несправедливым и какое решение ты хочешь:", reply_markup=xod())

@d.message(FF.q4)
async def _q4(m: Message, st: FSMContext):
    await st.update_data(w=m.text); dd = await st.get_data()
    await st.set_state(FF.fin)
    await m.answer(f"📄 Твоя заявка:\n\n<b>Название:</b> {dd['t']}\n<b>Наказание:</b> {dd['p']}\n<b>Ситуация:</b> {dd['s']}\n<b>Что хочу:</b> {dd['w']}", reply_markup=end_kb(), parse_mode="HTML")

@d.callback_query(F.data == "bk", FF.fin)
async def _bk(c: CallbackQuery, st: FSMContext):
    await st.set_state(FF.q4); await c.message.edit_text("Что ты считаешь несправедливым и какое решение ты хочешь:", reply_markup=xod())

@d.callback_query(F.data == "snd", FF.fin)
async def _snd(c: CallbackQuery, st: FSMContext):
    dd = await st.get_data()
    nik = c.from_user.username or c.from_user.first_name
    uid = c.from_user.id
    con = conn(); k = con.cursor()
    k.execute("INSERT INTO zapis (tipok, nik, titul, palka, chto_bylo, hochet) VALUES (?,?,?,?,?,?)", (uid, nik, dd['t'], dd['p'], dd['s'], dd['w']))
    con.commit(); con.close(); await st.clear()
    await c.message.edit_text("Заявка отправлена", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="gmain")]]))

@d.callback_query(F.data == "ml")
async def _ml(c: CallbackQuery):
    uid = c.from_user.id; con = conn(); k = con.cursor()
    k.execute("SELECT id, titul FROM zapis WHERE tipok=?", (uid,)); rows = k.fetchall(); con.close()
    if not rows:
        await c.message.edit_text("У тебя нет заявлений.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="gmain")]])); return
    btns = [[InlineKeyboardButton(text=f"📋 {z}", callback_data=f"vm_{n}")] for n, z in rows]
    btns.append([InlineKeyboardButton(text="Назад", callback_data="gmain")])
    await c.message.edit_text("Твои заявления:", reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))

@d.callback_query(F.data.startswith("vm_"))
async def _vm(c: CallbackQuery):
    n = int(c.data.split("_")[1]); con = conn(); k = con.cursor()
    k.execute("SELECT titul, palka, chto_bylo, hochet, stat FROM zapis WHERE id=?", (n,)); r = k.fetchone(); con.close()
    if not r: await c.answer("Не найдено"); return
    tt, pp, ss, ww, st = r
    smap = {"ojid": "На рассмотрении", "prinyat": "Оспорено", "otboi": "Отказано"}
    await c.message.edit_text(f"📄 Заявление\n\n<b>Название:</b> {tt}\n<b>Наказание:</b> {pp}\n<b>Ситуация:</b> {ss}\n<b>Что хочу:</b> {ww}\n\n<b>Статус:</b> {smap.get(st, st)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="ml")]]), parse_mode="HTML")

@d.callback_query(F.data == "amenu")
async def _amenu(c: CallbackQuery):
    if not svoy(c.from_user.id): await c.answer("Нет прав."); return
    await c.message.edit_text("Заявления:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ожидающие", callback_data="al_ojid_0")],
        [InlineKeyboardButton(text="Оспорены", callback_data="al_prinyat_0")],
        [InlineKeyboardButton(text="Отказано", callback_data="al_otboi_0")],
        [InlineKeyboardButton(text="Назад", callback_data="abk")]
    ]))

@d.callback_query(F.data == "abk")
async def _abk(c: CallbackQuery):
    await c.message.edit_text("Админ-панель:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Заявления", callback_data="amenu")]]))

@d.callback_query(F.data.startswith("al_"))
async def _al(c: CallbackQuery):
    if not svoy(c.from_user.id): await c.answer("Нет прав."); return
    _, tip, pg = c.data.split("_"); pg = int(pg)
    con = conn(); k = con.cursor()
    k.execute("SELECT id, titul, nik FROM zapis WHERE stat=?", (tip,)); rows = k.fetchall(); con.close()
    tot = len(rows); chunk = rows[pg*5:(pg+1)*5]
    if not chunk:
        await c.message.edit_text("Пусто.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="amenu")]])); return
    btns = [[InlineKeyboardButton(text=f"{nk} — {zt}", callback_data=f"av_{idd}_{tip}_{pg}")] for idd, zt, nk in chunk]
    nav = []
    if pg > 0: nav.append(InlineKeyboardButton(text="◀️", callback_data=f"al_{tip}_{pg-1}"))
    if (pg+1)*5 < tot: nav.append(InlineKeyboardButton(text="▶️", callback_data=f"al_{tip}_{pg+1}"))
    if nav: btns.append(nav)
    btns.append([InlineKeyboardButton(text="Назад", callback_data="amenu")])
    nm = {"ojid": "Ожидающие", "prinyat": "Оспорены", "otboi": "Отказано"}
    await c.message.edit_text(f"{nm.get(tip, tip)}:", reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))

@d.callback_query(F.data.startswith("av_"))
async def _av(c: CallbackQuery):
    if not svoy(c.from_user.id): await c.answer("Нет прав."); return
    spl = c.data.split("_"); idd = int(spl[1]); tip = spl[2]; pg = int(spl[3])
    con = conn(); k = con.cursor()
    k.execute("SELECT nik, tipok, titul, palka, chto_bylo, hochet FROM zapis WHERE id=?", (idd,)); r = k.fetchone(); con.close()
    if not r: await c.answer("Не найдено"); return
    nk, uid, tt, pp, ss, ww = r
    btns = []
    if tip == "ojid":
        btns.append([InlineKeyboardButton(text="Оспорить", callback_data=f"yes_{idd}_{tip}_{pg}"), InlineKeyboardButton(text="Отказать", callback_data=f"no_{idd}_{tip}_{pg}")])
    btns.append([InlineKeyboardButton(text="Назад", callback_data=f"al_{tip}_{pg}")])
    await c.message.edit_text(f"👤 <b>Ник:</b> {nk}\n<b>Юзер:</b> @{nk}\n<b>Айди:</b> <code>{uid}</code>\n\n📄 <b>Заявление</b>\n\n<b>Название:</b> {tt}\n<b>Наказание:</b> {pp}\n<b>Ситуация:</b> {ss}\n<b>Что хочет:</b> {ww}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=btns), parse_mode="HTML")

@d.callback_query(F.data.startswith("yes_"))
async def _yes(c: CallbackQuery):
    if not svoy(c.from_user.id): await c.answer("Нет прав."); return
    spl = c.data.split("_"); idd = int(spl[1]); tip = spl[2]; pg = int(spl[3])
    con = conn(); k = con.cursor()
    k.execute("UPDATE zapis SET stat='prinyat' WHERE id=?", (idd,))
    k.execute("SELECT tipok FROM zapis WHERE id=?", (idd,)); own = k.fetchone()
    con.commit(); con.close()
    if own:
        try: await b.send_message(own[0], "Твоя заявка оспорена")
        except: pass
    await c.message.edit_text("Ладно.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data=f"al_ojid_{pg}")]]))

@d.callback_query(F.data.startswith("no_"))
async def _no(c: CallbackQuery):
    if not svoy(c.from_user.id): await c.answer("Нет прав."); return
    spl = c.data.split("_"); idd = int(spl[1]); tip = spl[2]; pg = int(spl[3])
    con = conn(); k = con.cursor()
    k.execute("UPDATE zapis SET stat='otboi' WHERE id=?", (idd,))
    k.execute("SELECT tipok FROM zapis WHERE id=?", (idd,)); own = k.fetchone()
    con.commit(); con.close()
    if own:
        try: await b.send_message(own[0], " Твоя заявка отклонена.")
        except: pass
    await c.message.edit_text(" Отклонено.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data=f"al_ojid_{pg}")]]))

async def main():
    podnyal()
    print(" Бот пашет...")
    await d.start_polling(b)

if __name__ == "__main__":
    asyncio.run(main())
