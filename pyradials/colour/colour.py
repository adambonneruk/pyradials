"""Colour extends the windows terminal with simple colour printing"""
class Colour:
    BLACK:int = '30'
    RED:int = '31'
    GREEN:int = '32'
    YELLOW:int = '33'
    BLUE:int = '34'
    MAGENTA:int = '35'
    CYAN:int = '36'
    WHITE:int = '37'
    GRAY:int = '90'
    LIGHT_RED:int = '91'
    LIGHT_GREEN:int= '92'
    LIGHT_YELLOW:int = '93'
    LIGHT_BLUE:int = '94'
    LIGHT_MAGENTA:int = '95'
    LIGHT_CYAN:int = '96'
    BRIGHT_WHITE:int = '97'

    def convert(self, string: str, colour: int):
        return '\x1b[{}m{}\x1b[0m'.format(colour, string)

    def print(self, string: str, colour: int):
        colour_string = self.convert(string, colour)
        print(colour_string)
        return None

def main():
    # initialise the colour object
    colour = Colour()

    # print some colourful words
    colour.print("Red", Colour.RED)
    colour.print("Green", Colour.GREEN)
    colour.print("Blue", Colour.BLUE)

    colour.print("Cyan", Colour.CYAN)
    colour.print("Magenta", Colour.MAGENTA)
    colour.print("Yellow", Colour.YELLOW)

    colour.print("White", Colour.WHITE)
    colour.print("Gray", Colour.GRAY)
    colour.print("Black", Colour.BLACK)

    print("\n...will you take the " + colour.convert("red pill",Colour.LIGHT_RED) + ", or take the " + colour.convert("blue pill",Colour.LIGHT_BLUE) + "?")

if __name__ == "__main__":
    main()
