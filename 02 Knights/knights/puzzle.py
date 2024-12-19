from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
statementA0 = And(AKnight, AKnave)
knowledge0 = And(
    # Rules of the game
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    # A statement
    Biconditional(statementA0, AKnight) # equivalent to Implication(statementA0, AKnight) AND Implication(Not(statementA0), AKnave)
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
statementA1 = And(AKnave, BKnave)
knowledge1 = And(
    # Rules of the game
    Or(AKnight, BKnight),
    Not(And(AKnight, BKnight)),

    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    # A statement
    Biconditional(statementA1, AKnight)
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
statementA2 = Or(And(AKnight, BKnight), And(AKnave, BKnave))
satementB2 = Or(And(AKnight, BKnave), And(AKnave, BKnight))
knowledge2 = And(
     # Rules of the game
    Or(AKnight, BKnight),
    Not(And(AKnight, BKnight)),

    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    # A statement
    Biconditional(statementA2, AKnight),
    # B statement
    Biconditional(satementB2, BKnight),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
# A says nothing. His statement means nothing.
statementA3 = Or(AKnight, AKnave)
statementB3 = And(Biconditional(AKnight, AKnave), CKnight)
statementC3 = AKnight
knowledge3 = And(
    # Rules of the game
    Or(AKnight, BKnight, CKnight),
    Not(And(AKnight, BKnight)),
    Not(And(BKnight, CKnight)),

    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave)),
    # A statement
    Biconditional(AKnight, statementA3),
    # B statement
    Biconditional(BKnight, statementB3),
    # C statement
    Biconditional(CKnight, statementC3)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
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
