board_height = 5
board_width = 13
screen_height = 4
asset_folder = 'words/en'
backspace_key = 'backspace'
enter_key = 'enter'
default_layout = 'words1'
preview_keys = {
    'words1': 'Words1',
    'words2': 'Words2',
    'pos': 'Positive',
    'neg': 'Negative',
    'sys': 'ND_System',
    'other': 'Other',
    'pronouns': 'Pronouns',
    'tags': 'ToneTags',
    'default': 'Words',
}
layout = {
    'words1': [
        ['animal', 'anyone', 'adult', 'brother', 'cat', 'channel', 'child', 'clothes', 'color', 'dad', 'day', 'dog', 'emote'],
        ['everyone', 'everything', 'family', 'food', 'mom', 'music', 'name', 'night', 'parent', 'pic', 'practice', 'sense', 'server'],
        ['sibling', 'sister', 'someone', 'something', 'song', 'thing', 'today', 'tomorrow', 'word', 'yesterday'],
        [],
        ['words2', 'pos', 'neg', 'sys', 'other', 'pronouns', 'tags', 'lat', 'sym', 'cyr', 'ru_words/words1', 'enter', 'backspace'],
    ],
    'words2': [
        ['all', 'any', 'anyway', 'back', 'because', 'brb', 'breathe', 'come', 'DM_PM', 'early', 'eat', 'ever', 'explain'],
        ['feel', 'found', 'go', 'get', 'gone', 'happen', 'here', 'hold', 'IDK', 'know', 'late', 'left', 'long'],
        ['look', 'maybe', 'now', 'offline', 'online', 'really', 'reply', 'right', 'run', 'say', 'see', 'short', 'SMH'],
        ['still', 'talk', 'tall', 'TBH', 'there', 'think', 'tiny', 'understand', 'very', 'wait', 'wake', 'want', 'well'],
        ['words1', 'pos', 'neg', 'sys', 'other', 'pronouns', 'tags', 'lat', 'sym', 'cyr', 'ru_words/words2', 'enter', 'backspace'],
    ],
    'pos': [
        ['blanket', 'comfort', 'dream', 'haha', 'hi', 'hug', 'later', 'luck', 'make', 'okay', 'sleep', 'stuffie', 'thanks'],
        ['care', 'cool', 'done', 'easy', 'epic', 'excited', 'favorite', 'friend', 'goodluck', 'lmao', 'lol', 'nice', 'nicetomeetyou'],
        ['ofcourse', 'swag', 'yes', 'yeah', 'yum', '!', '!!!'],
        ['affection', 'baby', 'BF', 'datemate', 'feeling', 'GF', 'JF', 'love', 'meow', 'owo', 'partner', 'pretty', 'S_O'],
        ['words1', 'words2', 'neg', 'sys', 'other', 'pronouns', 'tags', 'lat', 'sym', 'cyr', 'ru_words/pos', 'enter', 'backspace'],
    ],
    'neg': [
        ['alone', 'cold', 'doesn\'tmatter', 'forgot', 'hungry', 'lost', 'miss', 'nvm', 'sad', 'sorry', 'spoon', 'tired', '_..._'],
        ['always', 'annoy', 'attention', 'bring', 'chore', 'holdon', 'hot', 'order', 'never', 'remember', 'rightnow', 'school', 'wash_clean'],
        ['block', 'can\'t', 'delete', 'DNI', 'distress', 'don\'t', 'fight', 'hard', 'hate', 'hurt', 'leave', 'mad', 'no'],
        ['not', 'scared', 'scary', 'stop', 'stressed', 'uncomfy', 'upset', 'wrong', 'yikes', '!!'],
        ['words1', 'words2', 'pos', 'sys', 'other', 'pronouns', 'tags', 'lat', 'sym', 'cyr', 'ru_words/neg', 'enter', 'backspace'],
    ],
    'sys': [
        ['anxiety', 'ADHD', 'ASD', 'depression', 'fidget', 'stim', 'tic', 'trauma', 'trigger'],
        ['body', 'caretaker', 'factive', 'fictive', 'faitive', 'gatekeeper', 'headmate', 'headspace', 'introject', 'host', 'little', 'middle', 'otherkin'],
        ['persecutor', 'PluralKit', 'proxy', 'source', 'system', 'tulpa', 'tupper', 'Tupperbox'],
        ['blurry', 'nonverbal', 'semiverbal', 'regress', 'switch', 'verbalflux'],
        ['words1', 'words2', 'pos', 'neg', 'other', 'pronouns', 'tags', 'lat', 'sym', 'cyr', 'ru_words/sys', 'enter', 'backspace'],
    ],
    'other': [
        ['a_an', 'about', 'after', 'also', 'am', 'and', 'are', 'at', 'be', 'before', 'but', 'can', 'could'],
        ['do', 'did', '-ed', '-er', 'for', 'from', 'got', 'have', 'if', '-ing', 'is', 'how', 'just'],
        ['kinda', 'much', 'of', 'oh', 'or', '-s', 'should', 'that', 'the', 'this', 'tho', 'to', 'too'],
        ['uh', 'was', 'were', 'will', 'would', 'with'],
        ['words1', 'words2', 'pos', 'neg', 'sys', 'pronouns', 'tags', 'lat', 'sym', 'cyr', 'ru_words/other', 'enter', 'backspace'],
    ],
    'pronouns': [
        ['I', 'me', 'my', 'mine', 'I\'m', '', 'we', 'us', 'our', 'ours', 'we\'re', '', '-self'],
        ['you', 'you', 'your', 'yours', 'you\'re', '', 'you', 'you', 'your', 'yours', 'you\'re', '', '-selves'],
        ['he', 'him', 'his', 'his', 'he\'s', '', 'it', 'it', 'its', 'its', 'it\'s', '', 'neos1'],
        ['she', 'her', 'her', 'hers', 'she\'s', '', 'they', 'them', 'their', 'theirs', 'they\'re', '', 'neos2'],
        ['words1', 'words2', 'pos', 'neg', 'sys', 'other', 'tags', 'lat', 'sym', 'cyr', 'ru_words/pronouns', 'enter', 'backspace'],
    ],
    'tags': [
        ['_gen', '_hyp', '_hj', '_j', '_lh', '_nav', '_nbh', '_neg', '_nm', '_p', '_pos', '_r', '_s'],
        ['_srs', '_t'],
        [],
        [],
        ['words1', 'words2', 'pos', 'neg', 'sys', 'other', 'pronouns', 'lat', 'sym', 'cyr', 'ru_words/tags', 'enter', 'backspace'],
    ],
}
