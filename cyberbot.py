from includes.bot import CyberBot
import sys

if __name__ == "__main__":

    try:
        bot = CyberBot(sys.argv[2]) # Bot instanciation
        bot.run(sys.argv[1])

    except IndexError:
        print(f"Error : missing API Key or Token. Try :\n\"python3 {sys.argv[0]} <BOT KEY/TOKEN> <ROOT_ME_API_KEY>\"")
        sys.exit(1) 

    except Exception as e:
        print(f"Error : {e}")
        sys.exit(1)