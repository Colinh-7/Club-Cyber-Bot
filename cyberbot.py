from includes.bot import CyberBot
import sys

if __name__ == "__main__":

    bot = CyberBot() # Bot instanciation

    try:
        bot.run(sys.argv[1])
    except IndexError:
        print(f"Error : missing API Key or Token. Try \"{sys.argv[0]} <KEY/TOKEN>\"")
        sys.exit(1) 
    except Exception as e:
        print(f"Error : {e}")
        sys.exit(1)