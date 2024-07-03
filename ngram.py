import numpy as np
from collections import Counter
from collections import defaultdict

def normalize(counter):
    """ Convert a `letter -> count` counter to a list 
    of (letter, frequency) pairs, sorted in descending order of 
    frequency.

    Parameters
    -----------
    counter : collections.Counter
        letter -> count

    Returns
    -------
    List[Tuple[str, float]]
       A list of tuples: (letter, frequency) pairs in order
       of descending-frequency

    Examples
    --------
    >>> from collections import Counter
    >>> letter_count = Counter({"a": 1, "b": 3})

    >>> normalize(letter_count)
    [('b', 0.75), ('a', 0.25)]
    """
    total = sum(counter.values())
    return [(char, cnt/total) for char, cnt in counter.most_common()]

def train_lm(text, n):
    """ Train character-based n-gram language model on: 
    Given a sequence of n-1 characters -> what the probability distribution is for the n-th character in the sequence.

    For example if we train on the text:
        text = "cacao"

    Using a n-gram size of n=3, then the following dict would be returned.
    See that we *normalize* each of the char_count_tuples for a given history

        {'ac': [('a', 1.0)],
         'ca': [('c', 0.5), ('o', 0.5)],
         '~c': [('a', 1.0)],
         '~~': [('c', 1.0)]}

    Tildas ("~") are used for padding the history when necessary, so that it's 
    possible to estimate the probability of a seeing a character when there 
    aren't (n - 1) previous characters of history available.

    So, according to this text we trained on, if you see the sequence 'ac',
    our model predicts that the next character should be 'a' 100% of the time.

    Parameters
    -----------
    text: str 
        A string (doesn't need to be lowercased).
        
    n: int
        The length of n-gram to analyze.

    Returns
    -------
    Dict[str, List[Tuple[str, float]]]
        
        {n-1 history -> [(letter, normalized count), ...]}
        
        A dictionary that maps histories (strings of length (n-1)) to lists of (char, prob) 
        pairs, where prob is the probability (i.e frequency) of char appearing after 
        that specific history.

    Examples
    --------
    >>> train_lm("cacao", 3)
    {'ac': [('a', 1.0)],
     'ca': [('c', 0.5), ('o', 0.5)],
     '~c': [('a', 1.0)],
     '~~': [('c', 1.0)]}
    """

    raw_lm = defaultdict(Counter) # history -> {char -> count}
    history = "~" * (n - 1)  # length n - 1 history
    
    # count number of times characters appear following different histories
    
    for char in text:
        raw_lm[history][char] += 1 # increment language model's count given current history and character
        # slide history window to the right by one character
        history = history[1:] + char # updating history
    
    # create the finalized language model – a dictionary with: history -> [(char, freq), ...]
    lm = {history : normalize(counter) for history, counter in raw_lm.items()} 
    
    return lm

def unzip(pairs):
    """
    "unzips" of groups of items into separate tuples.
    
    Example: pairs = [("a", 1), ("b", 2), ...] --> (("a", "b", ...), (1, 2, ...))
    
    Parameters
    ----------
    pairs : Iterable[Tuple[Any, ...]]
        An iterable of the form ((a0, b0, c0, ...), (a1, b1, c1, ...))
    
    Returns
    -------
    Tuple[Tuples[Any, ...], ...]
       A tuple containing the "unzipped" contents of `pairs`; i.e. 
       ((a0, a1, ...), (b0, b1, ...), (c0, c1), ...)
    """
    # zip() pairs corresponding index elements from the pairs together -> makes this a tuple
    return tuple(zip(*pairs))

def generate_letter(lm, history):
    """ Randomly picks letter according to probability distribution associated with 
    the specified history, as stored in your language model.

    Note: returns dummy character "~" if history not found in model. (ie if the orders don't match)

    Parameters
    ----------
    lm: Dict[str, List[Tuple[str, float]]] 
        The n-gram language model. (train_lm return value)
        I.e. the dictionary: history -> [(char, freq), ...]

    history: str
        A string of length (n-1) to use as context/history for generating 
        the next character.

    Returns
    -------
    str
        The predicted character. '~' if history is not in language model.
    """
    if not history in lm:
        return "~"
    # recall this is char, frequency from train_lm
    letters, probs = unzip(lm[history]) 
    i = np.random.choice(letters, p=probs) 
    return i

def generate_text(lm, n, nletters=100):
    """ Randomly generates `nletters` of text by drawing from 
    the probability distributions stored in a n-gram language model `lm`.

    Parameters
    ----------
    lm: Dict[str, List[Tuple[str, float]]]
        The n-gram language model. 
        I.e. the dictionary: history -> [(char, freq), ...]
    
    n: int
        Order of n-gram model.
    
    nletters: int (100 default)
        Number of letters to randomly generate.

    Returns
    -------
    str
        Model-generated text. Should contain `nletters` number of
        generated characters. The pre-pended ~'s are not to be included. 
    """
    history = "~" * (n - 1) # amount of history info to extract from text
    text = []
    for i in range(nletters):
        c = generate_letter(lm, history)
        text.append(c)
        history = history[1:] + c # update history
    return "".join(text)  