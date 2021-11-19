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
    'tags': 'ToneTags',
    'default': 'Words',
}
layout = {
    'words1': [
        ['animal', 'anyone', 'adult', 'brother', 'cat', 'channel', 'child', 'clothes', 'color', 'dad', 'day', 'dog', 'emote'],
        ['everyone', 'everything', 'family', 'food', 'mom', 'music', 'name', 'night', 'parent', 'pic', 'practice', 'sense', 'server'],
        ['sibling', 'sister', 'song', 'thing', 'today', 'tomorrow', 'word', 'yesterday'],
        ['I', 'I\'m', 'me', 'you', 'he', 'she', 'it', 'we', 'us', 'they'],
        ['words2', 'pos', 'neg', 'sys', 'other', 'tags', 'lat', 'cyr', 'cyr_words', '', '', 'enter', 'backspace'],
    ],
    'words2': [
        ['all', 'any', 'back', 'because', 'brb', 'breathe', 'come', 'DM_PM', 'early', 'ever', 'explain', 'feel', 'found'],
        ['get', 'gone', 'happen', 'hold', 'late', 'left', 'look', 'now', 'offline', 'online', 'really', 'reply', 'right'],
        ['run', 'say', 'short', 'SMH', 'still', 'talk', 'tall', 'TBH', 'think', 'tiny', 'understand', 'very', 'wait'],
        ['wake', 'want', 'well'],
        ['words1', 'pos', 'neg', 'sys', 'other', 'tags', 'lat', 'cyr', 'cyr_words', '', '', 'enter', 'backspace'],
    ],
    'pos': [
        ['blanket', 'comfort', 'dream', 'fidget', 'haha', 'hi', 'later', 'luck', 'make', 'sleep', 'stuffie', 'thanks'],
        ['care', 'cool', 'done', 'easy', 'epic', 'excited', 'favorite', 'friend', 'goodluck', 'lmao', 'lol', 'nice'],
        ['nicetomeetyou', 'ofcourse', 'swag', 'yum', '!!!'],
        ['affection', 'baby', 'BF', 'datemate', 'GF', 'JF', 'meow', 'partner', 'pretty', 'S/O'],
        ['words1', 'words2', 'neg', 'sys', 'other', 'tags', 'lat', 'cyr', 'cyr_words', '', '', 'enter', 'backspace'],
    ],
    'neg': [
        ['alone', 'cold', 'doesn\'tmatter', 'forgot', 'hungry', 'lost', 'miss', 'nvm', 'sorry', 'spoon', 'tired', '...'],
        ['always', 'annoy', 'attention', 'bring', 'chore', 'hold on', 'hot', 'order', 'never', 'remember', 'rightnow', 'school', 'wash/clean'],
        ['block', 'can\'t', 'delete', 'DNI', 'distress', 'don\'t', 'fight', 'hard', 'hate', 'hurt', 'leave', 'mad', 'no'],
        ['not', 'sad', 'scared', 'scary', 'stop', 'stressed', 'uncomfy', 'upset', 'wrong', 'yikes', '!!'],
        ['words1', 'words2', 'pos', 'sys', 'other', 'tags', 'lat', 'cyr', 'cyr_words', '', '', 'enter', 'backspace'],
    ],
    'sys': [
        ['anxiety', 'ADHD', 'ASD', 'depression', 'stim', 'tic', 'trauma', 'trigger'],
        ['body', 'caretaker', 'factive', 'fictive', 'fuzztive', 'gatekeeper', 'headmate', 'headspace', 'introject', 'host', 'little', 'middle', 'otherkin'],
        ['persecutor', 'PluralKit', 'proxy', 'source', 'system', 'tupper', 'Tupperbox'],
        ['blurry', 'nonverbal', 'semiverbal', 'regress', 'switchy', 'verbalflux'],
        ['words1', 'words2', 'pos', 'neg', 'other', 'tags', 'lat', 'cyr', 'cyr_words', '', '', 'enter', 'backspace'],
    ],
    'other': [
        ['about', 'after', 'am_are', 'before', 'can', 'could', 'do', '-ed', '-er', 'from', 'got', 'have', 'if'],
        ['-ing', 'is_are', 'how', 'just', 'kinda', 'much', 'oh', '-s', 'should', 'tho', 'too', 'was_were', 'will'], 
        ['would', 'with'],
        [],
        ['words1', 'words2', 'pos', 'neg', 'sys', 'tags', 'lat', 'cyr', 'cyr_words', '', '', 'enter', 'backspace'],
    ],
    'tags': [
        ['_gen', '_hyp', '_hj', '_j', '_lh', '_nav', '_nbh', '_neg', '_nm', '_p', '_pos', '_r', '_s'],
        ['_srs', '_t'],
        [],
        [],
        ['words1', 'words2', 'pos', 'neg', 'sys', 'other', 'lat', 'cyr', 'cyr_words', '', '', 'enter', 'backspace'],
    ],
}
