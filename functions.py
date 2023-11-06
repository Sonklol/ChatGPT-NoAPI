from undetected_chromedriver import ChromeOptions, Chrome
#from os import path, getcwd
from os import name, system
from art import tprint
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from tempfile import gettempdir
from sys import exit
from pickle import dump, load
from os import path
from time import sleep
from subprocess import call

def start_webdriver(headless=False, pos="max", lang='en', proxy=False, proxylist='', proxy_type='http'):
    '''
    Inicia un navegador de Chrome y devuelve el objeto Webdruver instanciado.
    pos: indica la posición del navegador en la pantalla ("max" | "left" | "right").
    '''

    chromedriver_path = './chromedriver.exe'

    options = ChromeOptions()

    # Idioma Inglés
    options.add_argument(f"--lang={lang}")

    # Desactivar guardado de credenciales
    options.add_argument('--password-store=basic')
    options.add_experimental_option(
        'prefs',
        {
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
        },
    )

    # Proxies
    if proxy:
        options.add_argument(f'--proxy-server={proxy_type}://{proxylist}')

    # Iniciar driver
    driver = Chrome(
        path=chromedriver_path,
        #version_main=114,
        options=options,
        headless=headless,
        log_level=3,
    )

    if not headless:
        # maximizar ventana
        driver.maximize_window()
        if pos != 'max':
            ancho, alto = driver.get_window_size().values()
            if pos == "left":
                driver.set_window_rect(x=0, y=0, width=ancho//2, height=alto)
            elif pos == "right":
                driver.set_window_rect(x=ancho//2, y=0, width=ancho//2, height=alto)
    return driver

#def cursor_arriba(n=1):
#    print(f'\33[{n}A]', end='')

def clear():
    linux = 'clear'
    windows = 'cls'
    system ([linux, windows][name == 'nt'])

class ChatGPT:
    def __init__(self):
        self.COOKIES_FILE = f'{gettempdir()}/openai.cookies'

        print('Iniciando WebDriver...')
        #cursor_arriba()

        self.driver = start_webdriver(pos="left")

        self.wait = WebDriverWait(self.driver, 30)

        login = self.login_openai()
        print()
        if not login:
            exit(1)

    def login_openai(self):
        # Login por cookies
        # Comprobar si el archivo de cookies existe
        if path.isfile(self.COOKIES_FILE):
            #print(self.COOKIES_FILE)
            print('LOGIN POR COOKIES')
            cookies = load(open(self.COOKIES_FILE, 'rb'))
            print('Cargando robots.txt')
            self.driver.get('https://chat.openai.com/robots.txt')
            print('Cargando Cookies...')
            for cookie in cookies:
                #cursor_arriba()
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass

            print('Cargando ChatGPT')
            self.driver.get('https://chat.openai.com')

            login = self.check_login()
            if login:
                print('Inicio de Sesión por COOKIES - CORRECTO')

                # Chat Custom
                check_chat, url_chat = self.create_chat()
                if check_chat:
                    self.driver.get(url_chat)

                return True
            else:
                print('Inicio de Sesión por COOKIES - FALLIDO')

        # Credenciales
        self.OPENAI_USER = input("Usuario: ")
        self.OPENAI_PASSWORD = input("Contraseña: ")

        # Login normal
        print('Obteniendo la página...')
        #cursor_arriba()
            
        self.driver.get('https://chat.openai.com/auth/login')

        # Click en Log in
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[1]/div/div/button[1]')))
        button.click()

        print('Iniciando Sesión en ChatGPT - OpenAI...')
        #cursor_arriba()

        # Botón Log in
        #button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[1]/div[4]/button[1]/div')))
        #button.click()

        # Email
        v = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="username"]')))
        v.send_keys(self.OPENAI_USER)

        # Botón Continue
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/main/section/div/div/div/div[1]/div/form/div[2]/button')))
        button.click()

        # Contraseña
        e = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="password"]')))
        e.send_keys(self.OPENAI_PASSWORD)

        # Botón Continue
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/main/section/div/div/div/form/div[3]/button')))
        button.click()
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/main/section/div/div/div/form/div[3]/button')))
        button.click()
        #button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/main/section/div/div/div/form/div[3]/button')))
        #button.click()
        print('CHECK LOGIN')

        login = self.check_login()

        if login:
            print('Inicio de Sesión - CORRECTO')
            dump(self.driver.get_cookies(), open(self.COOKIES_FILE, 'wb'))

            # Chat Custom
            check_chat, url_chat = self.create_chat()
            if check_chat:
                self.driver.get(url_chat)
        else:
            print('Inicio de Sesión - FALLIDO')
        #cursor_arriba()

        return login

    def check_login(self):
        try:
            e = self.driver.find_element(By.CSS_SELECTOR, 'h3.text-lg')
            if 'session has expired' in e.text:
                print('ERROR - La sesión ha expirado')
                return False
        except:
            pass

        try:
            # Botón Okay, let’s go
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div/div/div/div[2]/div/div[4]/button")))
            button.click()
            return True
        except:
            pass

        # Check Text Box
        try:
            self.driver.find_elements(By.XPATH, '/html/body/div[1]/div[1]/div/div/main/div[3]/form/div/div/textarea')
            return True
        except:
            return False
        
    def welcome():
        tprint('ChatGPT - NO API')
        print('Programa realizado con Web Scrapping para automatizar el proceso de inicio de sesión.\nSe ha buscado la sencillez al poder tener todo desde la terminal.')
        print('\nGithub del Creador: https://github.com/sonklol')

    def controls():
        print('\n[C] Limpiar Pantalla\n[X] Salir\n')
        
    def send_msg(self, prompt):
        # Para escribir
        while True:
            try:
                e = self.wait.until(EC.element_to_be_clickable((By.TAG_NAME, 'textarea')))
                e.send_keys(prompt)
                e.send_keys(Keys.ENTER)
                break
            except Exception as z:
                print(z)

        # Recepción del mensaje
        #/html/body/div[1]/div[1]/div/div/main/div[3]/form/div/div[1]/button/div # 3 puntos de recopilando respuesta ...
        # Botón de enviar mensaje (para ver que la respuesta ya se ha generado)

        while True:
            sleep(3)
            # Coger respuesta
            e = self.driver.find_elements(By.CSS_SELECTOR, 'div.markdown')[-1]
            try:
                # Comprobar que existe el icono (...)
                self.driver.find_element(By.CSS_SELECTOR, 'div.text-2xl')
            except:
                # Si no existe es que ya se ha generado la respuesta
                if e.text:
                    break
        #cursor_arriba(n=2)

        return e.text
        
    def quit_webdriver(self):
        print('Saliendo...')

        self.driver.quit()

        # Cierra todos los procesos de Google Chrome
        call(["taskkill", "/F", "/IM", "chrome.exe"])

    def create_chat(self):
        '''
        Crea un chat con una url personalizada para no tener que
        crear un chat cada vez que accedemos.
        Esta URL de chat la guardamos en un fichero.
        '''
        # Comprobar si existe ese fichero
        if path.isfile("./url_chat.config"):
            with open("./url_chat.config", "r") as file_chat:
                url = file_chat.read()
            return True, url
        else:
            # Crear chat
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div/div/nav/div[1]/a')))
            button.click()

            # Escribir algo para que genera la url
            self.send_msg("hola")
            
            # Sacar url
            url = str(self.driver.current_url)

            # Escribir en el archivo la url
            with open("./url_chat.config", "w") as file_chat:
                file_chat.write(url)
            return False, url