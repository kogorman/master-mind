#!/usr/bin/env python3
# Based on Knuth's "The Computer as Master Mind", J Recreational Mathematics Vol 9(1) 1976-77
# License: Creative Commons By 4.0 (https://creativecommons.org/licenses/by/4.0/)
# Last Modified: Mon Jul 29 19:38:13 PDT 2019

import argparse
import sys
import random

guess_version = "1.0"

def posint(s):
    '''Input validator for positive integers.

    Arguments:
        a string that should represent a positive integer.
    Result:
        the corresponding int
    Exceptions:
        on error
    '''
    v = int(s)
    if v <= 0:
        raise Exception(
                f'input must be a positive integer but {s} was supplied'
            )
    return v

def letter_string(l):
    '''Input validator for a string of 6 letters.

    Arguments:
        a string of 6 unique letters.
    Result
        the argument s
    Exceptions:
        on error
    '''
    if l is None:
        return l
    s = set(l)
    if len(l) != 6 or len(s) != 6:
        raise Exception(f'--letters -l argument requires 6 different letters but is {repr(l)}.')
    for ch in s:
        if ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            raise Exception('--letters -l argument requires English letters.')
    return l

def word_list(w):
    '''Input validator for a list of 6 color-names.
    
    Arguments:
        a comma-separated string of 6 words.
    Result
        the corresponding list of words
    Exceptions:
        on error
    '''
    if w is None:
        return None
    l = w.split(',')
    s = set(l)
    if len(l) != 6 or len(s) != 6:
        raise Exception('--words -w argument requires 6 different words.')
    for ch in w:
        if ch not in "abcdefghijklmnopqrstuvwxyz,ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            raise Exception('--words -w argument requires English letters.')
    return l

def match(a,b):
    ''' Determine the results of matching a guess and a code.

    Inputs:
        a,b code words (it doesn't matter which is which)
        must be lists or sequences of 4 elements each; all elements must be mutually comparable
        and none of which may be exactly "X"
    Resuts
        sequence (B,W) of integers, black hits and white hits
    Exceptions:
        raised if either argument's length is not 4
    '''
    if len(a) != 4:
        raise(Exception, " *** ERROR, len(a) is",len(a),", value is",a)
    if len(b) != 4:
        raise(Exception, " *** ERROR, len(b) is",len(b),", value is",b)
    av = [0,0,0,0]
    bv = [0,0,0,0]
    blackhits = whitehits = 0
    for i in range(4):
        if a[i] == b[i]:
            blackhits += 1
            bv[i] = "X"
            av[i] = "X"
        else:
            av[i] = a[i]
            bv[i] = b[i]
    for i in range(4):
        if av[i] != "X":
            if av[i] in bv:
                whitehits += 1
                w = bv.index(av[i])
                bv[w] = "X"
    return (blackhits, whitehits)

def howbad(guess, targets):
    '''Find the largest subset of targets that share a result when matched with guess.
    
    Arguments:
        guess a code to be used a guess
        targets a set of codes which may be matched.
    Result:
        num the size of the largest group of targets that all produce the same match result.

    Exceptions:
        Whatever may be thrown by match()
    '''
    counts = dict()
    for black in range(5):
        for white in range(5-black):
            counts[(black,white)] = 0
    for target in targets:
        m = match(guess, target)
        counts[m] += 1
    how = max(counts.values())
    #print(counts)
    #print(counts.values())
    #print(guess,"on", len(targets),"targets gives at least one group of size",how)
    return how

