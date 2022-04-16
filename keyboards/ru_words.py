board_height = 5
board_width = 13
screen_height = 4
asset_folder = 'words/ru'
backspace_key = 'backspace'
enter_key = 'enter'
default_layout = 'words1'
preview_keys = {
    'words1': 'Слова 1',
    'words2': 'Слова 2',
    'pos': 'Хорошее',
    'neg': 'Плохое',
    'sys': 'НД_Множ.',
    'other': 'Другое',
    'pronouns': 'Местоимения',
    'tags': 'Теги тона',
    'default': 'Слова',
}
layouts = {
    'words1': [
        ['животное', 'ктонибудь', 'взрослый', 'брат', 'кошка', 'канал', 'ребёнок', 'одежда', 'цвет', 'папа', 'день', 'собака', 'эмодзи'],
        ['кто угодно', 'что угодно', 'семья', 'еда', 'мама', 'музыка', 'имя', 'ночь', 'родитель', 'картинка', 'практика', 'ощущение', 'сервер'],
        ['родственник', 'сестра', 'ктонибудь', 'чтонибудь', 'песня', 'вещь', 'сегодня', 'завтра', 'слово', 'вчера'],
        [],
        ['words2', 'pos', 'neg', 'sys', 'other', 'pronouns', 'tags', 'cyr', 'sym', 'lat', 'en_words/words1', 'enter', 'backspace'],
    ],
    'words2': [
        ['все', 'любое', 'короче', 'назад', 'потому что', 'минутку', 'дышать', 'быть', 'ЛС', 'рано', 'видеть', 'объяснять', 'чувствовать'],
        ['находить', 'идти', 'брать', '(прошл.)', '(будущ.)', 'происходить', 'здесь', 'держать', 'не знаю', 'знать', 'поздно', 'лево', 'смотреть'],
        ['может быть', 'сейчас', 'не в сети', 'в сети', 'правда', 'отвечать', 'право', 'бежать', 'говорить', 'маленький', 'видеть', 'всё равно', 'сказать'],
        ['большой', 'честно говоря', 'там', 'думать', '(повел.)', 'понимать', 'очень', 'ждать', 'просыпаться', 'хотеть', 'нормально', 'длинный', 'есть'],
        ['words1', 'pos', 'neg', 'sys', 'other', 'pronouns', 'tags', 'cyr', 'sym', 'lat', 'en_words/words2', 'enter', 'backspace'],
    ],
    'pos': [
        ['одеяло', 'удобно', 'мечтать', 'хаха', 'привет', 'обнять', 'увидимся', 'удача', 'сделать', 'окей', 'спать', 'игрушка', 'спасибо'],
        ['забота', 'круто', 'готово', 'легко', 'эпик', 'восторг', 'любимое', 'друг', 'удачи!', 'ржака', 'лол', 'приятно', 'познакомиться'],
        ['конечно', 'клёво', 'да', 'ага', 'ням', '!', '!!!'],
        ['симпатия', 'зайчик', 'котик', 'парень', 'чувства', 'девушка', 'люблю', 'целую', 'мур', 'ня', 'партнёр', 'мило', 'обнимаю'],
        ['words1', 'words2', 'neg', 'sys', 'other', 'pronouns', 'tags', 'cyr', 'sym', 'lat', 'en_words/pos', 'enter', 'backspace'],
    ],
    'neg': [
        ['одиноко', 'холодно', 'неважно', 'забыть', 'голод', 'потеряться', 'скучаю', 'проехали', 'грустно', 'извини', 'силы_энергия', 'усталость', '_..._'],
        ['всегда', 'доставать', 'внимание', 'носить', 'дела', 'подожди', 'горячо', 'порядок', 'никогда', 'запомнить', 'прямо сейчас', 'школа', 'мыть_чистить'],
        ['блок', 'не могу', 'удалить', 'не трогай меня', 'нервничать', 'не надо', 'драться', 'тяжело', 'ненавидеть', 'больно', 'уходить', 'злость', 'нет'],
        ['не', 'страшно', 'расстроить', 'стой', 'стресс', 'дискомфорт', 'обида', 'неправильно', 'ай', '!!',],
        ['words1', 'words2', 'pos', 'sys', 'other', 'pronouns', 'tags', 'cyr', 'sym', 'lat', 'en_words/neg', 'enter', 'backspace'],
    ],
    'sys': [
        ['тревожность', 'СДВГ', 'РАС', 'депрессия', 'фиджет', 'стим', 'тик', 'травма', 'триггер'],
        ['тело', 'опекун', 'фактив', 'фиктив', 'фаитив', 'хранитель', 'хедмейт', 'хедспейс', 'интрожект', 'хост', 'хедмейтребёнок', 'хедмейтподросток', 'инокин'],
        ['преследователь', 'Plural Kit', 'прокси', 'источник', 'система', 'тульпа', 'таппер', 'Tupperbox'],
        ['размыто', 'невербально', 'полувербально', 'регресс', 'переключение', 'вербалфлюкс'],
        ['words1', 'words2', 'pos', 'neg', 'other', 'pronouns', 'tags', 'cyr', 'sym', 'lat', 'en_words/sys', 'enter', 'backspace'],
    ],
    'other': [
        ['эти', 'про', 'после', 'кстати', 'зачем', 'и', 'а', 'у', 'вроде', 'до', 'но', 'может', 'бы'],
        ['-то', '-нибудь', 'мало', 'одно', 'для', 'от', 'за', 'если', 'одни', 'где', 'как', 'просто', 'как-то'],
        ['в', 'из', 'ясно', 'или', 'много', 'должен', 'то', 'те', 'это', 'хотя', 'к', 'тоже', 'эм'],
        ['было', 'были', 'будет', 'когда', 'с'],
        ['words1', 'words2', 'pos', 'neg', 'sys', 'pronouns', 'tags', 'cyr', 'sym', 'lat', 'en_words/other', 'enter', 'backspace'],
    ],
    'pronouns': [
        ['я', 'меня', 'мне', 'мной', 'моё', 'мои', '', 'мы', 'нас', 'нам', 'нами', 'наше', 'наши'],
        ['ты', 'тебя', 'тебе', 'тобой', 'твоё', 'твои', '', 'вы', 'вас', 'вам', 'вами', 'ваше', 'ваши'],
        ['', 'себя',  'себе', 'собой', 'своё', 'свои'],
        ['он', 'его', 'ему', '', 'она', 'её', 'ей', '', 'оно', '', 'они', 'их', 'им'],
        ['words1', 'words2', 'pos', 'neg', 'sys', 'other', 'tags', 'cyr', 'sym', 'lat', 'en_words/pronouns', 'enter', 'backspace'],
    ],
    'tags': [
        ['_gen', '_hyp', '_hj', '_j', '_lh', '_nav', '_nbh', '_neg', '_nm', '_p', '_pos', '_r', '_s'],
        ['_srs', '_t'],
        [],
        [],
        ['words1', 'words2', 'pos', 'neg', 'sys', 'other', 'pronouns', 'cyr', 'sym', 'lat', 'en_words/tags', 'enter', 'backspace'],
    ],
}

alt_text = {
    k: [[string
         .replace('_', '/')
         # TODO: remove the need for these three
         .replace('онибудь', 'о-нибудь')
         .replace('хедмейтр', 'хедмейт-р')
         .replace('хедмейтп', 'хедмейт-п')
         for string in row] for row in v] for k, v in layouts.items()
}