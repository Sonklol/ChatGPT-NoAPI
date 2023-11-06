from sys import exit
from functions import ChatGPT, clear

if __name__ == '__main__':
    chatgpt = ChatGPT()
    clear()
    ChatGPT.welcome()
    ChatGPT.controls()
    while True:
        prompt = input('[>] ')
        if prompt.lower() == 'x' or prompt.lower() == 'exit':
            chatgpt.quit_webdriver()
            exit()
        elif prompt.lower() == 'c' or prompt.lower() == 'clear' or prompt.lower() == 'cls':
            clear()
            ChatGPT.welcome()
            ChatGPT.controls()
        else:
            respuesta = chatgpt.send_msg(prompt)
            print(f'\n{respuesta}\n')