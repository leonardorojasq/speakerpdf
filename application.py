import datetime
import os
from flask import Flask, jsonify, request
from dotenv import dotenv_values
from flask_cors import CORS 
from config.conex import get_conexion_pdf_cursor
from werkzeug.security import generate_password_hash, check_password_hash
import pyttsx3
import pdfplumber as pp
from werkzeug.utils import secure_filename


application = Flask(__name__)
CORS(application, resources={r"/api/*": {"origins":"*"}})

db = get_conexion_pdf_cursor()


@application.route('/', methods=['GET'])
def root():
    
    return "Esto es la raiz de speaker"

@application.route("/api/usuarios", methods=['GET'])
def listar_usuarios():
    with db.cursor() as conn:
        conn.execute("SELECT * FROM usuarios")
        listar = conn.fetchall() 
        return jsonify({"message":listar})
   
      
@application.route("/api/usuario/<user_id>", methods=['GET'])
def obtener_usuario(user_id: int):
    with db.cursor() as conn:
        conn.execute(f"SELECT Username FROM usuarios WHERE id={user_id}")
        listar = conn.fetchone()
        
        return jsonify({"message":listar})


@application.route("/api/usuario", methods=['POST'])
def crear_usuario():
    with db.cursor() as conn:    
        username = request.json['Username']
        password = request.json['Password']
        area = request.json['Area']
        passw = generate_password_hash( password, "pbkdf2:sha256:30", 30)
        print(passw)
 
        conn.execute("INSERT INTO usuarios( Username, Password, Area) VALUES(%s,%s,%s)",(username,passw,area))
        db.commit()
        return jsonify({"message":"usuario creado"})
    
        
@application.route("/api/usuario/login", methods=['POST'])
def verificar_login():
    with db.cursor() as conn:
        username = request.json['Username']
        password = request.json['Password']
        conn.execute("SELECT Username, Password FROM usuarios WHERE Username = %s",username)
        result = conn.fetchone()
        
        print(result)
        if result != None:
            check_pass = check_password_hash(result['Password'],password)
            print(check_pass)
            if check_pass:
                
                return {
                    "status": 200,
                    "message": "Acceso exitoso"
                }          
                 
        return jsonify({"message": "Acceso denegado"})
        

@application.route("/api/usuario/<user_id>", methods=['PUT'])
def actualizar_usuario(user_id: int):
    with db.cursor() as conn:
        name = request.json['Username']
        password = request.json['Password']
        area = request.json['Area']
        
        encrypt_passw = generate_password_hash(password, "pbkdf2:sha256:30", 30)
        
        conn.execute(f"UPDATE usuarios SET Username='{name}', Password='{encrypt_passw}', Area='{area}' WHERE id={user_id}")
        db.commit()
        conn.execute(f"SELECT * FROM usuarios WHERE id={user_id}")
        result = conn.fetchone()
        return jsonify({"Actualización exitosa": result})
    
    
@application.route("/api/usuario/<user_id>", methods=['DELETE'])
def deliminar_usuario(user_id: int):
    with db.cursor() as conn:
        conn.execute(f"DELETE FROM usuarios WHERE id={user_id}")
        db.commit()
        return jsonify({"message": "Eliminacion exitosa"})
    
 
@application.route("/api/crear_mp3", methods=['POST'])
def ejecutar_aplicacion():
    pdf_iniciar = pyttsx3.init() #inicializo la libreria
    voice_id = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\TTS_MS_ES_MX_SABINA_11.0'
    pdf_iniciar.setProperty('voice', voice_id) #ESTABLECER EN MI MOTOR LA VOZ DE SABINA
    all_book = ''
    archivo = request.files['archivo']

    nombre_archivo = secure_filename(archivo.filename)
    archivo.save(os.path.join(os.getcwd(), nombre_archivo))

    with pp.open(f'./{nombre_archivo}') as book:
        for page_no, page in enumerate(book.pages, start = 1):
            data = page.extract_text()
            all_book += data
    # definir all_book
    pdf = nombre_archivo.replace('.pdf','')
    pdf_iniciar.save_to_file(all_book, f'./books/{pdf}.mp3')
      
    # #Inicializar
    pdf_iniciar.runAndWait()
    pdf_iniciar.stop()

    # ruta_books = os.listdir('./books')
    # for elemento in  ruta_books:
    #     if elemento.find(f'{nombre_archivo}.mp3') != -1:
    #         print(os.path.join(os.path.dirname(elemento)))
    with db.cursor() as conn:
        print(os.path.join(os.getcwd(), "books", f"{pdf}.mp3"))
        conn.execute(f"""INSERT INTO archivos(nombre, url, fecha)
                     VALUES( '{pdf}' , '{"/books" + f"/{pdf}.mp3"}', '{datetime.datetime.today()}' )""")
        db.commit()
        os.remove(f'./{nombre_archivo}')
        
        return {"status": 200,"message": "Acceso exitoso" }

# ################################### AUDIOS #############################################################

@application.route('/api/listar_audios', methods=['GET'])
def listar_audios():
    with db.cursor() as conn:
        conn.execute("SELECT * FROM archivos")
        listar = conn.fetchall()
        
        return listar


@application.route('/api/eliminar_audio/<audios_id>', methods=['DELETE'])
def eliminar_audio(audios_id: int):
    with db.cursor() as conn:
        conn.execute(f"DELETE FROM archivos WHERE id={audios_id}")
        db.commit()
        
        conn.execute("SELECT * FROM archivos")
        
        listar = conn.fetchall()
        
        return jsonify({"Audio eliminado": listar})


if __name__ == '__main__':
    config = dotenv_values("./config/.env.prod")
    application.debug = config['DEBUG']
    application.run()