from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsDropShadowEffect #Clase para la ventana, para iniciar la aplicacion y para dar efecto sombra
from PyQt5.uic import loadUi #Cargar el archivo de diseño
from PyQt5.QtCore import QPoint, Qt, QByteArray, QIODevice, QBuffer #Las ultimas tres clases es para convertir la imagen para poderla almacenar en la base de datos
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog #Para abrir la ventana y para importar las imagenes
from PyQt5.QtGui import QImage, QPixmap, QColor, QIntValidator #para validar la entrada de solo entrada de numeros en este caso para el telefono
import sqlite3
import sys #Para ejecutar la ventana

class Formulario(QMainWindow): #Creamos la clase formulario y heredamos la clase principal de la ventana
    #CREAMOS EL CONSTRUCTOR
    def __init__(self): 
        super(Formulario, self).__init__()
        loadUi('interfaz.ui', self) #Cargamos el diseño con el loadUi

        self.conexion = sqlite3.connect('base_datoss.db')

        self.bt_normal.hide() #Ocultando boton normal
        self.click_position = QPoint() #Objeto donde nos va a dar la posicion
        self.bt_minimize.clicked.connect(lambda:self.showMinimized())
        self.bt_normal.clicked.connect(self.control_bt_normal)
        self.bt_maximize.clicked.connect(self.control_bt_maximize)
        self.bt_close.clicked.connect(lambda:self.close())

        #ELIMINAR LA BARRA DE TITULO Y OPACIDAD
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)
         #Funciones para que aparezcan con un borde redondeado
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        #SizeGrip para redimensionar la ventana
        self.gripSize = 10
        self.grip = QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)
        #Mover la ventana
        self.frame_superior.mouseMoveEvent = self.mover_ventana

        #BOTONES
        self.bt_importar_img.clicked.connect(self.load_image)#Para que nos lea la imagen en el guion 57
        self.bt_limpiar.clicked.connect(self.clear_data)#Para eliminar los datos que hemos ingresado en el guion 64
        self.bt_guardar.clicked.connect(self.save_data)#Para guardar los datos que hemos ingresado en el guion 70
        self.bt_buscar.clicked.connect(self.search_data)#Para buscar en el guion 100

        self.shadow_frame(self.frame_datos)
        self.shadow_frame(self.frame_buscar)
        self.in_telefono.setValidator(QIntValidator()) #Validamos que en la entrada del telefono solo deje ingresar números
    
    def shadow_frame(self, frame):
          #CREAMOS LAS SOMBRAS
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setOffset(5,5)
        shadow.setColor(QColor(127, 90, 240, 255))
        frame.setGraphicsEffect(shadow)

    def load_image(self):
        filename = QFileDialog.getOpenFileName(
            filter="Image JPG(*.jpg);;Image PNG(*.png)")[0]
        if filename:  #Si nos retorna una direccion
            pixmapImagen = QPixmap(filename).scaled(200,200,Qt.KeepAspectRatio,Qt.SmoothTransformation)#Tamaño de img 200x200
            self.img_preview.setPixmap(pixmapImagen) #Para colocar la imagen como vista previa

    def clear_data(self): #Metodo para eliminar los datos
        self.in_nombre.clear()
        self.in_telefono.clear()
        self.in_correo.clear()
        self.img_preview.clear()

    def save_data(self):#Obtenemos todos los datos
        nombre = self.in_nombre.text()
        telefono = self.in_telefono.text()
        correo = self.in_correo.text()
        foto = self.img_preview.pixmap()
        #Convertir QPixmap a bytes
        if foto: #Si hemos creado la foto
            bArray = QByteArray()
            buff = QBuffer(bArray)
            buff.open(QIODevice.WriteOnly)
            foto.save(buff, "PNG")

        cursor = self.conexion.cursor() #Verificar con la base de datos
        if cursor.execute("SELECT * FROM datos WHERE NOMBRE = ?", (nombre,)).fetchone():
            self.img_preview.setText('El usuario ya existe')
        elif len(nombre) <= 4:
            self.img_preview.setText('No hay nombre')
        elif len(correo) <= 5:
            self.img_preview.setText('No hay correo')
        elif len(telefono) <= 3:
            self.img_preview.setText('No hay telefono')
        elif foto:
            #Guardar en SQLite3
            cursor.execute("INSERT INTO datos VALUES (?,?,?,?)",(nombre, telefono, correo, bArray))
            self.conexion.commit()
            cursor.close()
            self.clear_data()
        else:
            self.img_preview.setText('No hay foto')
    
    def search_data(self):
        nombre_a_buscar = self.in_buscar_nombre.text() #Almacenamos lo que ingresamos en este campo
        #Obtener datos de SQLite3
        cursor = self.conexion.cursor()  #Para la base de datos
        cursor.execute("SELECT * FROM datos WHERE NOMBRE = '{}' ".format(nombre_a_buscar))
        nombrex = cursor.fetchall()
        cursor.close()
        if nombrex:
            self.telefono.setText(f'Telefono: {nombrex[0][1]}')
            self.correo.setText(f'Correo: {nombrex[0][2]}')
            foto = QPixmap()
            foto.loadFromData(nombrex[0][3], "PNG", Qt.AutoColor) #Cargamos la foto de la base de datos
            self.imagen.setPixmap(foto)
        else:
            self.telefono.setText('Telefono: None')
            self.correo.setText('Correo: None')
            self.imagen.clear()

    ################################################################
    def control_bt_normal(self):
        self.showNormal()
        self.bt_normal.hide()
        self.bt_maximize.show()

    def control_bt_maximize(self):
        self.showMaximized()
        self.bt_maximize.hide()
        self.bt_normal.show()
    
    ## SizeGrip : Para redimencionar
    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)
    ## Mover ventana
    def mousePressEvent(self, event):
        self.click_posicion = event.globalPos()
    
    def mover_ventana(self, event):
        if self.isMaximized() == False:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.click_posicion)
                self.click_posicion = event.globalPos()
                event.accept()
        if event.globalPos().y() <=5 or event.globalPos().x():
            self.showMaximized()
            self.bt_maximize.hide()
            self.bt_normal.show()
        else:
            self.showNormal()
            self.bt_normal.hide()
            self.bt_maximize.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_app = Formulario()
    my_app.show()
    sys.exit(app.exec_())