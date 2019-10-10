import random

class Card:
    def __init__(self, val, suit):
        self.val = val
        self.suit = suit
        self.color = 'Red' if suit in ('H', 'D') else 'Black'
        self.maps = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'} 
    
    def __repr__(self):
        return f'{self.maps.get(self.val, self.val)}{self.suit}'

    __str__ = __repr__

    def __eq__(self, other):
        return self.val == other.val

    def __ne__(self, other):
        return self.val != other.val

    def __lt__(self, other):
        return self.val < other.val

    def __gt__(self):
        return self.val > other.val
    
class Deck:
    def __init__(self):
        self.deck = [Card(val, suit) for val in range(2, 15) for suit in \
        ('H', 'D', 'S', 'C')]

    def shuffle(self):
        random.shuffle(self.deck)

    def __len__(self):
        return len(self.deck)

    def __repr__(self):
        return '\n'.join(str(c) for c in self.deck)

    __str__ = __repr__



class Player:
    def __init__(self, name='default', ai = False):
        self.name = name
        self.hand = []
        self.ai = ai

    def __repr__(self):
        return f'{self.name}\'s hand: {self.hand}'
    
    __str__ = __repr__

    def add_to_hand(self, source):
        res = None
        if isinstance(source, Deck):
            if source.deck:
                res = source.deck.pop()
            
        elif isinstance(source, Player):
            res = source.hand.pop(random.randint(0, len(source.hand)-1))

        elif isinstance(source, Card):
            res = source
        
        if res:
            self.hand.append(res)

        return res

    add = add_to_hand


    def give(self, card, player):
        loc = self.hand.index(card)

        player.add_to_hand(self.hand.pop(loc))

        return self.hand

    def has_card_val(self, card_val):
        return card_val in [i.val for i in self.hand]

    def total_cards_of_val(self, card_val):
        return [card for card in self.hand if card.val == card_val]


class Dealer(Player): 

    def __init__(self, name = 'Dealer', ai=False):
        super().__init__()
        self.name = 'Dealer'
        self.ai =  ai


    def deal(self, table, deck, cardsper = 0):
        deck.shuffle()
        i = cardsper if cardsper else len(deck)
        while i:
            for j in range(len(table.players)):
                table.players[j].add_to_hand(deck)
            i -= 1

        return table


class Table:
    def __init__(self, n):
        self.deck = Deck()
        self.dealer = Dealer(ai = True)
        realPlayer = input('Choose player name: ')
        #self.players = [self.dealer] + [Player("Player 1",True)]
        self.players = [self.dealer] + [Player(realPlayer)] + \
        [Player(f'P{i+1}',True) for i in range(n-2)]

    def __repr__(self):
        return '\n'.join(str(player) for player in self.players)

    def get_player(self, player_name):
        res = False

        for p in self.players:
            if p.name == player_name:
                res = p
        return res


    def seat(self, player):
        self.players.append(player)

    def kick_out(self, player_name):
        kicked = 0
        for i, p in enumerate(self.players):
            if p.name == player_name:
                kicked = i
                break
        self.players.pop(kicked)


    def __len__(self):
        return len(self.players)

    @property
    def size(self):
        return len(self)

class GoFish:
    def __init__(self, table = None):
        self.table = table if table else Table(int(input('How many players including yourself (max 5)? ')))
        self.books = {i:0 for i in range(2,15)}
        self.maps = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
    
    @property
    def set_table(self):
        cards_per_person = (5, 7)[self.table.size in (2,3)]
        self.table.dealer.deal(self.table, self.table.deck, cards_per_person)

    def play_round(self, player):
        [i.hand.sort(key = lambda x: x.val) for i in self.table.players]
        print(self.table.players[0])
        print(self.table.players[1]) 
        if self.check_win:
            return None
        if not player.hand:
            if self.table.deck.deck:
                drawn_card = player.add_to_hand(self.table.deck)
            else:
                return None
        if not player.ai:
            p_asked = self.table.get_player(input('Who are you asking: '))
            while not p_asked:
                p_asked = self.table.get_player(input('That person is not playing with you. Ask someone else: '))

            potential_c = int(input('What card rank? '))
            while not player.has_card_val(potential_c):
                potential_c = int(input('You must input a card rank you already own: '))

        else:
            print("Who are you asking: ")
            p_asked = random.choice(self.table.players)
            while p_asked.name == player.name:
                    p_asked = (random.choice(self.table.players))
            print(p_asked.name)

            print('What card rank? ')
            potential_c = random.choice(player.hand).val
            print(potential_c)
          
        if p_asked.has_card_val(potential_c):
            cards_owned = p_asked.total_cards_of_val(potential_c)
            [p_asked.give(card, player) for card in cards_owned]
            card_value = self.maps.get(potential_c,potential_c)
            print(f'{player.name} took {len(cards_owned)} {card_value} from {p_asked.name}!') if (len(cards_owned) == 1) else \
                print(f'{player.name} took {len(cards_owned)} {card_value}\'s from {p_asked.name}!')
            self.secureBook(player)
            self.play_round(player)
            return None

        else:
            print(f'{p_asked.name}: Go Fish!')
            return potential_c


    def secureBook(self, player):
        possible_values = [value for value in range(2,15)]
        temporary_val_count = {i:0 for i in possible_values}
        for card in player.hand:
            temporary_val_count[card.val] += 1
        for cards_in_rank in list(temporary_val_count.items()):
            if cards_in_rank[1] == 4:
                value_of_book = cards_in_rank[0]
                self.books[value_of_book] = player.name
                print(f'{player.name} has laid down the {self.maps.get(value_of_book,value_of_book)} book!')
                player.hand = [i for i in player.hand if i.val != value_of_book]
                return True
        return False

    @property
    def check_win(self):
        return all([True if name[1] else False for name in self.books.items()])

    @property
    def play(self):
        print("Shuffling Deck! Let's play some GoFish!")
        self.set_table
        while not self.check_win:
            player_index = 0
            while player_index < len(self.table.players):
                player = self.table.players[player_index]             
                card_rank_asked = self.play_round(player)
                if self.check_win:
                    return None
                drawn_card = player.add_to_hand(self.table.deck)
                self.secureBook(player)
                if self.check_win:
                    return None
                elif drawn_card and (drawn_card.val == card_rank_asked): 
                    if self.secureBook(player) and self.check_win():
                        return None
                    print(f"{player} has fished their wish!") 
                    continue  #Fish your wish

                player_index += 1

    @property
    def winner(self):
        book_owners = [i[1] for i in list(self.books.items())]
        winner = max(book_owners, key=book_owners.count)
        print(f'The winner is {winner} with {book_owners.count(winner)} books!')

    @property
    def main(self):
        self.play
        self.winner

a = GoFish()
a.main




