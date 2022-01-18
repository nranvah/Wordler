#!/usr/bin/env python
# coding: utf-8

# # Wordler Game Engine

# ## Initial Imports

import os
import sys
import pandas as pd
import numpy as np
from IPython.display import display, Markdown, HTML, clear_output
from enum import auto, Enum
import getpass


# # Wordler utilities
class Wordler():
    #     Static stuff (i.e. instance independent)
    @staticmethod
    def get_english_words_path():
        this_dir_path = os.path.dirname(os.path.realpath('__file__'))
        #         print (this_dir_path)
        # These are all the english words
        english_words_path = os.path.abspath(os.path.join(this_dir_path, 'english-words'))
        return english_words_path

    def reset_word_list(self, word_length: int = 5):
        english_words_path = Wordler.get_english_words_path()
        valid_wordles_path = os.path.join(english_words_path, f'valid_wordles_{word_length}.txt')
        self.valid_wordles_path = valid_wordles_path
        if not (os.path.exists(valid_wordles_path)):
            words_alpha_list = pd.read_csv(os.path.join(english_words_path, 'words_alpha.txt'), header=None,
                                           names=['Words'], dtype='str')
            #     display(words_alpha_list)
            mask = (words_alpha_list.Words.str.len() == word_length)
            wordle_valid_list = words_alpha_list[mask]
            wordle_valid_list.to_csv(self.valid_wordles_path, header=None, index=None)

    def get_word_list(self):
        english_words_path = Wordler.get_english_words_path()
        wordle_valid_list = pd.read_csv(self.valid_wordles_path, header=None, names=['Words'], dtype='str').Words.values
        #         display(wordle_valid_list)
        return wordle_valid_list

    # Initialise
    def __init__(self, word_length: int = 5):
        self.word_length = 5
        if not (word_length is None):
            self.word_length = word_length
            self.reset_word_list(self.word_length)
        self.valid_words = self.get_word_list()

    def is_valid_wordle(self, word: str):
        word = str.lower(word)
        is_valid_wordle = word in self.valid_words
        return is_valid_wordle

    class Wordle_Status(Enum):
        PLAYING = auto()
        WON = auto()
        LOST = auto()

    class Guess_Result(Enum):
        # We need to preserve the order here
        Unknown = 4
        NotInWord = 3
        InCorrectPlace = 2
        CorrectPlace = 1

        def __gt__(self, other):
            if self.__class__ is other.__class__:
                #                 print(f'current value: {self.value}, new value: {other.value}')
                #                 print(f'returning {self.value > other.value}')
                return self.value > other.value
            return NotImplemented


