from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
sentence_0 = And(AKnave, AKnight)
knowledge0 = And(
    Implication(sentence_0, AKnight),
    Implication(Not(sentence_0), AKnave),
    Or(AKnave, AKnight),
    Not(And(AKnave, AKnight)),
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
sentence_0 = And(AKnave, BKnave)
knowledge1 = And(
    Implication(Not(sentence_0), AKnave),
    Implication(sentence_0, AKnight),
    Implication(BKnight, AKnave),
    Not(And(AKnave, AKnight)),
    Not(And(BKnave, BKnight)),
    Or(AKnave, AKnight),
    Or(BKnave, BKnight),
)
# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
sentence_0 = Or(And(AKnave, BKnave), And(AKnight, BKnight))
sentence_1 = Or(And(AKnave, BKnight), And(AKnight, BKnave))
knowledge2 = And(
    Implication(Not(sentence_0), AKnave),
    Implication(sentence_0, AKnight),
    Implication(Not(sentence_1), BKnave),
    Implication(sentence_1, BKnight),
    Not(And(AKnave, AKnight)),
    Not(And(BKnave, BKnight)),
    Or(AKnave, AKnight),
    Or(BKnave, BKnight),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
sentence_0 = And(Not(And(AKnave, AKnight)), Or(AKnave, AKnight))
sentence_1 = And(Not(sentence_0), AKnave)
sentence_2 = CKnave
sentence_3 = AKnight
knowledge3 = And(
    Implication(Not(sentence_0), AKnave),
    Implication(sentence_0, AKnight),
    Implication(Not(Or(sentence_1, sentence_2)), BKnave),
    Implication(And(sentence_1, sentence_2), BKnight),
    Implication(Not(sentence_3), CKnave),
    Implication(sentence_3, CKnight),
    Not(And(CKnave, CKnight)),
    Not(And(AKnave, AKnight)),
    Not(And(BKnave, BKnight)),
    Or(CKnave, CKnight),
    Or(AKnave, AKnight),
    Or(BKnave, BKnight),
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3),
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