def guessWhat(codes, subset):
    '''Find the best guess(es) to reduce the maximum number of elements of subset that
    give the same match.

    Arguments:
        codes   a set comprising the universe of codes
        subset  a set comprising the codes to be discriminated (must be a subset of 'codes')
    Result:
        (num, best) a tuple
        num: the maximum number of elements of subset that give the same match to each element of best
        best: a set of codes which do at least as well as any other; can be any of the elements of
            argument 'codes'.
    '''
    how = len(subset)
    bad = set() | subset

    # Special cases where it makes no sense to return anything not in subset.
    if how <= 2:
        return (1, bad)

    for code in codes:
        v = howbad(code, subset)
        if v > 0 and v < how:
            bad = {code}
            how = v
        elif v == how:
            bad |= {code}

    return (how, bad)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='''The Program as Master Mind (with apologies to Donald E. Knuth.)
            This is version {}.
            The program makes guesses and the user must supply the answers.  If the answers
            are correct, the program is guaranteed to find the code in 5 guesses or less.

            Inspired by the paper "The Computer as Master Mind", J. Recreational Mathematics, Vol 9(1),
            1976-77 by Donald E. Knuth.  See
            http://www.cs.uni.edu/~wallingf/teaching/cs3530/resources/knuth-mastermind.pdf
            accessed July 2019.'''.format(guess_version),
            epilog='''The program acts as codebreaker; you must create the hidden code and provide results
            for the program's guesses.  You present each result as two digits, representing black hits
            and while hits.  Each digit must be in the range 0-4.  Each round ends when either no candidates
            remain, or your result is "40".
            The program will proceed to crack the next code, ad infinitum or until you
            enter "end" or any of several similar words.''')
    parser.add_argument('--relax', '-r', action='store_true',
            help='''Relax Knuth's rule of choosing the guess with the lowest number. and a possible
            answer if one is available.  Instead, any guess that matches the best reduction is the
            search space is eligible, and if there is more than one, a random choice is made.
            This should still solve the game, but the guarantee of a win in 5 has not been proven,
            as far as I know, but I have not seen any counterexamples either.''')
    parser.add_argument('--show-count', '-c',action='store_true',
            help='''Show the number of codes which remain possible answers.''')
    parser.add_argument('--show-x', '--show-extension','-x',action='store_true',
            help='''Show that a guess is not a possible code by an "x" after the code (extension to the
            search space)''')
    parser.add_argument('--choices', '-C', type=posint, nargs='?', default=0,
            help='''The cutoff for showing candidate answers.  If their number is greater than the cutoff,
            no candidates are shown.  The default is zero (never shown.)''')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--guess','-G', action='store_true',
            help='''show each guess as a sequence of 4 names of colors used in the "guess" game: Red, Yellow,
            Green, Blue, Tan or Purple.''')
    group.add_argument('-g', action='store_true',
            help='''show each guess as a sequence of 4 letters chosen from "rygbtp" instead of the default
            "123456", these being the initial letters of the colors from the "guess" game.''')
    group.add_argument('--letters','-l',type=letter_string, nargs='?',default=None,
            help='''show each guess as a sequence of 4 letters chosen from the 6-letter string used as
            the value of this argument.''')
    group.add_argument('--words','-w',type=word_list, nargs='?', default=None,
            help='''show each guess as a sequence of 4 words chosed from the comma-separated list of
            6 words used as the value of this argument.''')
    parser.add_argument('--version', '-V', action='store_true',
            help="Show the version number and exit (ignoring all other options.)")
    args = parser.parse_args()

    xspace = " "
    if args.guess:
        args.words = ['Red','Yellow','Green','Blue','Tan','Purple']
    if args.g:
        args.letters = 'rygbtp'
    if args.letters is None and args.words is None:
        args.letters='123456'
        xspace = ""

    if args.words is not None:
        lens = [len(x) for x in args.words]
        maxlen = max(lens)
        xspace = " "

    if args.version:
        print(f"This is Master Mind, version {guess_version}.")
        exit(0)
    print("Master Mind")
    if len(sys.argv)==1:
        print(f'Invoke "{sys.argv[0]} -h" for options and other help')
    print()

    allcodes = set()
    colors = ["1", "2", "3", "4", "5", "6"]
    for a in colors:
        for b in colors:
            for c in colors:
                for d in colors:
                    code = a+b+c+d
                    allcodes |= {code}
    try:
        while True:
            s = set()
            s |= allcodes

            suffix=''
            if args.random:
                how, bad = guessWhat(allcodes, s)
                guess = random.choice(list(bad))
            else:
                guess="1122"

            count = len(s)
            while len(s) > 0:
                if len(s) <= args.choices:
                    print("Remaining candidates:",end="")
                    remaining = list(s)
                    remaining.sort()
                    for i in remaining:
                        print(f" {i}",end="")
                    print()
                if count <= 0:
                    print("Impossible.  Quitting.")
                    exit(1)
                r=""
                while r == "":
                    if args.letters is not None:
                        guesslen = 4
                        guessstr = ''
                        for p in range(4):
                            guessstr += args.letters[int(guess[p])-1]
                    elif args.words is not None:
                        guesslen = maxlen * 4 + 3
                        guesses = []
                        for p in range(4):
                            guesses += [args.words[int(guess[p])-1]]
                        guessstr = " ".join(guesses)
                    else:
                        raise Exception("Never happen")
                    if args.show_x:
                        guesslen += len(xspace) + 1
                        if suffix != '':
                            added = xspace + suffix
                            guessstr += added
                    if args.show_count:
                        guessstr = f'{len(s):4d}({guessstr})'
                        guesslen += 6
                    print(f"Guess {guessstr:>{guesslen}s} result: ",end='')
                    r = input()
                    if r.lower() in ["end","bye","quit","exit","done"]:
                        raise KeyboardInterrupt
                    if len(r) != 2:
                        print("Must be 2 digits")
                        r = ""
                        continue
                    elif r[0] not in {"0","1","2","3","4"}:
                        print(r[0],"is invalid")
                        r = ""
                        continue
                    elif r[1] not in {"0","1","2","3","4"}:
                        print(r[1],"is invalid")
                        r = ""
                        continue
                    elif r[0] == "3" and r[1] == "1":
                        print(r,"is impossible")
                        r = ""
                        continue
                    x = int(r[0])
                    y = int(r[1])
                    if x + y > 4:
                        print("there are not",x+y,"columns")
                        r = ""
                        continue
                    r = [x,y]
                if x == 4:
                    print(" SUCCESS: all black")
                    print()
                    break
                elif len(s) < 2:
                    print(" *** ERROR: that had to be the right one!!!")
                    break

                news = set()
                for c in s:
                    # Pick candidates
                    exact, other = match(c, guess)
                    if exact == x and other == y:
                        news |= {c}
                if len(news) == 0:
                    print(" *** ERROR: No candidates left; I quit!")
                    break
                elif len(news) == 1:
                    for i in news:
                        guess = i
                        break
                    #print(" ALMOST THERE: answer must be",guess)
                elif len(news) == 2:
                    for i in news:
                        guess = i
                        break
                s = news

                if len(s) == 0:
                    break
                else:
                    #if len(s) < 3:
                    #    print("Choose one of these; one of the is the answer.")
                    #    for i in s:
                    #        print("    ",i)
                    #    break

                    how, bad = guessWhat(allcodes, s)
                    if args.random:
                        guess = random.choice(list(bad))
                        if guess not in s:
                            suffix = "X"
                        else:
                            suffix = ""
                    else:
                        if len(bad & s) > 0:
                            ingroup = bad & s
                            suffix = ""
                        else:
                            ingroup = bad
                            suffix = "x"
                        guess = min(ingroup)

                    #while len(guess) != 4:
                    #    print("Enter the next guess: ",end="")
                    #    guess = input()
                    #    if len(guess) != 4:
                    #        print(" *** need exactly 4 digits")
    except KeyboardInterrupt:
        print("Interrupt")
    except EOFError:
        print("EOF reached")
    print()
    print()
    print("Goodbye and thanks for playing!")