# ## Wordler Game
# Gaming stuff
class Game():
    class Guess_Result():
        def __init__(self,
                     msg='',
                     status: Wordler.Wordle_Status = Wordler.Wordle_Status.PLAYING,
                     tries_left: int = 6,
                     results: dict = dict(),
                     guesses: list = []
                     ):
            self.msg = msg
            self.results = results
            self.status = status
            self.tries_left = tries_left

    def __init__(self, word_to_guess: str, word_length: int = 5, max_tries: int = 6):
        self.engine = Wordler(word_length=word_length)  # Initialises and caches valid words
        word_to_guess = str.lower(word_to_guess)
        is_valid_wordle = self.engine.is_valid_wordle(word_to_guess)
        if is_valid_wordle:
            print(f'Good start buddy. That word is indeed a valid Wordle. ;-)')
        else:
            raise Exception(f'Come on!!!! Jeez! "{word_to_guess}" is not a valid Wordle.')
        self.word_to_guess = word_to_guess
        self.max_tries = max_tries
        self.tries_left = self.max_tries
        self.status = Wordler.Wordle_Status.PLAYING
        self.guesses = []
        self.results_per_guess = []
        self.alphabet_results = {char: Wordler.Guess_Result.Unknown for char in
                                 ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
                                  'r', 's', 't', 'u', 'v', 'w', 'y', 'z']}

    #         print(self.alphabet_results)
    #         self.print_alphabet_results()

    def update_alphabet_results(self, char: str, result_type: Wordler.Guess_Result):
        #         if (char == 't'):
        #             print(f'current result = {self.alphabet_results[char]}')
        #             print(f'new result = {result_type}')
        #         print(f'updating character map for {char}')
        if not (self.alphabet_results[char] > result_type):
            pass  # do nothing
        else:
            self.alphabet_results[char] = result_type

    #         if (char == 't'):
    #             print('after update')
    #             print(f'current result = {self.alphabet_results[char]}')

    def print_alphabet_results(self):
        def __print_inside_box(c: str, color: str):
            mdar_string = f" <span style='font-size:16px; font-weight: bold; background:#F5F5F5; border:1px; border-style:solid; border-color:#FF0000; padding: 0.25em; overflow: visible; color: {color};'>{c}</span> "
            return mdar_string

        mdar_string = '<p><br><br>Your available letters are: '
        for char in self.alphabet_results:
            letter = char
            result_type = self.alphabet_results[char]
            #             print(f'{letter}: {result_type}')
            if result_type == Wordler.Guess_Result.CorrectPlace:
                mdar_string += __print_inside_box(letter, 'green')
            elif result_type == Wordler.Guess_Result.InCorrectPlace:
                mdar_string += __print_inside_box(letter, 'orange')
            elif result_type == Wordler.Guess_Result.NotInWord:
                mdar_string += __print_inside_box(letter, 'red')
            else:
                mdar_string += __print_inside_box(letter, 'grey')
        mdar_string += '</p>'
        #         print(mdar_string)
        display(Markdown(mdar_string))

    def print_progress_box_guessed(self):
        num_tries = len(self.results_per_guess)
        for i in range(num_tries):
            Game.printmd(self.results_per_guess[i])

    def print_progress_box_unguessed(self):
        #         print('got b')
        tries_left = self.tries_left
        empty_results_set = [("_", Wordler.Guess_Result.Unknown) for i in range(self.engine.word_length)]
        for i in range(tries_left):
            Game.printmd(empty_results_set)

        def __print_inside_box(c: str, color: str):
            mdar_string = f" <span style='font-size:16px; font-weight: bold; background:#F5F5F5; border:1px; border-style:solid; border-color:#FF0000; padding: 0.25em; overflow: visible; color: {color};'>{c}</span> "
            return mdar_string

        mdar_string = '<p><br><br>Your available letters are: '
        for char in self.alphabet_results:
            letter = char
            result_type = self.alphabet_results[char]
            #             print(f'{letter}: {result_type}')
            if result_type == Wordler.Guess_Result.CorrectPlace:
                mdar_string += __print_inside_box(letter, 'green')
            elif result_type == Wordler.Guess_Result.InCorrectPlace:
                mdar_string += __print_inside_box(letter, 'orange')
            elif result_type == Wordler.Guess_Result.NotInWord:
                mdar_string += __print_inside_box(letter, 'red')
            else:
                mdar_string += __print_inside_box(letter, 'grey')
        mdar_string += '</p>'
        #         print(mdar_string)
        display(Markdown(mdar_string))

    def tries_left(self):
        return self.tries_left

    def status(self):
        return self.status

    def guesses_msg(self):
        tries_taken = self.max_tries - self.tries_left
        msg = ''
        msg += 'Your guesses have been: ' + ','.join(self.guesses) + '\n'
        msg += f'You have used up {tries_taken}/{self.max_tries} tries.\n'
        return msg

    def printmd(results: list = []):
        def __print_inside_box(c: str, color: str):
            md_string = f" <span style='font-size:24px; background:#F0FFFF; border:1px; border-style:solid; border-color:#FF0000; padding: 0.1em; overflow: visible; color: {color};'>{c}</span> "
            return md_string

        md_string = '<p>'
        for result in results:
            letter = result[0]
            result_type = result[1]
            if result_type == Wordler.Guess_Result.CorrectPlace:
                md_string += __print_inside_box(letter, 'green')
            elif result_type == Wordler.Guess_Result.InCorrectPlace:
                md_string += __print_inside_box(letter, 'orange')
            elif result_type == Wordler.Guess_Result.NotInWord:
                md_string += __print_inside_box(letter, 'red')
            else:
                md_string += __print_inside_box(letter, 'grey')
        md_string += '</p>'
        #         print(md_string)
        display(Markdown(md_string))

    def won_result(self, results: list = []):
        tries_taken = self.max_tries - self.tries_left
        guesses = ','.join(self.guesses)
        msg = f'You already won in {tries_taken}/{self.max_tries} tries.\n'
        msg += 'Congratulations.' + self.guesses_msg() + '\n'
        msg += f'Wordle was {self.word_to_guess}.'
        result = Game.Guess_Result(
            msg=msg,
            status=self.status,
            tries_left=self.tries_left,
            results=results,
            guesses=self.guesses
        )
        print(result.msg)
        #         print('\n')
        return result

    def lost_result(self, results: list = []):
        tries_taken = self.max_tries - self.tries_left
        guesses = ','.join(self.guesses)
        msg = f'You already lost in {tries_taken}.\n'
        msg += 'Go on, try another game of Wordle.' + self.guesses_msg() + '\n'
        msg += f'Wordle was {self.word_to_guess}.'
        result = Game.Guess_Result(
            msg=msg,
            status=self.status,
            tries_left=self.tries_left,
            results=results,
            guesses=self.guesses
        )
        print(result.msg)
        #         print('\n')
        return result

    def invalid_guess_result(self, msg: str = ''):
        tries_taken = self.max_tries - self.tries_left
        guesses = ','.join(self.guesses)
        msg = f'Invalid Entry because: {msg}' + '\n'
        result = Game.Guess_Result(
            msg=msg,
            status=self.status,
            tries_left=self.tries_left,
            guesses=self.guesses
        )
        print(result.msg)
        #         print('\n')
        return result

    def playing_result(self, results: list = []):
        tries_taken = self.max_tries - self.tries_left
        msg = 'Keep playing.' + self.guesses_msg()
        result = Game.Guess_Result(
            msg=msg,
            status=self.status,
            tries_left=self.tries_left,
            results=results,
            guesses=self.guesses
        )
        #         print(result.msg)
        #         print('\n')
        return result

    def guess(self, word: str):
        word = str.lower(word)
        if (self.status == Wordler.Wordle_Status.WON):
            return self.won_result()
        if (self.status == Wordler.Wordle_Status.LOST):
            return self.lost_result()
        if (word in self.guesses):
            return self.invalid_guess_result(f'{word} is in previous guesses.')
        is_valid_wordle = self.engine.is_valid_wordle(word)
        if not (is_valid_wordle):
            return self.invalid_guess_result(f'{word} is not in list of words. Please try again.')
        else:
            self.tries_left -= 1
            results = []
            correct_guesses = 0
            self.guesses.append(word)
            for i in range(self.engine.word_length):
                char = word[i]
                if (char == self.word_to_guess[i]):
                    this_result = Wordler.Guess_Result.CorrectPlace
                    correct_guesses += 1
                elif (char in self.word_to_guess):
                    this_result = Wordler.Guess_Result.InCorrectPlace
                else:
                    this_result = Wordler.Guess_Result.NotInWord
                results.append((char, this_result))
                self.update_alphabet_results(char, this_result)
            #             Game.printmd(results)
            self.results_per_guess.append(results)
            if (correct_guesses == self.engine.word_length):
                self.status = Wordler.Wordle_Status.WON
                return self.won_result(results=results)
            else:
                if (self.tries_left == 0):
                    self.status = Wordler.Wordle_Status.LOST
                    return self.lost_result(results=results)
                else:
                    return self.playing_result(results=results)

    def print_color_key():
        color_key = [
            ('In right place', Wordler.Guess_Result.CorrectPlace),
            ('In wrong place', Wordler.Guess_Result.InCorrectPlace),
            ('Not in word', Wordler.Guess_Result.NotInWord),
            ('Unknown', Wordler.Guess_Result.Unknown),
        ]
        Game.printmd(color_key)

    def play_manual(self):
        def is_number(guess):
            try:
                # Convert it into integer
                val = int(guess)
                return True
            except ValueError:
                try:
                    # Convert it into float
                    val = float(guess)
                    return True
                except ValueError:
                    return False

        msg = 'Lets begin the game.'
        while self.status == Wordler.Wordle_Status.PLAYING:
            def display_status(msg: str):
                clear_output()
                clear_output()
                Game.print_color_key()
                self.print_alphabet_results()
                self.print_progress_box_guessed()
                self.print_progress_box_unguessed()
                print('\n')
                print(msg)

            display_status(msg)
            which_try = self.max_tries - self.tries_left + 1
            this_guess = input(f'Enter your guess #{which_try} (enter number to quit the game): ')
            if is_number(this_guess):
                print('Sorry to see you go. Lets play another time.')
                break
            result = self.guess(this_guess)
            msg = result.msg
            display_status(msg)


def create_wordler(word_length: int = 5, max_tries: int = 6):
    msg = 'Welcome WORDLE host. What is the word that people need to guess? '
    word_to_guess = getpass.getpass(msg)
    game = Game(word_to_guess=word_to_guess, word_length=word_length, max_tries=max_tries)
    return game


# ## Example of how to create and play
# game = create_wordler(word_length=5, max_tries=6)
# game.play_manual()




